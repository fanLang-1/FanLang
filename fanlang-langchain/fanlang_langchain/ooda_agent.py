"""
OODA 智能代理（OODAAgent）。

基于 OODA (Observe-Orient-Decide-Act) 循环模型的 LangChain 集成代理。
可自动分析用户输入、选择合适的工具/策略、执行操作并评估结果。
"""

from __future__ import annotations

import logging
from typing import Any, Callable, ClassVar, Dict, List, Optional, Union

# --- LangChain 优雅降级 ---
try:
    from langchain_core._api import beta
    from langchain_core.callbacks import (
        BaseCallbackManager,
        CallbackManagerForToolRun,
    )
    from langchain_core.language_models import BaseLLM
    from langchain_core.tools import BaseTool

    _LANGCHAIN_AVAILABLE = True
except ImportError:  # pragma: no cover
    _LANGCHAIN_AVAILABLE = False

    # 提供占位类型以便类型提示正常工作
    BaseLLM = Any  # type: ignore[misc,assignment]
    BaseTool = Any  # type: ignore[misc,assignment]
    BaseCallbackManager = Any  # type: ignore[misc,assignment]
    CallbackManagerForToolRun = Any  # type: ignore[misc,assignment]

    def beta(*args: Any, **kwargs: Any) -> Callable[[Any], Any]:  # type: ignore[no-redef]
        """占位装饰器。"""
        return lambda cls: cls


# --- 标签定义 ---
_TAG_OBSERVE = "[察]"
_TAG_ORIENT = "[问]"
_TAG_DECIDE = "[策]"
_TAG_ACT = "[写]"
_TAG_RETRY = "[改]"
_TAG_DONE = "[成]"
_TAG_ERROR = "[错]"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 异常定义
# ---------------------------------------------------------------------------

class OODAAgentError(Exception):
    """OODA 代理运行时异常。"""


class LangChainNotInstalledError(ImportError):
    """LangChain 未安装时抛出的异常。

    请执行: pip install langchain
    """


# ---------------------------------------------------------------------------
# CallbackManager 适配器
# ---------------------------------------------------------------------------

class _SimpleCallbackManager:
    """轻量级 CallbackManager 包装器，同时支持 LangChain 原生与内置实现。

    当 LangChain 可用时，通过 set_handler 将日志输出委托给
    BaseCallbackManager；否则回退到标准 Python logging。
    """

    def __init__(self) -> None:
        self._handler: Optional[BaseCallbackManager] = None

    @property
    def handler(self) -> Optional[BaseCallbackManager]:
        """当前注册的 CallbackManager handler。"""
        return self._handler

    def set_handler(self, handler: Optional[BaseCallbackManager]) -> None:
        """设置 LangChain CallbackManager。

        Args:
            handler: LangChain BaseCallbackManager 实例，或 None 以清除。
        """
        self._handler = handler

    def log(self, message: str, level: int = logging.INFO) -> None:
        """输出日志消息。

        Args:
            message: 日志内容。
            level: 日志级别。
        """
        if self._handler and _LANGCHAIN_AVAILABLE:
            try:
                self._handler.on_text(message, run_id=None)
            except Exception:
                logger.log(level, message)
        else:
            logger.log(level, message)


# ---------------------------------------------------------------------------
# OODAAgent
# ---------------------------------------------------------------------------

