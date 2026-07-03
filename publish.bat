@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 运行发布脚本
python publish.py %*
pause
