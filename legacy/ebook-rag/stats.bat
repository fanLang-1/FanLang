@echo off
cd /d "C:\Users\Administrator\ebook-rag"
"venv\Scripts\python.exe" -c "import sys; sys.path.insert(0,'.'); from app.indexer import get_stats; s=get_stats(); print(f'Vector DB: {s[\"doc_chunks\"]} chunks'); print(f'Indexed: {s[\"indexed_files\"]} files')"
echo.
pause
