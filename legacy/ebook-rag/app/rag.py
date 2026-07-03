"""
🐺 RAG 引擎 - 检索 + 狼群推理
"""

import requests
from config import (
    OLLAMA_HOST, EMBED_MODEL, MAIN_MODEL, REASON_MODEL,
    WOLF_PACK, TOP_K,
)
from app.indexer import get_collection

def _call_ollama(messages, model, stream=False, options=None):
    """调用 Ollama 聊天"""
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "options": options or {},
    }
    resp = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload)
    resp.raise_for_status()
    return resp.json()["message"]["content"]

def _embed(text):
    """调用 Ollama embedding"""
    resp = requests.post(f"{OLLAMA_HOST}/api/embed", json={
        "model": EMBED_MODEL,
        "input": [text],
    })
    resp.raise_for_status()
    return resp.json()["embeddings"][0]

def search(query, top_k=TOP_K):
    """向量检索"""
    collection = get_collection()
    query_emb = _embed(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=min(top_k, collection.count()),
    )
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i].get("source", ""),
            "score": results["distances"][0][i] if results["distances"] else 0,
        })
    return chunks

def ask_with_model(query, model_name, context_chunks, system_prompt=None):
    """用指定模型回答问题"""
    if not system_prompt:
        system_prompt = "你是专业的学习助手。用中文回答，基于提供的资料，简明扼要。如果资料不足以回答，请如实说。引用资料中的内容。"
    
    # 构建上下文
    context = ""
    for i, c in enumerate(context_chunks):
        context += f"[来源{i+1}: {c['source']}]\n{c['text']}\n\n"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"以下是参考资料：\n{context}\n\n请回答：{query}"},
    ]
    
    return _call_ollama(messages, model_name)

def ask(query, model=None, top_k=TOP_K):
    """
    完整 RAG 问答
    - model: None 使用默认猎手, 或 "猎手"/"智囊"/"哨兵"
    """
    if model and model in WOLF_PACK:
        model_name = WOLF_PACK[model]["model"]
    else:
        model_name = MAIN_MODEL

    # 1. 检索
    chunks = search(query, top_k)
    if not chunks:
        return "📭 向量库中没有找到相关资料，请先索引电子书。", []

    # 2. 生成回答
    answer = ask_with_model(query, model_name, chunks)
    return answer, chunks

def ask_stream(query, model=None, top_k=TOP_K):
    """流式 RAG 问答"""
    if model and model in WOLF_PACK:
        model_name = WOLF_PACK[model]["model"]
    else:
        model_name = MAIN_MODEL

    # 先检索
    chunks = search(query, top_k)
    if not chunks:
        yield "📭 向量库中没有找到相关资料，请先索引电子书。", []
        return

    # 构建上下文
    context = ""
    for i, c in enumerate(chunks):
        context += f"[来源{i+1}: {c['source']}]\n{c['text']}\n\n"

    system_prompt = "你是专业的学习助手。用中文回答，基于提供的资料，简明扼要。如果资料不足以回答，请如实说。引用资料中的内容。"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"以下是参考资料：\n{context}\n\n请回答：{query}"},
    ]

    # 流式调用
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": True,
    }
    resp = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, stream=True)
    resp.raise_for_status()

    full_answer = ""
    for line in resp.iter_lines(decode_unicode=True):
        if line:
            import json
            data = json.loads(line)
            if "message" in data and "content" in data["message"]:
                content = data["message"]["content"]
                full_answer += content
                yield content, None
            if data.get("done"):
                break

    yield full_answer, chunks
