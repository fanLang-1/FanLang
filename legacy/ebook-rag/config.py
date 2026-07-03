"""
📋 狼群 RAG 全局配置
===========================
可以不用，不能没有。一次性配好，永不再折腾。
"""

import os
import json

# ============================================================
# 项目路径
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = r"E:\其它\BaiduNetdiskDownload"
VECTOR_DB_DIR = os.path.join(BASE_DIR, "chroma_db")
EXTRACTED_DIR = os.path.join(BASE_DIR, "extracted")
INDEX_RECORD = os.path.join(BASE_DIR, "indexed_files.json")

# ============================================================
# 🐺 狼群模型配置
# ============================================================
OLLAMA_HOST = "http://localhost:11434"

# 斥候 - 文本向量化（常驻，极小）
EMBED_MODEL = "shaw/dmeta-embedding-zh"

# 猎手 - 主力问答（常驻）
MAIN_MODEL = "qwen2.5:1.5b"

# 智囊 - 深度推理（按需加载）
REASON_MODEL = "deepseek-r1:1.5b"

# 哨兵 - 图文理解（按需加载）
VISION_MODEL = "minicpm-v4.6:1b"

# 狼群成员清单
WOLF_PACK = {
    "斥候": {"model": EMBED_MODEL, "desc": "文本向量化", "size": "408MB", "auto": True},
    "猎手": {"model": MAIN_MODEL, "desc": "主力问答·通义千问", "size": "986MB", "auto": True},
    "智囊": {"model": REASON_MODEL, "desc": "深度推理·DeepSeek", "size": "1.1GB", "auto": False},
    "哨兵": {"model": VISION_MODEL, "desc": "图文理解·MiniCPM", "size": "1.6GB", "auto": False},
}

# ============================================================
# 分块参数
# ============================================================
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
TOP_K = 5

# ============================================================
# 支持的格式
# ============================================================
SUPPORTED_EXTS = {".txt", ".md", ".epub", ".pdf", ".html", ".htm", ".docx"}

# ============================================================
# 自动创建目录
# ============================================================
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(EXTRACTED_DIR, exist_ok=True)
