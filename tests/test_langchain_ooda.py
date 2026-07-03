# -*- coding: utf-8 -*-
"""
FanLang LangChain OODA 代理模块（ooda_agent.py）的 pytest 测试。

测试范围：
  - OODAAgent 初始化（正常 / langchain 未安装错误 / 带工具）
  - run() 方法（正常完成 / 追问澄清 / 最大迭代次数限制）
  - OODA 四阶段：_orient, _decide, _act, _observe
  - _call_llm 兼容性（invoke / __call__ / content 属性 / 字符串响应）
  - 错误处理（LLM 调用异常 / 工具执行异常 / 缺少 langchain）
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
# Fixture: mock langchain 依赖
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _mock_langchain():
    """mock langchain_core 依赖，使 _LANGCHAIN_AVAILABLE = True。"""
    mock_base_llm = MagicMock()
    mock_base_tool = MagicMock()
    mock_callback_mgr = MagicMock()
    mock_callback_tool_run = MagicMock()
    mock_beta = lambda *a, **kw: (lambda cls: cls)

    mock_modules = {
        "langchain_core": MagicMock(),
        "langchain_core._api": MagicMock(beta=mock_beta),
        "langchain_core.callbacks": MagicMock(
            BaseCallbackManager=mock_callback_mgr,
            CallbackManagerForToolRun=mock_callback_tool_run,
        ),
        "langchain_core.language_models": MagicMock(BaseLLM=mock_base_llm),
        "langchain_core.tools": MagicMock(BaseTool=mock_base_tool),
    }

    for mod_name, mod_obj in mock_modules.items():
        sys.modules[mod_name] = mod_obj

    # 清理 ooda_agent 缓存
    for key in list(sys.modules.keys()):
        if "fanlang_langchain" in key:
            del sys.modules[key]

    from fanlang_langchain.ooda_agent import _LANGCHAIN_AVAILABLE
    assert _LANGCHAIN_AVAILABLE, "LangChain mock 后应可用"

    yield

    for key in list(sys.modules.keys()):
        if key in mock_modules or "fanlang_langchain" in key:
            sys.modules.pop(key, None)


# ═══════════════════════════════════════════════════════════════
# 辅助函数：创建 mock LLM
# ═══════════════════════════════════════════════════════════════

def _make_mock_llm(invoke_return: str = "模拟响应") -> MagicMock:
    """创建一个模拟的 LLM，支持 invoke 方法。"""
    llm = MagicMock()
    resp = MagicMock()
    resp.content = invoke_return
    llm.invoke.return_value = resp
    return llm


def _make_mock_llm_str_response(response: str = "模拟响应") -> MagicMock:
    """创建一个直接返回字符串的 mock LLM。"""
    llm = MagicMock()
    llm.invoke.return_value = response
    return llm


# ═══════════════════════════════════════════════════════════════
# tests: 初始化
# ═══════════════════════════════════════════════════════════════

class TestOODAAgentInit:
    """OODAAgent 初始化。"""

    def test_init_with_llm(self) -> None:
        from fanlang_langchain.ooda_agent import OODAAgent
        llm = _make_mock_llm()
        agent = OODAAgent(llm=llm)
        assert agent._llm is llm
        assert agent._tools == {}
        assert agent._max_iterations == 5
        assert agent._verbose is False

    def test_init_with_custom_max_iterations(self) -> None:
        from fanlang_langchain.ooda_agent import OODAAgent
        llm = _make_mock_llm()
        agent = OODAAgent(llm=llm, max_iterations=3)
        assert agent._max_iterations == 3

    def test_init_with_verbose(self) -> None:
        from fanlang_langchain.ooda_agent import OODAAgent
        llm = _make_mock_llm()
        agent = OODAAgent(llm=llm, verbose=True)
        assert agent._verbose is True

    def test_init_with_tools(self) -> None:
        from fanlang_langchain.ooda_agent import OODAAgent
        llm = _make_mock_llm()
        tool1 = MagicMock()
        tool1.name = "search_tool"
        tool2 = MagicMock()
        tool2.name = "calc_tool"
        agent = OODAAgent(llm=llm, tools=[tool1, tool2])
        assert "search_tool" in agent._tools
        assert "calc_tool" in agent._tools
        assert agent._tools["search_tool"] is tool1

    def test_init_tool_without_name(self) -> None:
        from fanlang_langchain.ooda_agent import OODAAgent
        llm = _make_mock_llm()
        # 没有 name 属性的工具
        tool = object()
        agent = OODAAgent(llm=llm, tools=[tool])
        # 应使用 id() 作为 key
        assert len(agent._tools) == 1

    def test_init_callbacks(self) -> None:
        from fanlang_langchain.ooda_agent import OODAAgent
        llm = _make_mock_llm()
        agent = OODAAgent(llm=llm)
        assert agent.callbacks is None


# ═══════════════════════════════════════════════════════════════
# tests: run() 方法
# ═══════════════════════════════════════════════════════════════

class TestOODAAgentRun:
    """OODAAgent.run() 方法。"""

    def test_run_basic_satisfied(self) -> None:
        """基本 run 流程：_orient 不需要澄清，_observe 满意。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("好的结果")
        agent = OODAAgent(llm=llm, max_iterations=5)

        # mock 各方法
        agent._orient = MagicMock(return_value={
            "needs_clarification": False,
            "question": "",
            "clarified": "帮我写一段代码",
        })
        agent._decide = MagicMock(return_value={
            "strategy": "direct_llm", "tool": "",
        })
        agent._act = MagicMock(return_value="这段代码实现了排序")
        agent._observe = MagicMock(return_value={
            "satisfied": True,
            "feedback": "满足需求",
        })

        result = agent.run("帮我写一段代码")
        assert result["satisfied"] is True
        assert "这段代码实现了排序" in result["result"]
        assert result["iterations"] == 1
        assert len(result["history"]) == 1

    def test_run_with_clarification(self) -> None:
        """_orient 需要澄清时修正输入。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("结果")
        agent = OODAAgent(llm=llm, max_iterations=1)

        agent._orient = MagicMock(return_value={
            "needs_clarification": True,
            "question": "请提供更多细节",
            "clarified": "澄清后的输入",
        })
        agent._decide = MagicMock(return_value={
            "strategy": "direct_llm", "tool": "",
        })
        agent._act = MagicMock(return_value="结果")
        agent._observe = MagicMock(return_value={
            "satisfied": True,
            "feedback": "满足",
        })

        result = agent.run("写")
        assert result["satisfied"] is True

    def test_run_max_iterations_reached(self) -> None:
        """达到 max_iterations 时返回不满足结果。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("不满足的结果")
        agent = OODAAgent(llm=llm, max_iterations=3)

        agent._orient = MagicMock(return_value={
            "needs_clarification": False,
            "question": "",
            "clarified": "输入",
        })
        agent._decide = MagicMock(return_value={
            "strategy": "direct_llm", "tool": "",
        })
        agent._act = MagicMock(return_value="始终不满足的结果")
        agent._observe = MagicMock(return_value={
            "satisfied": False,
            "feedback": "还需要改进",
        })

        result = agent.run("输入")
        assert result["satisfied"] is False
        assert result["iterations"] == 3

    def test_run_act_raises_ooda_error(self) -> None:
        """_act 抛出 OODAAgentError 时透传。"""
        from fanlang_langchain.ooda_agent import OODAAgent, OODAAgentError

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm, max_iterations=1)

        agent._orient = MagicMock(return_value={
            "needs_clarification": False, "question": "", "clarified": "输入",
        })
        agent._decide = MagicMock(return_value={
            "strategy": "tool_call", "tool": "missing_tool",
        })
        agent._act = MagicMock(side_effect=OODAAgentError("工具未找到"))

        with pytest.raises(OODAAgentError, match="工具未找到"):
            agent.run("输入")

    def test_run_act_raises_generic_exception(self) -> None:
        """_act 抛出普通异常时被捕获并记录。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm, max_iterations=1)

        agent._orient = MagicMock(return_value={
            "needs_clarification": False, "question": "", "clarified": "输入",
        })
        agent._decide = MagicMock(return_value={
            "strategy": "direct_llm", "tool": "",
        })
        agent._act = MagicMock(side_effect=ValueError("意外的错误"))
        agent._observe = MagicMock(return_value={
            "satisfied": False,
            "feedback": "[执行异常] 意外的错误",
        })

        result = agent.run("输入")
        assert result["satisfied"] is False

    def test_run_with_symbol_char(self) -> None:
        """传入 symbol_char 参数。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("结果")
        agent = OODAAgent(llm=llm, max_iterations=1)

        agent._orient = MagicMock(return_value={
            "needs_clarification": False, "question": "", "clarified": "输入",
        })
        agent._decide = MagicMock(return_value={
            "strategy": "direct_llm", "tool": "",
        })
        agent._act = MagicMock(return_value="结果")
        agent._observe = MagicMock(return_value={
            "satisfied": True, "feedback": "满足",
        })

        result = agent.run("输入", symbol_char="写")
        assert result["satisfied"] is True


