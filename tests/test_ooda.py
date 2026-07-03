# -*- coding: utf-8 -*-
"""
FanLang OODA 循环引擎测试
==========================
测试 OODA 类、CLARITY_RULES 完整性、orient/decide/act/observe。
"""
import json
import pytest
from unittest.mock import patch, Mock, MagicMock

from fanlang.ooda import (
    OODA, CLARITY_RULES, SYMBOL_TO_AGENT,
    _ollama_chat, DEFAULT_OLLAMA_HOST, DEFAULT_MODEL,
)
from fanlang.symbols import SINGLE_CHARS


# ============================================================
# CLARITY_RULES 完整性
# ============================================================

class TestClarityRulesCompleteness:
    """验证 CLARITY_RULES 覆盖所有 25 个符号。"""

    def test_all_symbols_have_rules(self):
        """每个单字符号都应有清晰度规则。"""
        for char in SINGLE_CHARS:
            assert char in CLARITY_RULES, f"{char} 缺少清晰度规则"

    def test_rules_count_equals_25(self):
        """CLARITY_RULES 应有 25 条规则。"""
        assert len(CLARITY_RULES) == 25

    def test_all_rules_are_lists_of_strings(self):
        """每条规则都是字符串列表。"""
        for char, rules in CLARITY_RULES.items():
            assert isinstance(rules, list), f"{char} 的规则不是 list"
            assert len(rules) >= 1, f"{char} 的规则列表为空"
            for r in rules:
                assert isinstance(r, str), f"{char} 的规则 {r} 不是字符串"

    def test_write_rules(self):
        rules = CLARITY_RULES["写"]
        assert "写什么类型" in rules
        assert "什么主题" in rules
        assert "多长" in rules

    def test_ask_rules(self):
        assert "问什么" in CLARITY_RULES["问"]

    def test_draw_rules(self):
        assert "画什么" in CLARITY_RULES["画"]
        assert "什么风格" in CLARITY_RULES["画"]

    def test_read_rules(self):
        assert "阅什么内容" in CLARITY_RULES["阅"]

    def test_stop_rules(self):
        assert "需要输出什么" in CLARITY_RULES["止"]


class TestSymbolToAgent:
    """验证 SYMBOL_TO_AGENT 覆盖所有 25 个符号。"""

    def test_all_symbols_have_agent(self):
        """每个单字符号都应有对应的智能体类型。"""
        for char in SINGLE_CHARS:
            assert char in SYMBOL_TO_AGENT, f"{char} 缺少智能体映射"

    def test_agent_names_meaningful(self):
        for char, agent in SYMBOL_TO_AGENT.items():
            assert "_agent" in agent, f"{char} 的智能体名 {agent} 不含 _agent"
            assert len(agent) > 5

    def test_write_agent(self):
        assert SYMBOL_TO_AGENT["写"] == "writing_agent"

    def test_ask_agent(self):
        assert SYMBOL_TO_AGENT["问"] == "qa_agent"

    def test_code_agent(self):
        assert SYMBOL_TO_AGENT["编"] == "coding_agent"


# ============================================================
# OODA 初始化
# ============================================================

class TestOODAInit:
    """测试 OODA 初始化。"""

    def test_default_init(self):
        ooda = OODA()
        assert ooda._agent_func is None
        assert ooda.max_iterations == 5
        assert ooda.model == DEFAULT_MODEL
        assert ooda._chat_func is None

    def test_custom_init(self):
        def agent_func(sym, inp):
            return "result"
        ooda = OODA(agent_func=agent_func, max_iterations=3, model="test-model")
        assert ooda._agent_func is agent_func
        assert ooda.max_iterations == 3
        assert ooda.model == "test-model"

    def test_with_chat_func(self):
        def chat_func(msgs, model):
            return "reply"
        ooda = OODA(chat_func=chat_func)
        assert ooda._chat_func is chat_func


# ============================================================
# orient() 阶段
# ============================================================

