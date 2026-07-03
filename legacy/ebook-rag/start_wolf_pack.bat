@echo off
cd /d "C:\Users\Administrator\ebook-rag"
title WolfPack RAG - Local Ebook Assistant

echo =============================================
echo        WolfPack RAG - Local Assistant
echo =============================================
echo.

:: Check if Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Ollama not running, starting...
    start /b ollama serve
    timeout /t 3 /nobreak >nul
)

:: Show models
echo [WolfPack Models]:
ollama list 2>nul | findstr /v "NAME"
echo.

:: Launch Web UI
echo [LAUNCH] Opening browser to http://localhost:8501
echo [STOP]   Close this window to stop the server
echo.
start http://localhost:8501
"venv\Scripts\streamlit.exe" run app/ui.py --server.port 8501

pause