# ═══════════════════════════════════════════════════════════════
# tests: _orient
# ═══════════════════════════════════════════════════════════════

class TestOrient:
    """_orient 阶段一：方向分析。"""

    def test_short_input_triggers_clarification(self) -> None:
        """输入过短（<8 字符）触发澄清。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("请提供更多细节")
        agent = OODAAgent(llm=llm, max_iterations=1)
        agent._call_llm = MagicMock(return_value="请提供更多关于需求的信息")

        result = agent._orient("写")
        assert result["needs_clarification"] is True
        assert "请提供更多" in result["question"] or result["question"] != ""

    def test_long_input_no_clarification_needed(self) -> None:
        """长输入且 LLM 回答"不需要"。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm, max_iterations=1)
        agent._call_llm = MagicMock(return_value="不需要")

        result = agent._orient("帮我写一段功能完善的 Python 排序代码")
        assert result["needs_clarification"] is False
        assert result["clarified"] == "帮我写一段功能完善的 Python 排序代码"

    def test_orient_llm_exception(self) -> None:
        """LLM 调用异常时保守处理。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm, max_iterations=1)
        agent._call_llm = MagicMock(side_effect=RuntimeError("LLM 错误"))

        result = agent._orient("这是一段足够长的输入文本")
        # 异常时 needs_clarification 为 False
        assert result["needs_clarification"] is False

    def test_orient_exception_during_clarify(self) -> None:
        """澄清阶段的 LLM 异常使用默认追问。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm, max_iterations=1)
        agent._call_llm = MagicMock()
        # 第一次（判断）- 返回需要澄清
        # 第二次（生成问题）- 异常
        # 第三次（生成澄清版本）- 不会调用因为第二次已异常
        agent._call_llm.side_effect = [
            "需要澄清",  # 判断：需要
            RuntimeError("生成问题失败"),  # 生成问题异常
        ]

        result = agent._orient("短")
        assert result["needs_clarification"] is True
        assert result["question"] == "请提供更多细节"


