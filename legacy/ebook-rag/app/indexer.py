"""
📚 电子书索引器 - 提取文本 → 分块 → 向量化 → 入库
"""

import os
import json
import hashlib
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import (
    VECTOR_DB_DIR, INDEX_RECORD, EXTRACTED_DIR,
    EMBED_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
    DATA_DIR, SUPPORTED_EXTS
)
from app.processors import extract_text

# 全局 ChromaDB 客户端
_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    _client = chromadb.PersistentClient(
        path=VECTOR_DB_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    _collection = _client.get_or_create_collection(
        name="ebook_rag",
        metadata={"hnsw:space": "cosine"}
    )
    return _collection

def _get_file_hash(filepath):
    """快速计算文件 hash（只读前 1MB）"""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        h.update(f.read(1024 * 1024))
    return h.hexdigest()

def load_index_record():
    if not os.path.exists(INDEX_RECORD):
        return {}
    with open(INDEX_RECORD, "r", encoding="utf-8") as f:
        return json.load(f)

def save_index_record(record):
    with open(INDEX_RECORD, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

def find_ebooks():
    """扫描 DATA_DIR 下所有支持的电子书文件"""
    ebooks = []
    for root, dirs, files in os.walk(DATA_DIR):
        # 跳过目录名含特殊字符的
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('$')]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in SUPPORTED_EXTS:
                ebooks.append(os.path.join(root, f))
    return ebooks

def index_ebooks(filepaths=None, on_progress=None):
    """
    索引电子书到向量数据库
    - filepaths: 指定文件列表，None=扫描全部
    - on_progress: 进度回调 (current, total, filename)
    """
    collection = get_collection()
    index_record = load_index_record()

    if filepaths is None:
        filepaths = find_ebooks()

    total = len(filepaths)
    new_count = 0

    for i, fp in enumerate(filepaths):
        fname = os.path.basename(fp)
        rel_path = os.path.relpath(fp, DATA_DIR)

        # 进度回调
        if on_progress:
            on_progress(i + 1, total, rel_path)

        # 检查是否已索引且未变更
        file_hash = _get_file_hash(fp)
        if rel_path in index_record and index_record[rel_path] == file_hash:
            continue

        # 提取文本
        text = extract_text(fp)
        if not text:
            continue

        # 分块
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
        )
        chunks = splitter.split_text(text)

        # 生成唯一 ID（基于文件路径 + 块索引）
        doc_id_base = hashlib.md5(rel_path.encode()).hexdigest()[:12]
        ids = [f"{doc_id_base}_{j}" for j in range(len(chunks))]
        metadatas = [{"source": rel_path, "chunk": j, "file": fname} for j in range(len(chunks))]

        # 批量入库（每次 100 条）
        batch_size = 100
        for start in range(0, len(chunks), batch_size):
            end = min(start + batch_size, len(chunks))
            collection.upsert(
                ids=ids[start:end],
                documents=chunks[start:end],
                metadatas=metadatas[start:end],
            )

        # 记录已索引
        index_record[rel_path] = file_hash
        new_count += 1

    save_index_record(index_record)
    return new_count, total

def get_stats():
    """获取向量库统计"""
    collection = get_collection()
    count = collection.count()
    return {
        "doc_chunks": count,
        "indexed_files": len(load_index_record()),
    }
