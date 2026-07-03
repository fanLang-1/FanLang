"""
🎨 狼群 RAG - Streamlit Web 界面
"""

import streamlit as st
import time
import os
from config import WOLF_PACK, MAIN_MODEL, DATA_DIR
from app.indexer import index_ebooks, get_stats
from app.rag import search, ask

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="🐺 狼群 RAG · 电子书学习助手",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.title("🐺 狼群 RAG")
    st.caption("本地电子书 · 智能问答")

    # --- 狼群状态 ---
    st.subheader("📡 狼群阵容")
    for name, info in WOLF_PACK.items():
        emoji = "🟢" if info["auto"] else "🟡"
        auto_label = "常驻" if info["auto"] else "按需"
        st.caption(f"{emoji} **{name}** · {info['desc']} · {info['size']} · {auto_label}")

    st.divider()

    # --- 模型选择 ---
    st.subheader("🎯 当前猎手")
    model_options = {"猎手 (qwen2.5:1.5b)": "猎手", "智囊 (deepseek-r1:1.5b)": "智囊"}
    selected_model = st.radio(
        "选择问答模型：",
        list(model_options.keys()),
        index=0,
        help="猎手：常规问答（快速） ｜ 智囊：深度推理（较慢但更深入）",
    )
    active_wolf = model_options[selected_model]

    # --- 检索参数 ---
    top_k = st.slider("检索块数", min_value=1, max_value=15, value=5, help="检索的相关文本块数，越多信息越全但越慢")

    st.divider()

    # --- 向量库统计 ---
    stats = get_stats()
    st.metric("📊 向量库", f"{stats['doc_chunks']} 文本块")
    st.metric("📚 已索引文件", f"{stats['indexed_files']} 个")

    st.divider()

    # --- 索引管理 ---
    st.subheader("📥 索引管理")
    if st.button("🔍 扫描并索引新书", use_container_width=True, type="primary"):
        with st.spinner("正在扫描电子书..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            def on_progress(current, total, fname):
                progress_bar.progress(current / total)
                status_text.text(f"[{current}/{total}] {fname}")

            new_count, total = index_ebooks(on_progress=on_progress)
            if new_count > 0:
                st.success(f"✅ 新增索引 {new_count} 个文件（共扫描 {total} 个）")
            else:
                st.info(f"📭 无新文件（共 {total} 个，均已索引）")
            time.sleep(1)
            st.rerun()

    if st.button("🔄 全量重建索引", use_container_width=True):
        import json
        from config import INDEX_RECORD
        if os.path.exists(INDEX_RECORD):
            os.remove(INDEX_RECORD)
        from app.indexer import get_collection
        import chromadb
        try:
            get_collection().delete(where={})
        except:
            pass
        st.warning("索引已清空，请点击「扫描并索引新书」重建")

    st.divider()
    st.caption(f"📁 数据源: `{DATA_DIR}`")
    st.caption("Powered by Ollama + ChromaDB + LangChain")

# ============================================================
# 主界面
# ============================================================
st.title("📚 电子书 RAG 智能问答")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = []

# 显示聊天历史
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and i < len(st.session_state.sources):
            src = st.session_state.sources[i]
            if src:
                with st.expander("📖 查看参考来源"):
                    for s in src:
                        st.caption(f"**{s['source']}** (相似度: {1-s['score']:.2%})")
                        st.text(s['text'][:200] + ("..." if len(s['text']) > 200 else ""))

# 输入框
if query := st.chat_input("输入你的问题..."):
    # 追加用户消息
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 生成回答
    with st.chat_message("assistant"):
        with st.spinner(f"🐺 {active_wolf} 正在思考..."):
            answer, chunks = ask(query, model=active_wolf, top_k=top_k)
        
        st.markdown(answer)
        
        # 显示来源
        if chunks:
            with st.expander("📖 查看参考来源"):
                for s in chunks:
                    st.caption(f"**{s['source']}** (相似度: {1-s['score']:.2%})")
                    st.text(s['text'][:200] + ("..." i
