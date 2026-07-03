@echo off
cd /d "C:\Users\Administrator\ebook-rag"
title AI Scaffold - Chinese Symbols
echo =============================================
echo   AI Scaffold - Chinese Symbol System
echo =============================================
echo.
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Ollama not running, starting...
    start /b ollama serve
    timeout /t 3 /nobreak >nul
)
echo [LAUNCH] Browser: http://localhost:8502
start http://localhost:8502
"venv\Scripts\streamlit.exe" run app/scaffold.py --server.port 8502
pause
