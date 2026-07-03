#!/bin/bash
echo "============================================"
echo "   开始安装 ..."
echo "============================================"
echo ""

echo "[1/3] 安装 Python 依赖..."
pip3 install streamlit -q
echo "✅ Python 依赖安装完成"
echo ""

echo "[2/3] 检查 Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  未检测到 Ollama，正在安装..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ollama
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
fi
echo "✅ Ollama 已安装"
echo ""

echo "[3/3] 拉取推荐模型（约 1GB，可能需要几分钟）..."
ollama pull qwen2.5:1.5b

echo ""
echo "============================================"
echo "✅ 安装完成！"
echo "运行 ./start.sh 启动"
echo "============================================"