class TestOrient:
    """测试 orient() 阶段。"""

    def test_orient_no_symbol(self):
        """没有符号时不需要澄清。"""
        ooda = OODA()
        result = ooda.orient("随便写点什么")
        assert result["need_clarify"] is False
        assert result["summary"] == "随便写点什么"

    def test_orient_short_input_triggers_clarify(self):
        """短输入（<8 字符）触发自动追问。"""
        ooda = OODA()
        result = ooda.orient("写", "写")
        assert result["need_clarify"] is True
        assert "?" in result["question"]

    def test_orient_short_input_uses_first_rule(self):
        ooda = OODA()
        result = ooda.orient("写", "写")
        assert result["question"] == "写什么类型?"

    def test_orient_short_input_other_symbol(self):
        ooda = OODA()
        result = ooda.orient("改", "改")
        assert result["question"] == "改什么?"

    def test_orient_normal_input_calls_llm(self):
        """正常输入调用 LLM 判断。"""
        ooda = OODA()

        with patch.object(ooda, "_chat") as mock_chat:
            mock_chat.return_value = json.dumps({
                "clear": True,
                "next_question": "",
                "summary": "用户要写一篇AI文章",
            }, ensure_ascii=False)

            result = ooda.orient("帮我写一篇关于AI的文章", "写")
            assert result["need_clarify"] is False
            assert "AI文章" in result["summary"]

    def test_orient_needs_clarify(self):
        ooda = OODA()

        with patch.object(ooda, "_chat") as mock_chat:
            mock_chat.return_value = json.dumps({
                "clear": False,
                "next_question": "你想写什么类型的文章?",
            }, ensure_ascii=False)

            result = ooda.orient("帮我写点东西", "写")
            assert result["need_clarify"] is True
            assert "类型" in result["question"]

    def test_orient_json_parse_error_fallback(self):
        """JSON 解析失败时不澄清。"""
        ooda = OODA()

        with patch.object(ooda, "_chat") as mock_chat:
            mock_chat.return_value = "不是JSON"

            result = ooda.orient("帮我写一篇关于AI的科普文章", "写")
            assert result["need_clarify"] is False
            assert "AI" in result["summary"]

    def test_orient_error_response(self):
        """LLM 返回错误时不澄清。"""
        ooda = OODA()

        with patch.object(ooda, "_chat") as mock_chat:
            mock_chat.return_value = '{"error": "ollama_not_running"}'

            result = ooda.orient("帮我写一篇关于AI的科普文章", "写")
            assert result["need_clarify"] is False

    def test_orient_nonexistent_symbol(self):
        """不存在的符号不澄清。"""
        ooda = OODA()
        result = ooda.orient("随便", "X")
        assert result["need_clarify"] is False


# ============================================================
# decide() 阶段
# ============================================================

class TestDecide:
    """测试 decide() 方法。"""

    def test_decide_with_valid_symbol(self):
        ooda = OODA()
        result = ooda.decide("帮我写文章", "写")
        assert result["agent"] == "writing_agent"
        assert result["symbol_char"] == "写"
        assert result["symbol_name"] == "写作"
        assert result["user_input"] == "帮我写文章"

    def test_decide_without_symbol(self):
        ooda = OODA()
        result = ooda.decide("你好")
        assert result["agent"] == "general_agent"
        assert result["symbol_char"] == "问"
        assert result["symbol_name"] == "问答"

    def test_decide_agent_mapping(self):
        """验证多个符号的智能体映射。"""
        ooda = OODA()
        tests = [
            ("写", "writing_agent"),
            ("改", "rewriting_agent"),
            ("翻", "translation_agent"),
            ("问", "qa_agent"),
            ("画", "drawing_agent"),
            ("编", "coding_agent"),
            ("查", "search_agent"),
            ("算", "calculate_agent"),
            ("记", "memory_agent"),
            ("定", "schedule_agent"),
        ]
        for char, expected_agent in tests:
            result = ooda.decide("test", char)
            assert result["agent"] == expected_agent, f"{char} 应映射到 {expected_agent}"


