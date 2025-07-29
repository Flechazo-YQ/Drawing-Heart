@echo off
REM 检查 frpc.exe 是否存在
IF NOT EXIST frpc.exe (
    echo frpc.exe 不存在，请下载并放在当前目录。
    pause
    exit /b
)

REM 检查 frpc.toml 是否存在
IF NOT EXIST frpc.toml (
    echo frpc.toml 配置文件不存在，请确保已放在当前目录。
    pause
    exit /b
)

REM 启动 frpc
frpc.exe -c frpc.toml

REM 如果需要后台运行可使用 start 命令
REM start frpc.exe -c frpc.toml