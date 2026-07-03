"""
🦯 中文 AI 脚手架 · OODA 版
=============================
先问清楚，再开干。
用户说"帮我写点东西"，系统会追问"写什么？多长？什么风格？"
问清楚了才干活，干完了问"满意吗？"
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.symbols import SINGLE_CHARS, CORE_7, translate
from src.ooda import ooda_cycle, detect_symbol
from src.engine import check_ollama

st.set_page_config(page_title="🦯 中文 AI 脚手架", page_icon="🦯", layout="centered")

# 检查 Ollama
if not check_ollama():
    st.error("⚠️ 请先安装并启动 Ollama\n👉 https://ollama.com")
    st.stop()

# ============================================================
# 初始化会话状态
# ============================================================
# 关键的 OODA 状态变量
if "phase" not in st.session_state:
    st.session_state.phase = "idle"       # idle | orienting | executing | observing
if "active_symbol" not in st.session_state:
    st.session_state.active_symbol = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""    # 用户当前输入
if "last_result" not in st.session_state:
    st.session_state.last_result = ""      # 上次执行结果
if "clarify_count" not in st.session_state:
    st.session_state.clarify_count = 0     # 防止死循环

# ============================================================
# 界面
# ============================================================
st.title("🦯 中文 AI")
st.caption("选一个字，开始对话。说不清楚？我来问你。")

# ── 符号按钮 ──
highlight = CORE_7 + ["解","教","比","查","理"]
cols = st.columns(6)
for i, k in enumerate(highlight):
    info = SINGLE_CHARS[k]
    with cols[i % 6]:
        btn_type = "primary" if st.session_state.active_symbol == k else "secondary"
        if st.button(f"{info['e']} {k}", use_container_width=True, type=btn_type, help=info['d']):
            st.session_state.active_symbol = k
            st.session_state.phase = "idle"
            st.session_state.messages = []
            st.rerun()

# 更多符号
if st.checkbox("显示更多符号", key="show_more"):
    more = [k for k in SINGLE_CHARS if k not in highlight]
    cols2 = st.columns(6)
    for i, k in enumerate(more):
        info = SINGLE_CHARS[k]
        with cols2[i % 6]:
            if st.button(f"{info['e']} {k}", use_container_width=True, type="primary" if st.session_state.active_symbol == k else "secondary", help=info['d']):
                st.session_state.active_symbol = k
                st.session_state.phase = "idle"
                st.session_state.messages = []
                st.rerun()

# 状态提示
status_bar = st.container()
with status_bar:
    if st.session_state.active_symbol:
        info = SINGLE_CHARS[st.session_state.active_symbol]
        phase_names = {
            "idle": f"{info['e']} 已选 **{info['n']}**，请输入需求",
            "orienting": f"{info['e']} 🤔 正在问清楚...",
            "executing": f"{info['e']} ⚡ 正在执行...",
            "observing": f"{info['e']} ✅ 完成",
        }
        st.info(phase_names.get(st.session_state.phase, ""))
    else:
        st.info("💡 点上面一个字开始，或者直接输入问题（系统会自动判断你想干什么）")

# ── 聊天记录 ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 输入框 ──
user_input = st.chat_input(
    "直接说你的需求..." if not st.session_state.active_symbol 
    else f"【{st.session_state.active_symbol}】说你的需求..."
)

if user_input:
    # ============================================================
    # 收到用户输入 → 进入 OODA 流程
    # ============================================================
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # 如果没有选符号，自动检测
        if not st.session_state.active_symbol:
            with st.spinner("🤔 判断你想干什么..."):
                st.session_state.active_symbol = detect_symbol(user_input)
            symbol_name = SINGLE_CHARS.get(st.session_state.active_symbol, {}).get("n", "")
            st.caption(f"🔄 自动识别：{SINGLE_CHARS[st.session_state.active_symbol]['e']}【{st.session_state.active_symbol}】{symbol_name}")

        # OODA 循环
        max_cycles = 5
        cycle = 0
        result = ""
        feedback_msg = ""

        while cycle < max_cycles:
            cycle += 1
            st.session_state.phase = "orienting"

            # 一次 OODA 循环
            out, satisfied = ooda_cycle(st.session_state.active_symbol, user_input)

            if out["status"] == "clarify":
                # Orient 说需要追问
                question = out["question"]
                st.markdown(f"🤔 **{question}**")
                st.session_state.messages.append({"role": "assistant", "content": f"🤔 {question}"})
                st.session_state.phase = "idle"
                st.session_state.pending_input = user_input
                st.stop()  # 等用户回答

            elif out["status"] == "done":
                result = out["result"]
                feedback_msg = out.get("feedback", "")

                # 显示结果
                st.markdown(result)
                st.session_state.messages.append({"role": "assistant", "content": result})
                st.session_state.last_result = result

                if satisfied:
                    # 用户满意
                    st.session_state.phase = "observing"
                    if feedback_msg:
                        st.success(f"✅ {feedback_msg}")
                    break
                else:
                    # 不满意，带着反馈继续循环
                    if cycle < max_cycles - 1:
                        st.warning(f"🔄 {feedback_msg}，我重新来...")
                        user_input = f"{user_input}，但是{feedback_msg}"
                        st.session_state.phase = "orienting"
                    else:
                        st.info("💡 试了几次还是不太满意，要不换个说法试试？")
                        break
            else:
                break

st.divider()
with st.expander("📖 完整符号表"):
    for c, info in SINGLE_CHARS.items():
        st.caption(f"{info['e']} **【{c}】** {info['n']} — {info['d']}")
st.caption("Powered by 🐉 中文 AI 语言 · OODA 引擎")
