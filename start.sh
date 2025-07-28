#!/bin/bash
# filepath: start.sh
#
# ==============================================================================
#  高效、健壮的应用部署与管理脚本 (v2) - 修正版
# ==============================================================================

set -e
set -o pipefail

# --- 目录定义 ---
# 根据实际项目结构修改目录路径
BACKEND_DIR="huixin-vue-back"  # 后端代码在当前目录
FRONTEND_DIR="huixin-vue-front"  # 假设前端在这个目录，如果不对请修改

# --- 日志函数 ---
log_info() {
    echo -e "\n[INFO] $1"
}

log_success() {
    echo -e "[SUCCESS] $1"
}

log_error() {
    echo -e "[ERROR] $1" >&2
    exit 1
}

# --- 功能函数 ---

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "命令 '$1' 未找到，请先安装它！"
    fi
}

install_dependencies() {
    log_info "检查环境..."
    check_command "python3"
    check_command "node"
    check_command "npm"

    log_info "安装 Python 依赖..."
    ( 
        cd "$BACKEND_DIR"
        # 检查是否有 requirements.txt
        if [ -f "requirements.txt" ]; then
            pip3 install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
            pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
        else
            log_info "未找到 requirements.txt，尝试安装必需的依赖..."
            # 根据 main.py 中的导入，安装基本依赖
            pip3 install flask flask-cors flask-socketio python-socketio pymongo jwt requests torchvision reportlab openai httpx -i https://mirrors.aliyun.com/pypi/simple/
        fi
    )

    log_info "安装 Node.js 依赖..."
    if [ -d "$FRONTEND_DIR" ]; then
        (
            cd "$FRONTEND_DIR"
            npm config set registry https://registry.npmmirror.com
            if [ ! -d "node_modules" ]; then
                npm install
            else
                log_info "Node.js 依赖已存在，跳过安装。"
            fi
        )
    else
        log_info "前端目录 '$FRONTEND_DIR' 不存在，跳过前端依赖安装。"
    fi
}

start_mongodb() {
    log_info "启动 MongoDB 服务..."
    if command -v docker &> /dev/null; then
        log_info "检测到 Docker，将使用 Docker 启动 MongoDB..."
        if sudo docker ps --format '{{.Names}}' | grep -q "^mongodb$"; then
            log_success "MongoDB 容器已在运行。"
            return
        fi
        if sudo docker ps -a --format '{{.Names}}' | grep -q "^mongodb$"; then
            log_info "MongoDB 容器已存在但已停止，正在启动..."
            sudo docker start mongodb
        else
            log_info "创建并启动新的 MongoDB 容器..."
            # 修正数据目录路径
            mkdir -p "$(pwd)/data/db"
            sudo docker run -d --name mongodb -p 27017:27017 -v "$(pwd)/data/db:/data/db" --restart unless-stopped mongo:7.0
        fi
    else
        log_info "未检测到 Docker，将尝试使用本地 mongod 启动..."
        if [ ! -d "data/db" ]; then
            log_info "创建 MongoDB 数据目录..."
            mkdir -p "data/db"
        fi
        if pgrep -f "mongod.*data/db" > /dev/null; then
            log_success "本地 mongod 服务已在运行。"
            return
        fi
        nohup mongod --dbpath "$(pwd)/data/db" --port 27017 > mongodb.log 2>&1 &
    fi
    log_info "等待 MongoDB 初始化..."
    sleep 8
}

start_services() {
    log_info "安装或检查 PM2..."
    if ! command -v pm2 &> /dev/null; then
        npm install -g pm2 --registry=https://registry.npmmirror.com
    fi
    
    log_info "使用 PM2 启动后端服务..."
    (
        cd "$BACKEND_DIR"
        # 停止现有的后端服务（如果存在）
        pm2 delete backend 2>/dev/null || true
        # 启动新的后端服务
        pm2 start main.py --name "backend" --interpreter python3
    )

    log_info "使用 PM2 启动前端服务..."
    if [ -d "$FRONTEND_DIR" ]; then
        (
            cd "$FRONTEND_DIR"
            # 停止现有的前端服务（如果存在）
            pm2 delete frontend 2>/dev/null || true
            # 启动新的前端服务
            pm2 start "npm run dev" --name "frontend"
        )
    else
        log_info "前端目录不存在，跳过前端服务启动。"
    fi
}

health_check() {
    log_info "执行服务健康检查..."
    local backend_ok=false
    local frontend_ok=false

    # 增加等待时间，因为 Flask 应用可能需要更长时间启动
    for i in {1..30}; do
        # 检查后端 API (端口 5000)
        if ! $backend_ok && curl -s --connect-timeout 3 --max-time 5 http://localhost:5000 > /dev/null 2>&1; then
            backend_ok=true
            log_success "后端服务 (端口 5000) 已响应。"
        fi

        # 检查前端服务 (端口 5173)
        if ! $frontend_ok && curl -s --connect-timeout 3 --max-time 5 http://localhost:5173 > /dev/null 2>&1; then
            frontend_ok=true
            log_success "前端服务 (端口 5173) 已响应。"
        fi

        # 如果两个都成功，则退出检查
        if $backend_ok && ($frontend_ok || [ ! -d "$FRONTEND_DIR" ]); then
            break
        fi
        
        # 每5秒显示一次状态
        if [ $((i % 5)) -eq 0 ]; then
            log_info "等待服务启动... ($i/30)"
            # 显示 PM2 日志的最后几行来帮助诊断问题
            pm2 logs backend --lines 3 --nostream 2>/dev/null || true
        fi
        
        sleep 1
    done

    # 最终检查结果
    if ! $backend_ok; then
        log_info "后端服务启动可能有问题，显示日志："
        pm2 logs backend --lines 10 --nostream
        log_error "后端服务在 30 秒内未成功启动或响应！请检查上述日志。"
    fi
    
    if [ -d "$FRONTEND_DIR" ] && ! $frontend_ok; then
        log_info "前端服务启动可能有问题，显示日志："
        pm2 logs frontend --lines 10 --nostream
        log_error "前端服务在 30 秒内未成功启动或响应！请检查上述日志。"
    fi
}

# --- 主逻辑 ---
main() {
    echo "===================================="
    echo "        正在启动系统 (v2)..."
    echo "===================================="

    install_dependencies
    start_mongodb
    start_services
    health_check

    echo "===================================="
    log_success "所有服务已成功启动并验证！"
    echo "===================================="
    echo "  MongoDB:  mongodb://localhost:27017"
    echo "  后端API:  http://localhost:5000"
    if [ -d "$FRONTEND_DIR" ]; then
        echo "  前端页面: http://localhost:5173"
    fi
    echo "===================================="
    pm2 list
    echo ""
    log_info "如果需要查看服务日志，请使用："
    echo "  pm2 logs backend  # 查看后端日志"
    if [ -d "$FRONTEND_DIR" ]; then
        echo "  pm2 logs frontend # 查看前端日志"
    fi
}

# 执行主函数
main