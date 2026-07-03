@echo off
chcp 65001 >nul
title 安装 中文 AI 语言
echo ============================================
echo   开始安装 ...
echo ============================================
echo.

echo [1/3] 安装 Python 依赖...
pip install streamlit -q
echo ✅ Python 依赖安装完成
echo.

echo [2/3] 检查 Ollama...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 未检测到 Ollama，请手动下载安装:
    echo    https://ollama.com/download/windows
) else (
    echo ✅ Ollama 已安装
    echo.
    echo [3/3] 拉取推荐模型（约 1GB，可能需要几分钟）...
    ollama pull qwen2.5:1.5b
)
echo.
echo ============================================
echo ✅ 安装完成！
echo 双击 start.bat 启动
echo ============================================
pause
