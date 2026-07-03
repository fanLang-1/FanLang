"""
🦯 AI 脚手架 - 基于中文符号的大众 AI 工具
============================================
12 个大按钮，每个对应一个中文符号。
点一下切换模式，然后直接聊天。
不用学任何英文术语。
"""

import streamlit as st
from app.ai_symbols import ALL_SYMBOLS, CORE_SYMBOLS, TOOL_SYMBOLS
from app.rag import search, ask_with_model
from config import MAIN_MODEL

st.set_page_config(
    page_title="🦯 AI 脚手架 · 中文符号",
    page_icon="🦯",
    layout="centered",
)

# ============================================================
# 初始化状态
# ============================================================
if "active_symbol" not in st.session_state:
    st.session_state.active_symbol = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "chat"  # chat | raq

# ============================================================
# 头部
# ============================================================
st.title("🦯 AI 脚手架")
st.caption("选一个符号，开始对话。每个符号代表一种 AI 能力。")

# 模式切换
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("💬 聊天模式", use_container_width=True,
                 type="primary" if st.session_state.mode == "chat" else "secondary"):
        st.session_state.mode = "chat"
        st.session_state.messages = []
        st.session_state.active_symbol = None
        st.rerun()
with col2:
    if st.button("📚 查书模式（RAG）", use_container_width=True,
                 type="primary" if st.session_state.mode == "raq" else "secondary"):
        st.session_state.mode = "raq"
        st.session_state.messages = []
        st.session_state.active_symbol = None
        st.rerun()

st.divider()

# ============================================================
# 符号按钮区
# ============================================================

# 核心符号
st.subheader("🐉 核心符号")
cols = st.columns(7)
for i, sym in enumerate(CORE_SYMBOLS):
    with cols[i]:
        btn_type = "primary" if (st.session_state.active_symbol == sym.char and st.session_state.mode == "chat") else "secondary"
        if st.button(f"{sym.emoji} {sym.char}", use_container_width=True, type=btn_type,
                     help=sym.desc):
            st.session_state.active_symbol = sym.char
            st.session_state.messages = []
            st.session_state.mode = "chat"
            st.rerun()

# 工具符号
st.subheader("🛠️ 工具符号")
cols = st.columns(5)
for i, sym in enumerate(TOOL_SYMBOLS):
    with cols[i]:
        btn_type = "primary" if (st.session_state.active_symbol == sym.char and st.session_state.mode == "chat") else "secondary"
        if st.button(f"{sym.emoji} {sym.char}", use_container_width=True, type=btn_type,
                     help=sym.desc):
            st.session_state.active_symbol = sym.char
            st.session_state.messages = []
            st.session_state.mode = "chat"
            st.rerun()

# ============================================================
# 当前模式/符号提示
# ============================================================
if st.session_state.mode == "chat" and st.session_state.active_symbol:
    sym = next((s for s in ALL_SYMBOLS if s.char == st.session_state.active_symbol), None)
    if sym:
        st.info(f"📌 当前模式：**{sym.emoji} {sym.char}** — {sym.desc}")
        st.caption(f"💡 试试说：{sym.example}")
elif st.session_state.mode == "raq":
    st.info("📚 查书模式 — 从你的电子书库里检索答案")

st.divider()

# ============================================================
# 聊天区域
# ============================================================

# 显示历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入框
if prompt := st.chat_input("在这里输入..."):
    # 追加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 生成回答
    with st.chat_message("assistant"):
        with st.spinner("🤔 想着呢..."):
            if st.session_state.mode == "chat" and st.session_state.active_symbol:
                # 符号模式：按符号的 prompt 模板生成
                sym = next((s for s in ALL_SYMBOLS if s.char == st.session_state.active_symbol), None)
                if sym:
                    system_prompt = sym.prompt_template
                    answer = ask_with_model(prompt, MAIN_MODEL, [], system_prompt)
                else:
                    answer = ask_with_model(prompt, MAIN_MODEL, [])
            elif st.session_state.mode == "raq":
                # RAG 查书模式
                from app.rag import ask
                answer, chunks = ask(prompt)
                # 显示来源
                if chunks:
                    with st.expander("📖 参考来源"):
                        for s in chunks:
                            st.caption(f"**{s['source']}** · 相似度 {1-s['score']:.2%}")
                            st.text(s['text'][:150] + ("..." if len(s['text']) > 150 else ""))
            else:
                # 默认自由聊天
                answer = ask_with_model(prompt, MAIN_MODEL, [])

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

# ============================================================
# 底部：符号表
# ============================================================
st.divider()
with st.expander("📖 完整符号表 — 一看就懂"):
    for i, sym in enumerate(ALL_SYMBOLS):
        label = "🐉 核心" if i < len(CORE_SYMBOLS) else "🛠️ 工具"
        st.markdown(f"**{sym.emoji} `{sym.char}`** — {sym.desc}")
        st.caption(f"💡 {sym.example}")
        if i < len(ALL_SYMBOLS) - 1:
            st.divider()
