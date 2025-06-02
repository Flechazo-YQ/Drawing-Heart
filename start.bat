@echo off
echo 正在启动画心系统...

:: 启动后端服务
start cmd /k "cd huixin-vue-back && python main.py"

:: 等待后端服务启动
timeout /t 3

:: 启动前端服务
start cmd /k "cd huixin-vue-front && npm run dev"

:: 等待前端服务启动
timeout /t 3

:: 打开浏览器访问前端页面
start http://localhost:5173

echo 服务已启动完成！ 