# ============================================================
# act() 阶段
# ============================================================

class TestAct:
    """测试 act() 方法。"""

    def test_act_with_agent_func(self):
        """使用自定义 agent_func 执行。"""
        def agent_func(sym_char, user_input):
            return f"执行符号 {sym_char}: {user_input}"
        ooda = OODA(agent_func=agent_func)
        result = ooda.act({"symbol_char": "写", "user_input": "写文章"})
        assert "执行符号 写" in result

    def test_act_default_calls_ollama(self):
        """默认通过 self._chat 调用 LLM。"""
        ooda = OODA()
        with patch.object(ooda, "_chat") as mock:
            mock.return_value = "AI生成的文本"
            result = ooda.act({"symbol_char": "写", "user_input": "写文章"})
            assert result == "AI生成的文本"
            mock.assert_called_once()

    def test_act_nonexistent_symbol(self):
        """不存在的符号使用默认提示词。"""
        ooda = OODA()
        with patch.object(ooda, "_chat") as mock:
            mock.return_value = "回复"
            result = ooda.act({"symbol_char": "X", "user_input": "hello"})
            assert result == "回复"

    def test_act_uses_prompt_template(self):
        """使用符号的 prompt_template 作为 system prompt。"""
        ooda = OODA()
        with patch.object(ooda, "_chat") as mock:
            mock.return_value = "回复"
            ooda.act({"symbol_char": "写", "user_input": "写文章"})
            args = mock.call_args[0][0]
            system_msg = args[0]
            assert system_msg["role"] == "system"
            assert "写作助手" in system_msg["content"]


# ============================================================
# observe() 阶段
# ============================================================

class TestObserve:
    """测试 observe() 方法。"""

    def test_observe_satisfied(self):
        ooda = OODA()
        with patch.object(ooda, "_chat") as mock_chat:
            mock_chat.return_value = json.dumps({
                "satisfied": True,
                "feedback": "OK",
            }, ensure_ascii=False)

            result = ooda.observe("写文章", "这是一篇好文章")
            assert result["satisfied"] is True
            assert result["feedback"] == "OK"

    def test_observe_not_satisfied(self):
        ooda = OODA()
        with patch.object(ooda, "_chat") as mock_chat:
            mock_chat.return_value = json.dumps({
                "satisfied": False,
                "feedback": "需要更详细的内容",
            }, ensure_ascii=False)

            result = ooda.observe("写文章", "太短了")
            assert result["satisfied"] is False
            assert "详细" in result["feedback"]

    def test_observe_json_error_fallback(self):
        """JSON 解析失败时默认满意。"""
        ooda = OODA()
        with patch.object(ooda, "_chat") as mock_chat:
            mock_chat.return_value = "无效JSON"
            result = ooda.observe("写文章", "内容")
            assert result["satisfied"] is True
            assert result["feedback"] == ""


# ============================================================
# run() 完整循环
# ============================================================

