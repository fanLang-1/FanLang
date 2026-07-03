@echo off
cd /d "C:\Users\Administrator\ebook-rag"
title Chinese AI Language - Symbol Browser
echo =============================================
echo   Chinese AI Language System
echo   Browser: http://localhost:8503
echo =============================================
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    start /b ollama serve
    timeout /t 3 /nobreak >nul
)
start http://localhost:8503
"venv\Scripts\streamlit.exe" run app/symbol_browser.py --server.port 8503
pause
