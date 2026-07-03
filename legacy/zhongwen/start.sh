#!/bin/bash
echo "============================================"
echo "  🐉 中文 AI 语言"
echo "  不用学英文，用中文就能用 AI"
echo "============================================"
echo ""

# 检查 Ollama
echo "[1/2] 检查 Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama 未运行，正在启动..."
    ollama serve &
    sleep 3
fi
echo "✅ Ollama 运行中"
echo ""

# 启动界面
echo "[2/2] 启动界面..."
echo "📌 浏览器打开: http://localhost:8501"
echo ""
pip install streamlit -q 2>/dev/null
streamlit run apps/scaffold.py --server.port 8501
