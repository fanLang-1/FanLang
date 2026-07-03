"""FanLang Streamlit —— 为 FanLang 符号系统准备的 Streamlit 集成插件。

提供可直接嵌入 Streamlit 应用的交互组件：

核心导出：
- ``render_symbol_bar``：符号按钮栏（一行核心符号）
- ``render_symbol_picker``：展开式符号选择器（按梯队分组）
- ``render_terminology_tooltip``：术语提示卡片

辅助导出：
- ``on_symbol_click``：符号点击回调
- ``clear_selected_symbol``：清除选中状态
- ``get_selected_symbol``：读取当前选中符号
- ``inject_styles``：手动注入自定义 CSS

用法示例::

    import streamlit as st
    from fanlang_streamlit import render_symbol_bar, render_symbol_picker

    selected = render_symbol_bar()
    if selected:
        st.write(f"你选择了: {selected}")
"""

from __future__ import annotations

from .callbacks import (
    clear_selected_symbol,
    get_selected_symbol,
    on_symbol_click,
)
from .components import (
    render_symbol_bar,
    render_symbol_picker,
    render_terminology_tooltip,
)
from .styles import inject_styles

__all__: list[str] = [
    # 核心组件
    "render_symbol_bar",
    "render_symbol_picker",
    "render_terminology_tooltip",
    # 回调函数
    "on_symbol_click",
    "clear_selected_symbol",
    "get_selected_symbol",
    # 样式工具
    "inject_styles",
]
