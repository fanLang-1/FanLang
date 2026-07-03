"""
📖 中文 AI 语言浏览器 —— 查看完整符号体系
"""

import streamlit as st
from app.chinese_ai_lang import (
    SINGLE_CHARS, TWO_WORDS, GRAMMAR_SYMBOLS,
    AGENT_PRIMITIVES, EN_TO_CN, render_symbol_system,
    EXAMPLE_PROMPTS,
)
from app.prompt_demo import EXAMPLES as PROMPT_EXAMPLES
from app.agent_demo import AGENT_TEMPLATES

st.set_page_config(page_title="📖 中文 AI 语言", page_icon="📖", layout="wide")

st.title("🐉 中文 AI 语言 · 完整体系")
st.caption("三层结构：18个单字 + 36个双词 + 12个语法符号 | 纯中文原生，不用英文术语")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 单字", "📖 双词", "🔣 语法符号", "📝 提示词示例", "🤖 智能体模板"
])

# ============================================================
# Tab 1: 单字
# ============================================================
with tab1:
    st.subheader("第一层 · 单字（18 个核心动词）")
    st.caption("每个字对应一个 AI 核心能力，小学三年级就能认")
    
    cols = st.columns(3)
    for i, (char, info) in enumerate(SINGLE_CHARS.items()):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {info['emoji']} 【{char}】{info['name']}")
                st.caption(f"📌 {info['desc']}")
                st.caption(f"💡 {info['举例']}")

# ============================================================
# Tab 2: 双词
# ============================================================
with tab2:
    st.subheader("第二层 · 双词（36 个能力词）")
    st.caption("两个汉字组合，比单字更精确")
    
    categories = [
        ("🧠 推理类", ["推理","分析","预测","规划","决策"]),
        ("⚡ 生成类", ["生成","创作","设计","推荐","优化"]),
        ("👁️ 理解类", ["识别","理解","提取","分类","排序"]),
        ("💬 交互类", ["搜索","对话","反馈","审核","监控"]),
        ("💻 专业性", ["编程","建模","测试","标注","训练","评估"]),
        ("🤝 协同类", ["协作","分配","调度","同步","汇总"]),
    ]
    
    for cat_name, words in categories:
        st.markdown(f"**{cat_name}**")
        cols = st.columns(len(words))
        for i, w in enumerate(words):
            if w in TWO_WORDS:
                with cols[i]:
                    info = TWO_WORDS[w]
                    st.markdown(f"{info['emoji']} **{w}**")
                    st.caption(info['desc'])

# ============================================================
# Tab 3: 语法符号
# ============================================================
with tab3:
    st.subheader("第三层 · 语法符号（12 个）")
    st.caption("用符号替代英文语法关键词，结构化表达")
    
    cols = st.columns(3)
    for i, (sym, info) in enumerate(GRAMMAR_SYMBOLS.items()):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### `{sym}`")
                st.markdown(f"**{info['name']}** *({info['英文']})*")
                st.caption(info['用法'])
    
    st.divider()
    st.subheader("英文 → 中文 翻译对照")
    en_items = list(EN_TO_CN.items())
    for i in range(0, len(en_items), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(en_items):
                en, cn = en_items[i + j]
                with cols[j]:
                    st.code(f"{en} → {cn}", language="text")

# ============================================================
# Tab 4: 提示词示例
# ============================================================
with tab4:
    st.subheader("📝 用中文符号写提示词")
    st.caption("左边是中文符号版，右边是传统英文版，对比看看哪个更易懂")
    
    for ex in PROMPT_EXAMPLES:
        with st.expander(f"📌 {ex.name} — {ex.desc}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🐉 中文符号版**")
                st.code(ex.chinese_prompt, language="text")
            with col2:
                st.markdown("**🌍 传统英文版**")
                st.code(ex.english_prompt, language="text")
            st.success(f"💡 {ex.note}")

# ============================================================
# Tab 5: 智能体模板
# ============================================================
with tab5:
    st.subheader("🤖 用中文符号搭智能体")
    st.caption("【智能体 = 知 + 记 + 感 + 应 + 定 + 联】，纯中文定义")
    
    for agent in AGENT_TEMPLATES:
        with st.expander(f"🤖 {agent.name} — {agent.desc}"):
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown("**🐉 中文定义**")
                st.code(agent.chinese_def, language="text")
            with col2:
                st.markdown("**⚙️ 工作流程**")
                st.info(agent.workflow)
                st.markdown(f"**💡 适用场景**")
                st.success(agent.when_to_use)
                st.markdown("**🧩 用到的原语**")
                for p in agent.primitives:
                    if p in AGENT_PRIMITIVES:
                        st.caption(f"{AGENT_PRIMITIVES[p]['name']} — {AGENT_PRIMITIVES[p]['desc']}")
