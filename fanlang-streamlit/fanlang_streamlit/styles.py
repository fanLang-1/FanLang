"""FanLang Streamlit 样式模块。

通过 st.markdown 注入自定义 CSS，为符号按钮和术语提示卡片提供统一的视觉风格。
主题色为 #2563EB（蓝色系）。
"""

from __future__ import annotations

import streamlit as st

# ── 主题色定义 ──────────────────────────────────────────────
THEME_COLOR: str = "#2563EB"
THEME_COLOR_LIGHT: str = "#DBEAFE"
THEME_COLOR_HOVER: str = "#1D4ED8"
THEME_COLOR_ACTIVE: str = "#1E40AF"


_CSS_INJECTED: bool = False


def inject_styles() -> None:
    """向 Streamlit 页面注入 FanLang 自定义 CSS 样式。

    该函数幂等（同一会话中重复调用不会重复注入）。包含以下样式：
    - .fanlang-symbol-btn：符号按钮基础样式（圆角、边框、过渡动效）
    - .fanlang-symbol-btn:hover：鼠标悬停效果
    - .fanlang-symbol-btn.selected：选中状态高亮样式
    - .fanlang-terminology-card：术语提示卡片样式
    - .fanlang-symbol-bar：符号栏容器样式
    """
    global _CSS_INJECTED
    if _CSS_INJECTED:
        return

    css: str = f"""
    <style>
        /* ── 符号栏容器 ── */
        .fanlang-symbol-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
            padding: 8px 0;
        }}

        /* ── 符号按钮基础样式 ── */
        .fanlang-symbol-btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            padding: 6px 14px;
            border-radius: 8px;
            border: 2px solid #E5E7EB;
            background-color: #FFFFFF;
            color: #374151;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
            white-space: nowrap;
        }}

        .fanlang-symbol-btn:hover {{
            border-color: {THEME_COLOR};
            background-color: {THEME_COLOR_LIGHT};
            color: {THEME_COLOR};
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.15);
        }}

        .fanlang-symbol-btn:active {{
            transform: translateY(0);
            box-shadow: none;
        }}

        /* ── 选中状态高亮 ── */
        .fanlang-symbol-btn.selected {{
            border-color: {THEME_COLOR};
            background-color: {THEME_COLOR};
            color: #FFFFFF;
            font-weight: 600;
            box-shadow: 0 2px 12px rgba(37, 99, 235, 0.3);
        }}

        .fanlang-symbol-btn.selected:hover {{
            background-color: {THEME_COLOR_HOVER};
            border-color: {THEME_COLOR_HOVER};
            color: #FFFFFF;
        }}

        /* ── 术语提示卡片 ── */
        .fanlang-terminology-card {{
            display: inline-block;
            padding: 10px 16px;
            border-radius: 10px;
            border: 1px solid #E5E7EB;
            background: linear-gradient(135deg, #F8FAFC, #FFFFFF);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
            font-size: 14px;
            line-height: 1.6;
            color: #374151;
        }}

        .fanlang-terminology-card .term-en {{
            font-weight: 600;
            color: {THEME_COLOR};
            font-size: 15px;
        }}

        .fanlang-terminology-card .term-zh {{
            color: #6B7280;
            font-size: 13px;
            margin-top: 2px;
        }}

        /* ── 梯队标签 ── */
        .fanlang-tier-label {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            color: {THEME_COLOR};
            background-color: {THEME_COLOR_LIGHT};
            margin-bottom: 8px;
        }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)
    _CSS_INJECTED = True
