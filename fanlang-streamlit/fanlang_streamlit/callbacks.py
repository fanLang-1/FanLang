"""FanLang Streamlit 回调函数模块。

提供符号交互的回调函数，用于管理 Streamlit session_state。
"""

from __future__ import annotations

from typing import Optional

import streamlit as st


def on_symbol_click(character: str) -> None:
    """符号点击回调：将选中的 FanLang 符号字符写入 session_state。

    该回调被设计用于 Streamlit 按钮的 on_click 参数。点击后，
    选中的符号字符会存入 st.session_state["fanlang_selected_symbol"]，
    供后续组件读取。

    Args:
        character: 被点击的 FanLang 符号字符（如 "写"、"改"、"翻" 等）。
    """
    st.session_state["fanlang_selected_symbol"] = character


def clear_selected_symbol() -> None:
    """清除当前选中的符号。

    将 session_state 中的 fanlang_selected_symbol 重置为 None。
    """
    st.session_state["fanlang_selected_symbol"] = None


def get_selected_symbol() -> Optional[str]:
    """从 session_state 中获取当前选中的符号。

    Returns:
        当前选中的符号字符，如果未选中则返回 None。
    """
    return st.session_state.get("fanlang_selected_symbol", None)
