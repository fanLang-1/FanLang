@echo off
cd /d "C:\Users\Administrator\ebook-rag"
title WolfPack RAG - Main Menu
echo ============================================================
echo              🐺 狼群 RAG · 主菜单
echo ============================================================
echo.
echo  [1] 🚀 RAG 电子书问答    (port 8501)
echo  [2] 🦯 AI 脚手架          (port 8502)
echo  [3] 📖 中文 AI 语言体系   (port 8503)
echo.
echo  ===========================================================
echo  [4] 📚 索引电子书
echo  [5] 📊 查看向量库状态
echo.
echo  [Q] 退出
echo  ===========================================================
echo.

:menu
set /p choice="请输入编号 (1-5, Q): "
if "%choice%"=="1" goto start_rag
if "%choice%"=="2" goto start_scaffold
if "%choice%"=="3" goto start_symbol
if /i "%choice%"=="4" goto index
if /i "%choice%"=="5" goto stats
if /i "%choice%"=="Q" goto end
echo 输入无效，请重试
goto menu

:start_rag
start http://localhost:8501
"venv\Scripts\streamlit.exe" run app/ui.py --server.port 8501
goto end

:start_scaffold
start http://localhost:8502
"venv\Scripts\streamlit.exe" run app/scaffold.py --server.port 8502
goto end

:start_symbol
start http://localhost:8503
"venv\Scripts\streamlit.exe" run app/symbol_browser.py --server.port 8503
goto end

:index
"venv\Scripts\python.exe" index_all.py
pause
goto menu

:stats
"venv\Scripts\python.exe" -c "import sys; sys.path.insert(0,'.'); from app.indexer import get_stats; s=get_stats(); print(f'Vector DB: {s[\"doc_chunks\"]} chunks'); print(f'Indexed: {s[\"indexed_files\"]} files')"
pause
goto menu

:end
