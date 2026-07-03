"""
📖 中文 AI 符号浏览器
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.symbols import SINGLE_CHARS, TWO_WORDS, GRAMMAR_SYMBOLS, EN_TO_CN, translate

st.set_page_config(page_title="📖 中文 AI 符号", page_icon="📖", layout="wide")

tab1, tab2, tab3, tab4 = st.tabs(["📖 单字", "📖 双词", "🔣 语法符号", "🔤 英中翻译"])

with tab1:
    st.subheader("25 个单字")
    for c, i in SINGLE_CHARS.items():
        with st.container(border=True):
            st.markdown(f"{i['e']} **【{c}】** {i['n']}  — {i['d']}")

with tab2:
    st.subheader("31 个双词")
    cols = st.columns(5)
    for i, (w, e) in enumerate(TWO_WORDS.items()):
        with cols[i % 5]:
            st.markdown(f"{e} **{w}**")

with tab3:
    st.subheader("12 个语法符号")
    for s, n in GRAMMAR_SYMBOLS.items():
        st.markdown(f"`{s}` — {n}")

with tab4:
    st.subheader("英文 → 中文 翻译")
    for en, cn in EN_TO_CN.items():
        st.code(f"{en}  →  {cn}")
