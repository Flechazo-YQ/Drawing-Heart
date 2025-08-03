@echo off
chcp 65001>nul
cd /d %~dp0
echo ====================================
echo        正在启动系统...
echo ==================================== 

:: 检查 Python 是否安装
echo [检查] Python 环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请安装 Python 3.8 或更高版本！
    pause
    exit
)

:: 检查 Node.js 是否安装
echo [检查] Node.js 环境...
node --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请安装 Node.js！
    pause
    exit
)

:: 检查 MongoDB 数据目录
if not exist "huixin-python-back\data\db" (
    echo [配置] 创建 MongoDB 数据目录...
    mkdir "huixin-python-back\data\db"
)

:: 检查并安装缺失的 Python 依赖
echo [检查] Python 依赖包...
cd huixin-python-back
pip list > installed_packages.txt
for /f "tokens=1,2 delims==" %%a in (requirements.txt) do (
    findstr /i /c:"%%a" installed_packages.txt > nul
    if errorlevel 1 (
        echo [安装] 依赖包: %%a
        pip install "%%a==%%b"
        if errorlevel 1 (
            echo [错误] 依赖包 %%a 安装失败！
            del installed_packages.txt
            pause
            exit
        )
    )
)
del installed_packages.txt
cd ..

:: 检查并安装 Node.js 依赖
echo [信息] 检查 Node.js 依赖...
cd huixin-vue-front
if not exist "node_modules" (
    echo [信息] 安装前端依赖...
    call npm install
    if errorlevel 1 (
        echo [错误] Node.js 依赖安装失败
        pause
        exit
    )
)
cd ..

:: 启动 MongoDB
echo [信息] 正在启动 MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [信息] MongoDB 已经在运行
) else (
    echo [信息] 启动 MongoDB 服务器...
    start "MongoDB" /B cmd /c "mongod --dbpath huixin-python-back\data\db"
    timeout /t 5
)

:: 启动后端服务
echo [信息] 正在启动后端服务...
start "Backend" cmd /k "cd huixin-python-back && python main.py"
timeout /t 5

:: 启动前端服务
echo [信息] 正在启动前端服务...
start "Frontend" cmd /k "cd huixin-vue-front && npm run dev"
timeout /t 3

echo ====================================
echo          服务启动成功！
echo ====================================
echo  MongoDB:  mongodb://localhost:27017
echo  后端API:  http://localhost:5000
echo  前端页面: http://localhost:5173
echo ====================================
echo.
echo 提示：按任意键关闭此窗口，服务将在后台继续运行
pause > nul