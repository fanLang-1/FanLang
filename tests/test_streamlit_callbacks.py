# -*- coding: utf-8 -*-
"""
FanLang Streamlit 回调函数模块（callbacks.py）的 pytest 测试。

测试范围：
  - on_symbol_click: 将选中符号写入 session_state
  - clear_selected_symbol: 清除 session_state 中的选中符号
  - get_selected_symbol: 读取 session_state 中的选中符号（存在 / 不存在）
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

# ── 添加项目根目录到 sys.path ──
PROJECT_ROOT = Path("C:/Work/FanLang").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════
# Fixture: mock streamlit 和 callbacks 模块
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _mock_streamlit(monkeypatch):
    """在每个测试前 mock streamlit.session_state 为普通 dict。"""
    mock_st = MagicMock()
    mock_session: Dict[str, Any] = {}
    mock_st.session_state = mock_session
    # 使 st.session_state["key"] = value 直接修改 dict
    type(mock_st).session_state = PropertyMock(return_value=mock_session)

    sys.modules["streamlit"] = mock_st

    # 清理 callbacks 模块缓存
    for key in list(sys.modules.keys()):
        if "fanlang_streamlit" in key:
            del sys.modules[key]

    yield

    for key in list(sys.modules.keys()):
        if key in ("streamlit",) or "fanlang_streamlit" in key:
            sys.modules.pop(key, None)

    # 清理 PropertyMock
    monkeypatch.undo()


# ═══════════════════════════════════════════════════════════════
# tests: on_symbol_click
# ═══════════════════════════════════════════════════════════════

class TestOnSymbolClick:
    """on_symbol_click 回调写入 session_state。"""

    def test_sets_session_state(self) -> None:
        from fanlang_streamlit.callbacks import on_symbol_click
        on_symbol_click("写")
        assert "fanlang_selected_symbol" in sys.modules["streamlit"].session_state
        assert sys.modules["streamlit"].session_state["fanlang_selected_symbol"] == "写"

    def test_overwrites_previous(self) -> None:
        from fanlang_streamlit.callbacks import on_symbol_click
        # 首次设置
        on_symbol_click("写")
        assert sys.modules["streamlit"].session_state["fanlang_selected_symbol"] == "写"
        # 覆盖
        on_symbol_click("改")
        assert sys.modules["streamlit"].session_state["fanlang_selected_symbol"] == "改"

    def test_with_empty_string(self) -> None:
        from fanlang_streamlit.callbacks import on_symbol_click
        on_symbol_click("")
        assert sys.modules["streamlit"].session_state["fanlang_selected_symbol"] == ""

    def test_with_unicode(self) -> None:
        from fanlang_streamlit.callbacks import on_symbol_click
        on_symbol_click("翻译")
        assert sys.modules["streamlit"].session_state["fanlang_selected_symbol"] == "翻译"


# ═══════════════════════════════════════════════════════════════
# tests: clear_selected_symbol
# ═══════════════════════════════════════════════════════════════

class TestClearSelectedSymbol:
    """clear_selected_symbol 将 session_state 中选中符号设为 None。"""

    def test_clears_to_none(self) -> None:
        from fanlang_streamlit.callbacks import clear_selected_symbol, on_symbol_click
        # 先设置
        on_symbol_click("写")
        assert sys.modules["streamlit"].session_state["fanlang_selected_symbol"] == "写"
        # 清除
        clear_selected_symbol()
        assert sys.modules["streamlit"].session_state["fanlang_selected_symbol"] is None

    def test_clear_when_not_set(self) -> None:
        """session_state 中无 key 时不会报错（因为直接赋值 None）。"""
        from fanlang_streamlit.callbacks import clear_selected_symbol
        clear_selected_symbol()
        # 现在应该已经有了 key 且值为 None
        assert "fanlang_selected_symbol" in sys.modules["streamlit"].session_state
        assert sys.modules["streamlit"].session_state["fanlang_selected_symbol"] is None


# ═══════════════════════════════════════════════════════════════
# tests: get_selected_symbol
# ═══════════════════════════════════════════════════════════════

class TestGetSelectedSymbol:
    """get_selected_symbol 读取 session_state。"""

    def test_returns_selected(self) -> None:
        from fanlang_streamlit.callbacks import get_selected_symbol, on_symbol_click
        on_symbol_click("查")
        result = get_selected_symbol()
        assert result == "查"

    def test_returns_none_when_not_set(self) -> None:
        """session_state 中无 key 时返回 None。"""
        from fanlang_streamlit.callbacks import get_selected_symbol
        # 确保 key 不存在
        ss = sys.modules["streamlit"].session_state
        ss.pop("fanlang_selected_symbol", None)
        result = get_selected_symbol()
        assert result is None

    def test_returns_none_after_clear(self) -> None:
        from fanlang_streamlit.callbacks import (
            clear_selected_symbol,
            get_selected_symbol,
            on_symbol_click,
        )
        on_symbol_click("比")
        clear_selected_symbol()
        result = get_selected_symbol()
        assert result is None
