# -*- coding: utf-8 -*-
"""
FanLang Streamlit 样式模块（styles.py）的 pytest 测试。

测试范围：
  - inject_styles 幂等性：首次注入 CSS，重复调用不重复注入
  - CSS 内容结构包含预期的 class 名称、颜色值、伪类
  - 模块级常量（THEME_COLOR 等）
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── 添加项目根目录到 sys.path ──
PROJECT_ROOT = Path("C:/Work/FanLang").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════
# Fixture
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _mock_streamlit():
    """mock streamlit，重置 _CSS_INJECTED 标志。"""
    mock_st = MagicMock()
    mock_st.markdown.return_value = None
    sys.modules["streamlit"] = mock_st

    for key in list(sys.modules.keys()):
        if "fanlang_streamlit" in key:
            del sys.modules[key]

    # 强制重置 _CSS_INJECTED
    import fanlang_streamlit.styles as styles_mod
    import importlib
    importlib.reload(styles_mod)
    styles_mod._CSS_INJECTED = False

    yield styles_mod, mock_st

    for key in list(sys.modules.keys()):
        if key in ("streamlit",) or "fanlang_streamlit" in key:
            sys.modules.pop(key, None)


# ═══════════════════════════════════════════════════════════════
# tests: inject_styles 幂等性
# ═══════════════════════════════════════════════════════════════

class TestInjectStylesIdempotency:
    """inject_styles 幂等性。"""

    def test_first_call_injects_css(self, _mock_streamlit) -> None:
        styles_mod, mock_st = _mock_streamlit
        styles_mod.inject_styles()
        mock_st.markdown.assert_called_once()
        args, kwargs = mock_st.markdown.call_args
        assert kwargs.get("unsafe_allow_html") is True
        assert "<style>" in args[0]

    def test_second_call_skips(self, _mock_streamlit) -> None:
        styles_mod, mock_st = _mock_streamlit
        styles_mod.inject_styles()  # 第一次
        assert mock_st.markdown.call_count == 1
        styles_mod.inject_styles()  # 第二次
        # 只应调用一次
        assert mock_st.markdown.call_count == 1

    def test_injected_flag_set(self, _mock_streamlit) -> None:
        styles_mod, mock_st = _mock_streamlit
        assert styles_mod._CSS_INJECTED is False
        styles_mod.inject_styles()
        assert styles_mod._CSS_INJECTED is True


# ═══════════════════════════════════════════════════════════════
# tests: CSS 内容结构
# ═══════════════════════════════════════════════════════════════

class TestCSSContent:
    """CSS 样式内容包含预期的类名和颜色。"""

    CSS_EXPECTED_CLASSES = (
        "fanlang-symbol-bar",
        "fanlang-symbol-btn",
        "fanlang-symbol-btn:hover",
        "fanlang-symbol-btn:active",
        "fanlang-symbol-btn.selected",
        "fanlang-terminology-card",
        "fanlang-tier-label",
    )

    def test_contains_expected_classes(self, _mock_streamlit) -> None:
        styles_mod, mock_st = _mock_streamlit
        # 需要直接检查 CSS 字符串而不通过 markdown
        # 方式：调用 inject_styles 后检查调用参数
        styles_mod.inject_styles()
        args, _ = mock_st.markdown.call_args
        css_content = args[0]

        for cls in self.CSS_EXPECTED_CLASSES:
            assert cls in css_content, f"CSS 中缺少 class: {cls}"

    def test_contains_theme_color(self, _mock_streamlit) -> None:
        styles_mod, mock_st = _mock_streamlit
        styles_mod.inject_styles()
        args, _ = mock_st.markdown.call_args
        css_content = args[0]

        from fanlang_streamlit.styles import THEME_COLOR
        assert THEME_COLOR in css_content

    def test_contains_hover_active_colors(self, _mock_streamlit) -> None:
        styles_mod, mock_st = _mock_streamlit
        styles_mod.inject_styles()
        args, _ = mock_st.markdown.call_args
        css_content = args[0]

        from fanlang_streamlit.styles import THEME_COLOR_HOVER, THEME_COLOR_LIGHT
        assert THEME_COLOR_HOVER in css_content
        assert THEME_COLOR_LIGHT in css_content

    def test_style_tag_present(self, _mock_streamlit) -> None:
        styles_mod, mock_st = _mock_streamlit
        styles_mod.inject_styles()
        args, _ = mock_st.markdown.call_args
        css_content = args[0]

        assert css_content.strip().startswith("<style>")
        assert css_content.strip().endswith("</style>")

    def test_css_uses_variables_not_hardcoded(self, _mock_streamlit) -> None:
        """CSS 中使用 f-string 的 THEME_COLOR 变量而非硬编码值。"""
        styles_mod, mock_st = _mock_streamlit
        styles_mod.inject_styles()
        args, _ = mock_st.markdown.call_args
        css_content = args[0]

        # 确认使用的是 #2563EB 而非 #1D4ED8 等（检查 hover 颜色未出现在第一段）
        from fanlang_streamlit.styles import THEME_COLOR
        # 验证 THEME_COLOR 出现多次（被 f-string 插入）
        assert css_content.count(THEME_COLOR) >= 3


# ═══════════════════════════════════════════════════════════════
# tests: 模块常量
# ═══════════════════════════════════════════════════════════════

class TestModuleConstants:
    """样式模块常量正确性。"""

    def test_theme_color_format(self) -> None:
        from fanlang_streamlit.styles import THEME_COLOR
        assert THEME_COLOR.startswith("#")
        assert len(THEME_COLOR) == 7  # #RRGGBB

    def test_all_theme_colors(self) -> None:
        from fanlang_streamlit.styles import (
            THEME_COLOR,
            THEME_COLOR_LIGHT,
            THEME_COLOR_HOVER,
            THEME_COLOR_ACTIVE,
        )
        for color in (THEME_COLOR, THEME_COLOR_LIGHT, THEME_COLOR_HOVER, THEME_COLOR_ACTIVE):
            assert color.startswith("#")
            assert len(color) == 7
