# -*- coding: utf-8 -*-
"""
FanLang 测试共享 fixtures 和 mock 工具
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

import pytest

# ── 添加项目根目录到 sys.path ──
PROJECT_ROOT = Path("C:/Work/FanLang").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# Mock Ollama / 网络调用工具
# ============================================================

def make_mock_chat(response: str = "模拟回复"):
    """创建一个返回固定文本的 mock chat 函数。"""
    def _chat(*args, **kwargs):
        return response
    return _chat


def make_mock_chat_json(json_data: dict):
    """创建一个返回 JSON 字符串的 mock chat 函数。"""
    def _chat(*args, **kwargs):
        return json.dumps(json_data, ensure_ascii=False)
    return _chat


@pytest.fixture
def mock_requests_post():
    """Mock requests.post，返回指定 JSON。"""
    with patch("fanlang.seminar.requests.post") as mock_post:
        mock_resp = Mock()
        mock_resp.json.return_value = {"message": {"content": "模拟研讨厅回复"}}
        mock_post.return_value = mock_resp
        yield mock_post


@pytest.fixture
def mock_ollama_chat_clear():
    """Mock _ollama_chat 返回 '清晰' 的 orient 结果。"""
    with patch("fanlang.ooda._ollama_chat") as mock:
        mock.return_value = json.dumps({
            "clear": True,
            "next_question": "",
            "summary": "用户已说清楚，帮我写一篇关于AI的文章",
        }, ensure_ascii=False)
        yield mock


@pytest.fixture
def mock_ollama_chat_satisfied():
    """Mock _ollama_chat 返回满意的 observe 结果。"""
    with patch("fanlang.ooda._ollama_chat") as mock:
        def side_effect(messages, model=None, stream=False, host=None):
            text = messages[-1]["content"] if messages else ""
            if "判断用户是否说清楚了" in text or "判断回答是否" in text:
                return json.dumps({
                    "clear": True,
                    "next_question": "",
                    "summary": "已清晰",
                    "satisfied": True,
                    "feedback": "OK",
                }, ensure_ascii=False)
            return json.dumps({"message": {"content": "AI模拟回答"}}, ensure_ascii=False)
        mock.side_effect = side_effect
        yield mock