class OODAAgent:
    """基于 OODA 循环的 LangChain 智能代理。

    OODA 循环四个阶段:
        1. Orient (方向):  分析用户输入，判断是否需要追问澄清
        2. Decide  (决策):  选择合适的工具或策略
        3. Act     (执行):  调用 LLM 或工具执行任务
        4. Observe (观察):  评估结果，决定是否进入新一轮循环

    Usage::

        from langchain.chat_models import ChatOpenAI
        from fanlang_langchain import OODAAgent

        llm = ChatOpenAI(model="gpt-4o")
        agent = OODAAgent(llm=llm, max_iterations=5)
        result = agent.run("帮我写一段 Python 排序代码")
    """

    # ------------------------------------------------------------------
    # 类属性
    # ------------------------------------------------------------------

    _LANGCHAIN_LOADED: ClassVar[bool] = _LANGCHAIN_AVAILABLE

    # ------------------------------------------------------------------
    # 构造
    # ------------------------------------------------------------------

    def __init__(
        self,
        llm: Any,
        tools: Optional[List[Any]] = None,
        max_iterations: int = 5,
        verbose: bool = False,
    ) -> None:
        """初始化 OODAAgent。

        Args:
            llm: LangChain BaseLLM / BaseChatModel 实例。
            tools: 可选的 LangChain BaseTool 列表。
            max_iterations: OODA 循环的最大迭代次数，默认 5。
            verbose: 是否在标准输出打印详细日志。

        Raises:
            LangChainNotInstalledError: 当 langchain 包不可用时抛出。
        """
        if not _LANGCHAIN_AVAILABLE:
            raise LangChainNotInstalledError(
                "langchain 未安装。请执行: pip install langchain"
            )

        self._llm = llm
        self._tools: Dict[str, Any] = {}
        self._max_iterations = max_iterations
        self._verbose = verbose

        # 构建工具索引
        if tools:
            for tool in tools:
                name = getattr(tool, "name", str(id(tool)))
                self._tools[name] = tool

        # 回调管理
        self._callback = _SimpleCallbackManager()
        self.callbacks: Optional[BaseCallbackManager] = None

        # 符号字符（可由 run() 传入覆盖）
        self._symbol_char: Optional[str] = None

    # ------------------------------------------------------------------
    # 对外 API
    # ------------------------------------------------------------------

    def run(
        self,
        user_input: str,
        symbol_char: Optional[str] = None,
    ) -> Dict[str, Any]:
        """执行 OODA 循环，处理用户输入。

        Args:
            user_input: 用户输入文本。
            symbol_char: 可选的符号字符，用于自定义阶段标签前缀。

        Returns:
            dict，包含以下键:
                - result (str): 最终输出内容
                - iterations (int): 实际执行的迭代次数
                - satisfied (bool): 是否正常结束（未超限）
                - history (list[dict]): 历次迭代记录

        Raises:
            OODAAgentError: LLM 调用失败或工具执行异常时抛出。
        """
        self._symbol_char = symbol_char

        history: List[Dict[str, Any]] = []
        clarified_input = user_input

        # --- 第一阶段: Orient ---
        orient_result = self._orient(user_input)
        self._log(f"{_TAG_ORIENT} 分析用户输入...")

        if orient_result["needs_clarification"]:
            clarified_input = orient_result["clarified"]
            self._log(
                f"{_TAG_ORIENT} 追问: {orient_result['question']}"
                f" -> 澄清后: {clarified_input}"
            )

        # --- OODA 主循环 ---
        final_result = ""
        satisfied = False

        for iteration in range(1, self._max_iterations + 1):
            self._log(f"--- OODA 第 {iteration}/{self._max_iterations} 次循环 ---")

            # 阶段 2: Decide
            decision = self._decide(clarified_input)
            self._log(
                f"{_TAG_DECIDE} 决策: 策略={decision['strategy']}, "
                f"工具={decision.get('tool', '无')}"
            )

            # 阶段 3: Act
            try:
                result = self._act(decision, clarified_input)
                self._log(f"{_TAG_ACT} 执行完成")
            except OODAAgentError:
                raise
            except Exception as exc:
                self._log(f"{_TAG_ERROR} 执行异常: {exc}", level=logging.ERROR)
                result = f"[执行异常] {exc}"

            # 阶段 4: Observe
            observation = self._observe(result, clarified_input)
            self._log(
                f"{_TAG_OBSERVE} 评估: satisfied={observation['satisfied']}, "
                f"feedback={observation['feedback']}"
            )

            history.append({
                "iteration": iteration,
                "decision": decision,
                "result": result,
                "observation": observation,
            })

            if observation["satisfied"]:
                final_result = result
                satisfied = True
                self._log(f"{_TAG_DONE} OODA 循环完成")
                break

            # 不满足时，将反馈并入下一轮输入
            clarified_input = (
                f"上一轮结果不够满意（反馈: {observation['feedback']}），"
                f"请重新处理: {clarified_input}"
            )
        else:
            # 循环耗尽
            final_result = (
                f"[达到最大迭代次数 {self._max_iterations}] {result}"
            )
            self._log(f"{_TAG_ERROR} 达到最大迭代次数", level=logging.WARNING)

        return {
            "result": final_result,
            "iterations": len(history),
            "satisfied": satisfied,
            "history": history,
        }

    # ------------------------------------------------------------------
    # OODA 四阶段实现
    # ------------------------------------------------------------------

    def _orient(self, user_input: str) -> Dict[str, Any]:
        """OODA 阶段一: 方向分析。

        分析用户输入是否清晰完整。如有歧义或不完整，生成追问问题
        并使用 LLM 自动澄清。

        Args:
            user_input: 原始用户输入。

        Returns:
            dict:
                - needs_clarification (bool): 是否需要澄清
                - question (str): 面向用户的追问问题（如有）
                - clarified (str): 澄清后的输入文本
        """
        # 简单启发式: 输入过短或明显有疑问词时触发澄清
        needs_clarification = len(user_input.strip()) < 8

        if not needs_clarification:
            clarification_prompt = (
                "请判断以下用户输入是否需要进一步澄清。如果需要，请用一行简短提问；"
                "如果不需要，请直接回复'不需要'。\n\n"
                f"用户输入: {user_input}\n"
            )
            try:
                llm_response = self._call_llm(clarification_prompt)
                needs_clarification = "不需要" not in llm_response
            except Exception:
                needs_clarification = False

        question = ""
        clarified = user_input

        if needs_clarification:
            question_prompt = (
                "用户输入不够清晰，请用一句简短的中文向用户追问关键信息。\n\n"
                f"用户输入: {user_input}\n"
                "请直接输出追问内容:"
            )
            try:
                question = self._call_llm(question_prompt).strip()
                # 生成澄清版本
                clarify_prompt = (
                    f"用户原始输入: {user_input}\n"
                    f"追问问题: {question}\n"
                    "请根据追问将用户意图整合为一句话，直接输出:"
                )
                clarified = self._call_llm(clarify_prompt).strip()
            except Exception:
                question = "请提供更多细节"
                clarified = user_input

        return {
            "needs_clarification": needs_clarification,
            "question": question,
            "clarified": clarified,
        }

    def _decide(self, clarified_input: str) -> Dict[str, Any]:
        """OODA 阶段二: 决策。

        根据澄清后的输入选择合适的策略和工具。

        Args:
            clarified_input: 澄清后的用户输入。

        Returns:
            dict:
                - strategy (str): 所选的执行策略，如 "direct_llm", "tool_call"
                - tool (str): 工具名称（仅 tool_call 策略时有效）
        """
        if not self._tools:
            return {"strategy": "direct_llm", "tool": ""}

        # 让 LLM 选择最合适的工具
        tool_names = list(self._tools.keys())
        tool_descriptions = []
        for name, tool in self._tools.items():
            desc = getattr(tool, "description", "")
            tool_descriptions.append(f"- {name}: {desc}")

        decide_prompt = (
            "你是一个任务路由器。根据用户输入选择最合适的工具。\n\n"
            "可用工具:\n"
            + "\n".join(tool_descriptions)
            + "\n\n"
            f"用户输入: {clarified_input}\n\n"
            "请回复工具名称（直接调用 LLM 请回复 'direct_llm'，"
            "仅回复一个名称不要解释）:"
        )

        try:
            choice = self._call_llm(decide_prompt).strip().lower()
            if choice == "direct_llm" or choice not in self._tools:
                return {"strategy": "direct_llm", "tool": ""}
            return {"strategy": "tool_call", "tool": choice}
        except Exception:
            return {"strategy": "direct_llm", "tool": ""}

    def _act(self, decision: Dict[str, Any], user_input: str) -> str:
        """OODA 阶段三: 执行。

        根据决策调用 LLM 或工具。

        Args:
            decision: _decide() 返回的决策字典。
            user_input: 当前轮次的输入文本。

        Returns:
            str: 执行结果。

        Raises:
            OODAAgentError: 工具调用失败时抛出。
        """
        strategy = decision.get("strategy", "direct_llm")

        if strategy == "tool_call":
            tool_name = decision.get("tool", "")
            tool = self._tools.get(tool_name)
            if tool is None:
                raise OODAAgentError(f"未找到工具: {tool_name}")
            try:
                # 兼容 LangChain BaseTool 的 _run / run 接口
                if hasattr(tool, "_run"):
                    return str(tool._run(user_input))
                elif hasattr(tool, "run"):
                    return str(tool.run(user_input))
                else:
                    return str(tool(user_input))
            except Exception as exc:
                raise OODAAgentError(f"工具 [{tool_name}] 执行失败: {exc}") from exc

        # 默认: 直接 LLM 调用
        try:
            return self._call_llm(user_input)
        except Exception as exc:
            raise OODAAgentError(f"LLM 调用失败: {exc}") from exc

    def _observe(self, result: str, user_input: str) -> Dict[str, Any]:
        """OODA 阶段四: 观察评估。

        评估执行结果是否满足要求，决定是否需要重试。

        Args:
            result: _act() 的执行结果。
            user_input: 原始用户输入（用于比对意图）。

        Returns:
            dict:
                - satisfied (bool): 结果是否满足要求
                - feedback (str): 不满足时的改进建议
        """
        # 简单启发式: 空结果、异常信息视为不满足
        if not result or not result.strip():
            return {"satisfied": False, "feedback": "结果为空"}

        if result.startswith("[执行异常]") or result.startswith("[错误]"):
            return {"satisfied": False, "feedback": result}

        # 使用 LLM 自评估
        eval_prompt = (
            "请评估以下回答是否满足用户需求。\n\n"
            f"用户需求: {user_input}\n"
            f"回答内容: {result}\n\n"
            "如果满足需求，请回复 '满足'；如果不满足，请回复 '不满足: <原因>'。"
        )

        try:
            feedback = self._call_llm(eval_prompt).strip()
            satisfied = feedback.startswith("满足") and "不满足" not in feedback
            return {"satisfied": satisfied, "feedback": feedback}
        except Exception:
            # 评估失败时保守满足
            return {"satisfied": True, "feedback": "评估跳过"}

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM 并返回响应的文本内容。

        兼容 LangChain BaseLLM（__call__）与 BaseChatModel（invoke）。

        Args:
            prompt: 提示词文本。

        Returns:
            str: LLM 响应文本。
        """
        # 尝试 invoke (BaseChatModel 风格)
        if hasattr(self._llm, "invoke"):
            resp = self._llm.invoke(prompt)
        else:
            resp = self._llm(prompt)

        # 提取文本
        if isinstance(resp, str):
            return resp
        if hasattr(resp, "content"):
            return str(resp.content)
        return str(resp)

    def _log(self, message: str, level: int = logging.INFO) -> None:
        """输出日志（通过 CallbackManager 或标准 logging）。

        Args:
            message: 日志消息。
            level: 日志级别。
        """
        self._callback.log(message, level)
        if self._verbose:
            print(message)

    @property
    def return_values(self) -> Dict[str, Any]:
        """返回 run() 的输出键说明（兼容 BaseTool 接口）。"""
        return {
            "result": "OODA 循环的最终输出结果",
            "iterations": "实际执行的迭代次数",
            "satisfied": "是否正常结束",
            "history": "历次迭代的详细记录",
        }

    @property
    def is_single_input(self) -> bool:
        """是否只接受单个输入（兼容 BaseTool）。"""
        return True