class TestRun:
    """测试完整的 run() 循环。"""

    def test_run_clarify_early_exit(self):
        """Orient 阶段需要澄清时提前返回。"""
        ooda = OODA()

        # 短输入触发澄清，不调用 LLM
        result = ooda.run("写", "写")
        assert result["status"] == "clarify"
        assert result["result"] is None
        assert result["question"] is not None
        assert result["iterations"] == 0

    def test_run_successful(self):
        """完整的 OODA 循环。"""
        ooda = OODA()

        with patch.object(ooda, "_chat") as mock_chat:
            def side_effect(messages):
                text = messages[-1]["content"]
                if "判断用户是否说清楚了" in text:
                    return json.dumps({
                        "clear": True,
                        "summary": "写一篇AI文章",
                    }, ensure_ascii=False)
                if "判断回答是否满足了" in text:
                    return json.dumps({
                        "satisfied": True,
                        "feedback": "OK",
                    }, ensure_ascii=False)
                return "这是一篇关于AI的文章"
            mock_chat.side_effect = side_effect

            result = ooda.run("帮我写一篇关于AI的文章", "写")
            assert result["status"] == "done"
            assert result["satisfied"] is True
            assert result["iterations"] >= 1

    def test_run_no_symbol_no_clarify(self):
        """没有符号时跳过澄清。"""
        ooda = OODA()
        with patch.object(ooda, "_chat") as mock_chat:
            mock_chat.return_value = json.dumps({
                "satisfied": True,
                "feedback": "OK",
            }, ensure_ascii=False)
            result = ooda.run("你好")
            assert result["status"] == "done"

    def test_run_max_iterations_exceeded(self):
        """超出最大循环次数。"""
        ooda = OODA(max_iterations=2)

        def chat_side_effect(messages):
            text = messages[-1]["content"]
            if "判断用户是否说清楚了" in text:
                return json.dumps({
                    "clear": True,
                    "summary": "需要写一篇详细的技术文章",
                }, ensure_ascii=False)
            if "判断回答是否满足了" in text:
                return json.dumps({
                    "satisfied": False,
                    "feedback": "需要改进",
                }, ensure_ascii=False)
            return "AI生成的回复"
        ooda._chat = chat_side_effect

        result = ooda.run("需要写一篇详细的技术文章", "写")
        assert result["status"] == "done"
        assert result["satisfied"] is False
        assert result["iterations"] == 2


# ============================================================
# _ollama_chat 函数
# ============================================================

class TestOllamaChat:
    """测试 _ollama_chat() 函数。"""

    def test_successful_call(self):
        """正常调用返回内容。"""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = Mock()
            mock_resp.read.return_value = json.dumps({
                "message": {"content": "你好"}
            }).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            result = _ollama_chat([{"role": "user", "content": "hi"}])
            assert result == "你好"

    def test_connection_error_returns_json_error(self):
        """连接错误返回错误 JSON。"""
        with patch("urllib.request.urlopen") as mock_urlopen:
            import urllib.error
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

            result = _ollama_chat([{"role": "user", "content": "hi"}])
            assert "error" in result
            assert "ollama_not_running" in result


# ============================================================
# Edge Cases
# ============================================================

class TestOODAEdgeCases:
    """OODA 边界情况。"""

    def test_orient_with_zero_length_input(self):
        """空输入使用短输入规则触发澄清。"""
        ooda = OODA()
        result = ooda.orient("", "写")
        assert result["need_clarify"] is True

    def test_decide_with_empty_input(self):
        ooda = OODA()
        result = ooda.decide("")
        assert result["user_input"] == ""

    def test_act_with_no_agent_func_and_no_symbol(self):
        """没有 agent_func 且符号不存在时使用默认提示词。"""
        ooda = OODA()
        with patch.object(ooda, "_chat") as mock:
            mock.return_value = "回复"
            result = ooda.act({"symbol_char": None, "user_input": "hello"})
            assert result == "回复"

    def test_run_with_multiple_iterations(self):
        """多次观察不满意直到最大迭代。"""
        ooda = OODA(max_iterations=3)

        def chat_side_effect(messages):
            text = messages[-1]["content"]
            if "判断用户是否说清楚了" in text:
                return json.dumps({"clear": True, "summary": "需要写一篇详细的技术文章"}, ensure_ascii=False)
            if "判断回答是否满足了" in text:
                return json.dumps({"satisfied": False, "feedback": "改"}, ensure_ascii=False)
            return "第N次回复"

        ooda._chat = chat_side_effect
        with patch("fanlang.ooda._ollama_chat") as mock_ollama:
            mock_ollama.return_value = "回复"
            result = ooda.run("需要写一篇详细的技术文章", "写")
            assert result["iterations"] == 3
            assert result["satisfied"] is False