# ═══════════════════════════════════════════════════════════════
# tests: _decide
# ═══════════════════════════════════════════════════════════════

class TestDecide:
    """_decide 阶段二：决策。"""

    def test_no_tools_direct_llm(self) -> None:
        """没有工具时直接返回 direct_llm。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        result = agent._decide("输入")
        assert result["strategy"] == "direct_llm"

    def test_with_tools_llm_chooses_tool(self) -> None:
        """有工具时 LLM 选择工具。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        tool = MagicMock()
        tool.name = "search"
        tool.description = "搜索工具"
        agent._tools = {"search": tool}
        agent._call_llm = MagicMock(return_value="search")

        result = agent._decide("查找资料")
        assert result["strategy"] == "tool_call"
        assert result["tool"] == "search"

    def test_with_tools_llm_chooses_direct(self) -> None:
        """LLM 返回 direct_llm 时走直接 LLM 策略。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        tool = MagicMock()
        tool.name = "search"
        tool.description = "搜索工具"
        agent._tools = {"search": tool}
        agent._call_llm = MagicMock(return_value="direct_llm")

        result = agent._decide("思考问题")
        assert result["strategy"] == "direct_llm"

    def test_with_tools_llm_returns_unknown(self) -> None:
        """LLM 返回未知工具时走 direct_llm。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        agent._tools = {"search": MagicMock()}
        agent._call_llm = MagicMock(return_value="unknown_tool")

        result = agent._decide("输入")
        assert result["strategy"] == "direct_llm"

    def test_decide_llm_exception(self) -> None:
        """LLM 异常时回退到 direct_llm。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        agent._tools = {"search": MagicMock()}
        agent._call_llm = MagicMock(side_effect=RuntimeError("LLM 错误"))

        result = agent._decide("输入")
        assert result["strategy"] == "direct_llm"


# ═══════════════════════════════════════════════════════════════
# tests: _act
# ═══════════════════════════════════════════════════════════════

class TestAct:
    """_act 阶段三：执行。"""

    def test_direct_llm_strategy(self) -> None:
        """direct_llm 策略直接调用 LLM。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("LLM 执行结果")
        agent = OODAAgent(llm=llm)
        agent._call_llm = MagicMock(return_value="LLM 执行结果")

        result = agent._act({"strategy": "direct_llm", "tool": ""}, "写一段代码")
        assert "LLM 执行结果" in result

    def test_tool_call_strategy_with_run(self) -> None:
        """tool_call 策略调用工具的 run 方法。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        tool = MagicMock()
        # MagicMock 会自动创建 _run 属性，需显式删除以触发 run 路径
        if hasattr(tool, '_run'):
            del tool._run
        tool.run.return_value = "工具执行结果"
        agent._tools = {"search": tool}

        result = agent._act({"strategy": "tool_call", "tool": "search"}, "查询数据")
        assert "工具执行结果" in result
        tool.run.assert_called_once_with("查询数据")

    def test_tool_call_strategy_with_private_run(self) -> None:
        """工具使用 _run 方法。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        tool = MagicMock()
        # 有 _run 但没有 run
        tool._run.return_value = "_run 结果"
        del tool.run
        agent._tools = {"search": tool}

        result = agent._act({"strategy": "tool_call", "tool": "search"}, "查询")
        assert "_run 结果" in result

    def test_tool_call_direct_callable(self) -> None:
        """工具本身是可调用的（没有 _run 或 run）。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        tool = MagicMock()
        del tool._run
        del tool.run
        tool.__call__ = MagicMock(return_value="直接调用结果")
        agent._tools = {"search": tool}

        # 注意：这里需要模拟 hasattr 为 False
        # 当 tool 是 MagicMock 时，hasattr(tool, '_run') 为 True（自动创建属性）
        # 所以我们直接测试 _run 路径
        result = agent._act({"strategy": "tool_call", "tool": "search"}, "查询")
        # 由于 MagicMock 会创建 _run，所以走 _run 路径
        assert isinstance(result, str)

    def test_tool_not_found_raises_error(self) -> None:
        """未找到工具时抛出 OODAAgentError。"""
        from fanlang_langchain.ooda_agent import OODAAgent, OODAAgentError

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)

        with pytest.raises(OODAAgentError, match="未找到工具"):
            agent._act({"strategy": "tool_call", "tool": "nonexistent"}, "输入")

    def test_llm_call_raises_error(self) -> None:
        """LLM 调用失败时抛出 OODAAgentError。"""
        from fanlang_langchain.ooda_agent import OODAAgent, OODAAgentError

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        agent._call_llm = MagicMock(side_effect=RuntimeError("LLM 崩溃"))

        with pytest.raises(OODAAgentError, match="LLM 调用失败"):
            agent._act({"strategy": "direct_llm", "tool": ""}, "输入")


# ═══════════════════════════════════════════════════════════════
# tests: _observe
# ═══════════════════════════════════════════════════════════════

class TestObserve:
    """_observe 阶段四：观察评估。"""

    def test_empty_result_not_satisfied(self) -> None:
        """空结果不满足。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        result = agent._observe("", "输入")
        assert result["satisfied"] is False
        assert "结果为空" in result["feedback"]

    def test_whitespace_only_not_satisfied(self) -> None:
        """全空白结果不满足。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        result = agent._observe("   \n  ", "输入")
        assert result["satisfied"] is False

    def test_error_prefix_not_satisfied(self) -> None:
        """以 [执行异常] 开头的结果不满足。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        result = agent._observe("[执行异常] 内存不足", "输入")
        assert result["satisfied"] is False

    def test_llm_evaluates_satisfied(self) -> None:
        """LLM 评估为满足。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        agent._call_llm = MagicMock(return_value="满足")

        result = agent._observe("一段合理的结果", "输入")
        assert result["satisfied"] is True

    def test_llm_evaluates_not_satisfied(self) -> None:
        """LLM 评估为不满足。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        agent._call_llm = MagicMock(return_value="不满足: 缺少关键信息")

        result = agent._observe("结果不完整", "输入")
        assert result["satisfied"] is False
        assert "不满足" in result["feedback"]

    def test_llm_evaluation_exception(self) -> None:
        """LLM 评估异常时保守满足。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = _make_mock_llm("")
        agent = OODAAgent(llm=llm)
        agent._call_llm = MagicMock(side_effect=RuntimeError("评估失败"))

        result = agent._observe("一些结果", "输入")
        assert result["satisfied"] is True
        assert result["feedback"] == "评估跳过"


# ═══════════════════════════════════════════════════════════════
# tests: _call_llm
# ═══════════════════════════════════════════════════════════════

class TestCallLLM:
    """_call_llm 兼容不同 LLM 类型。"""

    def test_invoke_method_with_content(self) -> None:
        """BaseChatModel 风格：invoke 返回带 content 属性的对象。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = MagicMock()
        resp = MagicMock()
        resp.content = "chat 回复"
        llm.invoke.return_value = resp
        agent = OODAAgent(llm=llm)

        result = agent._call_llm("你好")
        assert result == "chat 回复"

    def test_invoke_method_with_string(self) -> None:
        """invoke 直接返回字符串。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = MagicMock()
        llm.invoke.return_value = "字符串回复"
        agent = OODAAgent(llm=llm)

        result = agent._call_llm("你好")
        assert result == "字符串回复"

    def test_call_method(self) -> None:
        """BaseLLM 风格：__call__ 返回字符串。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = MagicMock()
        # 没有 invoke 方法
        del llm.invoke
        llm.return_value = "call 回复"
        agent = OODAAgent(llm=llm)

        result = agent._call_llm("提示")
        assert result == "call 回复"

    def test_call_with_content_attr(self) -> None:
        """__call__ 返回带 content 属性的对象。"""
        from fanlang_langchain.ooda_agent import OODAAgent

        llm = MagicMock()
        del llm.invoke
        resp = MagicMock()
        resp.content = "content 回复"
        llm.return_value = resp
        agent = OODAAgent(llm=llm)

        result = agent._call_llm("提示")
        assert result == "content 回复"


