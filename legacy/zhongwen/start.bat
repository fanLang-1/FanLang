@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 中文 AI 语言
echo ============================================
echo   🐉 中文 AI 语言
echo   不用学英文，用中文就能用 AI
echo ============================================
echo.
echo [1/2] 检查 Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Ollama 未运行，正在启动...
    start /b ollama serve
    timeout /t 3 /nobreak >nul
)
echo ✅ Ollama 运行中
echo.
echo [2/2] 启动界面...
echo 📌 浏览器打开: http://localhost:8501
echo ❌ 关闭此窗口即可退出
echo.
start http://localhost:8501
pip install streamlit -q 2>nul
streamlit run apps/scaffold.py --server.port 8501
pause
