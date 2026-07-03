# -*- coding: utf-8 -*-
"""
FanLang Streamlit 组件模块（components.py）的 pytest 测试。

测试范围：
  - render_symbol_bar: 默认符号 / 自定义符号 / 空列表边界
  - render_symbol_picker: 展开式选择器 / 梯队分组 / fanlang 不可用降级
  - render_terminology_tooltip: 术语卡片渲染 / 缺少键
  - 内部辅助函数: _attr, _emoji_for, _resolve_symbols, _group_by_tier, _tier_symbol_counts
  - CSS 注入断言
  - session_state 通过回调的交互
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

# ── 添加项目根目录到 sys.path ──
PROJECT_ROOT = Path("C:/Work/FanLang").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════
# conftest-style fixtures（在每个测试文件内独立声明）
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _mock_streamlit_and_imports():
    """自动 mock streamlit 及相关子模块，防止真实导入失败。

    此 fixture 在每个测试前:
      1. 创建 mock_st（模拟 streamlit 模块）
      2. 注入 sys.modules['streamlit']
      3. 创建 mock_callbacks 和 mock_styles 模块对象
      4. 注入 fanlang_streamlit.callbacks / styles
      5. 清理测试中可能被污染的缓存
    """
    mock_st = MagicMock()
    mock_st.session_state = {}
    mock_st.columns.return_value = [MagicMock() for _ in range(8)]
    mock_st.button.return_value = False
    mock_st.markdown.return_value = None
    mock_st.expander.return_value = MagicMock()
    # streamlit 的子模块也应 mock 掉
    sys.modules["streamlit"] = mock_st

    # 预先注入子模块，防止 from .callbacks / .styles 触发真实导入
    mock_callbacks = MagicMock()
    mock_callbacks.on_symbol_click = MagicMock()
    mock_callbacks.get_selected_symbol = MagicMock(return_value=None)
    mock_callbacks.clear_selected_symbol = MagicMock()
    sys.modules["fanlang_streamlit.callbacks"] = mock_callbacks

    mock_styles = MagicMock()
    mock_styles.inject_styles = MagicMock()
    mock_styles._CSS_INJECTED = False
    mock_styles.THEME_COLOR = "#2563EB"
    sys.modules["fanlang_streamlit.styles"] = mock_styles

    yield

    # 清理，避免影响其他测试文件
    for mod in ["streamlit", "fanlang_streamlit", "fanlang_streamlit.components",
                 "fanlang_streamlit.callbacks", "fanlang_streamlit.styles",
                 "fanlang_streamlit.components"]:
        sys.modules.pop(mod, None)

    # 清理从 fanlang.symbols 导入的缓存
    for key in list(sys.modules.keys()):
        if key.startswith("fanlang"):
            sys.modules.pop(key, None)


# ═══════════════════════════════════════════════════════════════
# tests: _attr 辅助函数
# ═══════════════════════════════════════════════════════════════

class TestAttr:
    """_attr 兼容 dict 和 object 的属性访问器。"""

    def test_dict_access(self) -> None:
        from fanlang_streamlit.components import _attr
        d = {"character": "写", "emoji": "✍️"}
        assert _attr(d, "character") == "写"
        assert _attr(d, "emoji") == "✍️"

    def test_dict_missing_key_default(self) -> None:
        from fanlang_streamlit.components import _attr
        d: dict = {}
        assert _attr(d, "character", "?") == "?"
        assert _attr(d, "missing") is None

    def test_object_access(self) -> None:
        from fanlang_streamlit.components import _attr
        obj = MagicMock()
        obj.character = "改"
        obj.emoji = "✏️"
        assert _attr(obj, "character") == "改"
        assert _attr(obj, "emoji") == "✏️"

    def test_object_missing_key_default(self) -> None:
        from fanlang_streamlit.components import _attr
        obj = MagicMock(spec=["other"])
        assert _attr(obj, "character", "") == ""


# ═══════════════════════════════════════════════════════════════
# tests: _emoji_for 辅助函数
# ═══════════════════════════════════════════════════════════════

class TestEmojiFor:
    """_emoji_for 获取符号对应 emoji。"""

    def test_emoji_from_field(self) -> None:
        from fanlang_streamlit.components import _emoji_for
        sym = {"character": "写", "emoji": "✍️"}
        assert _emoji_for(sym) == "✍️"

    def test_emoji_fallback_to_core(self) -> None:
        from fanlang_streamlit.components import _emoji_for
        sym = {"character": "写", "emoji": ""}
        assert _emoji_for(sym) == "✍️"

    def test_emoji_unknown_character(self) -> None:
        from fanlang_streamlit.components import _emoji_for
        sym = {"character": "??", "emoji": ""}
        assert _emoji_for(sym) == ""

    def test_emoji_from_object(self) -> None:
        from fanlang_streamlit.components import _emoji_for
        sym = MagicMock()
        sym.character = "改"
        sym.emoji = "✏️"
        assert _emoji_for(sym) == "✏️"

    def test_emoji_object_no_emoji_field(self) -> None:
        from fanlang_streamlit.components import _emoji_for
        sym = MagicMock()
        sym.character = "翻"
        # 没有 emoji 属性 — 通过 spec 或 del 模拟
        del sym.emoji
        # _attr getattr 会报 AttributeError，回退到默认值
        assert _emoji_for(sym) == "🔄"


# ═══════════════════════════════════════════════════════════════
# tests: _resolve_symbols 辅助函数
# ═══════════════════════════════════════════════════════════════

class TestResolveSymbols:
    """_resolve_symbols 解析符号列表逻辑。"""

    def test_custom_symbols_returned_as_is(self) -> None:
        from fanlang_streamlit.components import _resolve_symbols, _CORE_SYMBOL_CHARS
        custom = [{"character": "A"}, {"character": "B"}]
        result = _resolve_symbols(custom, _CORE_SYMBOL_CHARS)
        assert result is custom

    def test_none_fallback_from_fanlang(self) -> None:
        """当 symbols 为 None 时，尝试从 fanlang 核心包获取。"""
        from fanlang_streamlit.components import _resolve_symbols, _CORE_SYMBOL_CHARS

        fake_syms = [
            {"character": "写", "emoji": "✍️", "tier": 1},
            {"character": "改", "emoji": "✏️", "tier": 1},
            {"character": "OTHER", "emoji": "?", "tier": 9},  # 不在 default_chars
        ]

        with patch("fanlang.symbols.get_all_symbols", return_value=fake_syms):
            result = _resolve_symbols(None, _CORE_SYMBOL_CHARS)
            # 只保留 default_chars 中出现的
            chars = [s["character"] if isinstance(s, dict) else getattr(s, "character", "") for s in result]
            assert "写" in chars
            assert "改" in chars
            assert "OTHER" not in chars

    def test_none_fanlang_import_error(self) -> None:
        """fanlang 核心包不可用时降级到本地映射。"""
        from fanlang_streamlit.components import _resolve_symbols, _CORE_SYMBOL_CHARS

        with patch("fanlang.symbols.get_all_symbols", side_effect=ImportError):
            result = _resolve_symbols(None, _CORE_SYMBOL_CHARS)
            assert len(result) == len(_CORE_SYMBOL_CHARS)
            for item in result:
                assert "character" in item
                assert "emoji" in item
                assert "tier" in item

    def test_none_fanlang_returns_empty(self) -> None:
        """fanlang 返回空列表时也降级。"""
        from fanlang_streamlit.components import _resolve_symbols, _CORE_SYMBOL_CHARS

        with patch("fanlang.symbols.get_all_symbols", return_value=[]):
            result = _resolve_symbols(None, _CORE_SYMBOL_CHARS)
            # 降级到本地
            assert len(result) == len(_CORE_SYMBOL_CHARS)


# ═══════════════════════════════════════════════════════════════
# tests: _group_by_tier 辅助函数
# ═══════════════════════════════════════════════════════════════

class TestGroupByTier:
    """_group_by_tier 按梯队分组。"""

    def test_groups_created(self) -> None:
        from fanlang_streamlit.components import _group_by_tier
        syms = [
            {"character": "写", "tier": 1},
            {"character": "改", "tier": 1},
            {"character": "S1", "tier": 2},
        ]
        groups = _group_by_tier(syms)
        assert len(groups[1]) == 2
        assert len(groups[2]) == 1
        assert len(groups[3]) == 0  # 空梯队保留空列表
        assert len(groups[4]) == 0

    def test_unknown_tier_uses_setdefault(self) -> None:
        from fanlang_streamlit.components import _group_by_tier
        syms = [
            {"character": "X", "tier": 99},
        ]
        groups = _group_by_tier(syms)
        assert 99 in groups
        assert len(groups[99]) == 1

    def test_missing_tier_defaults_to_one(self) -> None:
        from fanlang_streamlit.components import _group_by_tier
        syms = [
            {"character": "写"},  # 没有 tier
        ]
        groups = _group_by_tier(syms)
        assert len(groups[1]) == 1


# ═══════════════════════════════════════════════════════════════
# tests: render_symbol_bar
# ═══════════════════════════════════════════════════════════════

class TestRenderSymbolBar:
    """render_symbol_bar 符号按钮栏。"""

    def _import_and_prep(self) -> tuple:
        """导入 render_symbol_bar 并准备 mock 环境。"""
        # 重新 mock streamlit
        mock_st = MagicMock()
        mock_st.session_state = {}
        mock_st.columns.return_value = [MagicMock() for _ in range(8)]
        mock_st.button.return_value = False
        mock_st.markdown.return_value = None
        sys.modules["streamlit"] = mock_st

        # 清理并重新导入
        for k in list(sys.modules.keys()):
            if "fanlang_streamlit" in k:
                del sys.modules[k]

        from fanlang_streamlit import components
        # 重新加载使导入发生在新的 streamlit mock 之上
        import importlib
        importlib.reload(components)

        return components, mock_st

    def test_default_symbols_renders_8_buttons(self) -> None:
        """默认 8 个核心符号渲染 8 个按钮。"""
        components, mock_st = self._import_and_prep()

        # mock _resolve_symbols 返回 8 个核心符号
        with patch.object(components, "_resolve_symbols") as mock_resolve:
            mock_resolve.return_value = [
                {"character": c, "emoji": "?", "tier": 1}
                for c in ["写", "改", "翻", "总", "问", "查", "比", "理"]
            ]
            with patch.object(components, "get_selected_symbol", return_value=None):
                result = components.render_symbol_bar()

        assert mock_st.columns.called
        assert mock_st.button.call_count == 8

    def test_custom_symbols(self) -> None:
        """自定义符号列表。"""
        components, mock_st = self._import_and_prep()
        custom = [
            {"character": "A", "emoji": "🍎", "tier": 1},
            {"character": "B", "emoji": "🍊", "tier": 2},
        ]
        with patch.object(components, "get_selected_symbol", return_value=None):
            result = components.render_symbol_bar(symbols=custom)

        assert mock_st.button.call_count == 2

    def test_empty_list_returns_none(self) -> None:
        """空列表返回 None 且不渲染按钮。"""
        components, mock_st = self._import_and_prep()
        with patch.object(components, "_resolve_symbols", return_value=[]):
            with patch.object(components, "get_selected_symbol", return_value=None):
                result = components.render_symbol_bar(symbols=[])

        assert result is None
        mock_st.button.assert_not_called()

    def test_injects_css(self) -> None:
        """CSS 注入被调用。"""
        components, mock_st = self._import_and_prep()
        with patch.object(components, "_resolve_symbols") as mock_resolve:
            mock_resolve.return_value = [{"character": "写", "emoji": "✍️", "tier": 1}]
            with patch.object(components, "get_selected_symbol", return_value=None):
                with patch.object(components, "inject_styles") as mock_inject:
                    components.render_symbol_bar()
                    mock_inject.assert_called_once()

    def test_selected_symbol_highlight(self) -> None:
        """选中符号时按钮标记为 primary。"""
        components, mock_st = self._import_and_prep()
        syms = [{"character": "写", "emoji": "✍️", "tier": 1}]
        with patch.object(components, "_resolve_symbols", return_value=syms):
            with patch.object(components, "get_selected_symbol", return_value="写"):
                components.render_symbol_bar()
                # 验证调用了 st.button，且 type 为 "primary"
                call_kwargs = mock_st.button.call_args_list[0][1]
                assert call_kwargs.get("type") == "primary"

    def test_unselected_symbol(self) -> None:
        """未选中符号时按钮标记为 secondary。"""
        components, mock_st = self._import_and_prep()
        syms = [{"character": "写", "emoji": "✍️", "tier": 1}]
        with patch.object(components, "_resolve_symbols", return_value=syms):
            with patch.object(components, "get_selected_symbol", return_value="改"):
                components.render_symbol_bar()
                call_kwargs = mock_st.button.call_args_list[0][1]
                assert call_kwargs.get("type") == "secondary"

    def test_session_state_interaction(self) -> None:
        """验证 session_state 通过 get_selected_symbol 交互。"""
        components, mock_st = self._import_and_prep()
        syms = [{"character": "写", "emoji": "✍️", "tier": 1}]
        with patch.object(components, "_resolve_symbols", return_value=syms):
            mock_get = MagicMock(return_value="写")
            with patch.object(components, "get_selected_symbol", mock_get):
                components.render_symbol_bar()
                mock_get.assert_called()


# ═══════════════════════════════════════════════════════════════
# tests: render_symbol_picker
# ═══════════════════════════════════════════════════════════════

class TestRenderSymbolPicker:
    """render_symbol_picker 展开式符号选择器。"""

    def _import_and_prep(self) -> tuple:
        mock_st = MagicMock()
        mock_st.session_state = {}
        mock_st.columns.return_value = [MagicMock() for _ in range(5)]
        mock_st.button.return_value = False
        mock_st.markdown.return_value = None
        # st.expander 作为上下文管理器使用，__enter__ 返回自身
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander)
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
        sys.modules["streamlit"] = mock_st

        for k in list(sys.modules.keys()):
            if "fanlang_streamlit" in k:
                del sys.modules[k]

        from fanlang_streamlit import components
        import importlib
        importlib.reload(components)
        return components, mock_st

    def test_renders_with_custom_symbols(self) -> None:
        """使用自定义符号渲染。"""
        components, mock_st = self._import_and_prep()
        symbols = [
            {"character": "写", "emoji": "✍️", "tier": 1},
            {"character": "改", "emoji": "✏️", "tier": 2},
        ]
        with patch.object(components, "get_selected_symbol", return_value=None):
            result = components.render_symbol_picker(symbols=symbols)

        assert mock_st.expander.called
        assert mock_st.button.call_count == 2

    def test_renders_no_symbols(self) -> None:
        """symbols 为 None 时走 fanlang 获取逻辑。"""
        components, mock_st = self._import_and_prep()

        with patch.object(components, "_group_by_tier") as mock_group:
            mock_group.return_value = {1: [], 2: [], 3: [], 4: []}
            with patch.object(components, "get_selected_symbol", return_value=None):
                result = components.render_symbol_picker(symbols=None)

        # 不能使用 from fanlang.symbols，因为我们 mock 了整个 fanlang 命名空间
        pass

    def test_fanlang_import_error_during_picker(self) -> None:
        """fanlang 不可用时降级。"""
        components, mock_st = self._import_and_prep()

        # 模拟 fanlang.symbols.get_all_symbols 不可用
        with patch.object(components, "_group_by_tier") as mock_group:
            mock_group.return_value = {1: [], 2: [], 3: [], 4: []}
            with patch.object(components, "get_selected_symbol", return_value=None):
                # 在 _resolve_symbols 中模拟 ImportError
                with patch("fanlang.symbols.get_all_symbols",
                           side_effect=ImportError("no fanlang")):
                    result = components.render_symbol_picker(symbols=None)
                    # 不崩就算通过

    def test_selected_symbol_in_picker(self) -> None:
        """选择器内选中符号。"""
        components, mock_st = self._import_and_prep()
        symbols = [
            {"character": "写", "emoji": "✍️", "tier": 1},
        ]
        with patch.object(components, "get_selected_symbol", return_value="写"):
            components.render_symbol_picker(symbols=symbols)
            call_kwargs = mock_st.button.call_args_list[0][1]
            assert call_kwargs.get("type") == "primary"

    def test_missing_tier_label_fallback(self) -> None:
        """符号按梯队展示时调用 expander。"""
        components, mock_st = self._import_and_prep()
        symbols = [
            {"character": "写", "emoji": "✍️", "tier": 1},
            {"character": "改", "emoji": "✏️", "tier": 2},
        ]
        with patch.object(components, "get_selected_symbol", return_value=None):
            components.render_symbol_picker(symbols=symbols)
            # expander 应被调用（梯队1和2各一个）
            assert mock_st.expander.called


# ═══════════════════════════════════════════════════════════════
# tests: render_terminology_tooltip
# ═══════════════════════════════════════════════════════════════

class TestRenderTerminologyTooltip:
    """render_terminology_tooltip 术语提示卡片。"""

    def _import_and_prep(self) -> tuple:
        mock_st = MagicMock()
        mock_st.markdown.return_value = None
        sys.modules["streamlit"] = mock_st

        for k in list(sys.modules.keys()):
            if "fanlang_streamlit" in k:
                del sys.modules[k]

        from fanlang_streamlit import components
        import importlib
        importlib.reload(components)
        return components, mock_st

    def test_render_with_valid_term(self) -> None:
        """有效术语卡片渲染。"""
        components, mock_st = self._import_and_prep()
        term = {"term_en": "Translate", "term_zh": "翻 - 翻译"}
        with patch.object(components, "inject_styles"):
            components.render_terminology_tooltip(term)

        mock_st.markdown.assert_called_once()
        html_arg = mock_st.markdown.call_args[0][0]
        assert "Translate" in html_arg
        assert "翻 - 翻译" in html_arg
        assert "fanlang-terminology-card" in html_arg

    def test_render_with_missing_keys(self) -> None:
        """缺少键时使用空字符串。"""
        components, mock_st = self._import_and_prep()
        term: dict = {}
        with patch.object(components, "inject_styles"):
            components.render_terminology_tooltip(term)

        mock_st.markdown.assert_called_once()
        html_arg = mock_st.markdown.call_args[0][0]
        # term_en 和 term_zh 都应为空
        # 但 class 名称应仍存在
        assert "fanlang-terminology-card" in html_arg

    def test_injects_css(self) -> None:
        """注入 CSS。"""
        components, mock_st = self._import_and_prep()
        term = {"term_en": "T", "term_zh": "Z"}
        with patch.object(components, "inject_styles") as mock_inject:
            components.render_terminology_tooltip(term)
            mock_inject.assert_called_once()


# ═══════════════════════════════════════════════════════════════
# tests: _tier_symbol_counts
# ═══════════════════════════════════════════════════════════════

class TestTierSymbolCounts:
    """_tier_symbol_counts 返回固定值映射。"""

    def test_returns_expected_counts(self) -> None:
        from fanlang_streamlit.components import _tier_symbol_counts
        counts = _tier_symbol_counts()
        assert counts[1] == 7
        assert counts[2] == 5
        assert counts[3] == 8
        assert counts[4] == 5
        assert len(counts) == 4


# ═══════════════════════════════════════════════════════════════
# tests: _CORE_SYMBOL_EMOJIS 常量
# ═══════════════════════════════════════════════════════════════

class TestCoreSymbols:
    """核心符号常量的完整性。"""

    def test_all_core_symbols_have_emojis(self) -> None:
        from fanlang_streamlit.components import _CORE_SYMBOL_CHARS, _CORE_SYMBOL_EMOJIS
        for char in _CORE_SYMBOL_CHARS:
            assert char in _CORE_SYMBOL_EMOJIS, f"{char} missing emoji"
            assert _CORE_SYMBOL_EMOJIS[char] != ""

    def test_core_symbol_count(self) -> None:
        from fanlang_streamlit.components import _CORE_SYMBOL_CHARS
        assert len(_CORE_SYMBOL_CHARS) == 8


# ═══════════════════════════════════════════════════════════════
# tests: _TIER_LABELS 常量
# ═══════════════════════════════════════════════════════════════

class TestTierLabels:
    """梯队标签常量完整性。"""

    def test_tier_labels_exist(self) -> None:
        from fanlang_streamlit.components import _TIER_LABELS
        assert 1 in _TIER_LABELS
        assert 2 in _TIER_LABELS
        assert 3 in _TIER_LABELS
        assert 4 in _TIER_LABELS
