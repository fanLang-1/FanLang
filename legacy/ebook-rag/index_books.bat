@echo off
cd /d "C:\Users\Administrator\ebook-rag"
title WolfPack RAG - Index Books
echo =============================================
echo   Indexing all ebooks...
echo   First run may take a while
echo =============================================
"venv\Scripts\python.exe" index_all.py
echo.
echo Done! Press any key to exit...
pause >nul