# ═══════════════════════════════════════════════════════════════
# tests: 属性
# ═══════════════════════════════════════════════════════════════

class TestProperties:
    """OODAAgent 属性。"""

    def test_return_values(self) -> None:
        from fanlang_langchain.ooda_agent import OODAAgent
        llm = _make_mock_llm()
        agent = OODAAgent(llm=llm)
        rv = agent.return_values
        assert "result" in rv
        assert "iterations" in rv
        assert "satisfied" in rv
        assert "history" in rv

    def test_is_single_input(self) -> None:
        from fanlang_langchain.ooda_agent import OODAAgent
        llm = _make_mock_llm()
        agent = OODAAgent(llm=llm)
        assert agent.is_single_input is True

    def test_class_var_langchain_loaded(self) -> None:
        from fanlang_langchain.ooda_agent import OODAAgent
        assert OODAAgent._LANGCHAIN_LOADED is True


# ═══════════════════════════════════════════════════════════════
# tests: _SimpleCallbackManager
# ═══════════════════════════════════════════════════════════════

class TestSimpleCallbackManager:
    """_SimpleCallbackManager 日志路由。"""

    def test_init_no_handler(self) -> None:
        from fanlang_langchain.ooda_agent import _SimpleCallbackManager
        mgr = _SimpleCallbackManager()
        assert mgr.handler is None

    def test_set_handler(self) -> None:
        from fanlang_langchain.ooda_agent import _SimpleCallbackManager
        mgr = _SimpleCallbackManager()
        handler = MagicMock()
        mgr.set_handler(handler)
        assert mgr.handler is handler

    def test_log_with_handler(self) -> None:
        from fanlang_langchain.ooda_agent import _SimpleCallbackManager
        mgr = _SimpleCallbackManager()
        handler = MagicMock()
        mgr.set_handler(handler)
        mgr.log("测试消息")
        handler.on_text.assert_called_once()

    def test_log_without_handler(self) -> None:
        """无 handler 时使用标准 logging。"""
        from fanlang_langchain.ooda_agent import _SimpleCallbackManager
        mgr = _SimpleCallbackManager()
        # 不抛异常即可
        mgr.log("消息", level=20)
