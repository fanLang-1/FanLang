# -*- coding: utf-8 -*-
"""
FanLang OODA 循环引擎
======================
Orient → Decide → Act → Observe 四阶段循环。
每个符号有对应的清晰度规则，确保 AI 获得足够信息后再执行。
"""

import json
from typing import Any, Callable, Dict, List, Optional

from .symbols import get_symbol, Symbol


# ============================================================
# 清晰度规则：每个符号需要哪些信息才算完整
# ============================================================
CLARITY_RULES: Dict[str, List[str]] = {
    "写": ["写什么类型", "什么主题", "多长", "什么风格"],
    "改": ["改什么", "改成什么样"],
    "翻": ["翻什么", "从哪到哪"],
    "总": ["总什么", "多短的摘要"],
    "问": ["问什么"],
    "画": ["画什么", "什么风格"],
    "想": ["想什么方面", "要几个点子"],
    "解": ["解什么概念", "用哪个领域打比方"],
    "教": ["教什么", "从什么水平开始"],
    "比": ["比什么和什么", "从哪些维度比"],
    "查": ["查什么", "在哪查"],
    "理": ["理什么", "理成什么样子"],
    "编": ["编什么", "什么语言", "什么功能"],
    "转": ["转什么", "转成什么格式"],
    "算": ["算什么", "想要什么结果"],
    "记": ["记什么", "什么时候要用"],
    "定": ["定什么时间", "做什么事"],
    "说": ["说什么内容", "什么风格"],
    "试": ["试什么", "有什么约束条件"],
    "评": ["评什么", "从哪些维度评"],
    "阅": ["阅什么内容"],
    "空": ["想创造什么"],
    "止": ["需要输出什么"],
    "兼": ["要合并什么和什么"],
    "或": ["有哪些选项", "按什么标准选"],
}

# 符号 → 智能体类型
SYMBOL_TO_AGENT: Dict[str, str] = {
    "写": "writing_agent", "改": "rewriting_agent", "翻": "translation_agent",
    "总": "summary_agent", "问": "qa_agent", "画": "drawing_agent",
    "想": "brainstorm_agent", "解": "explain_agent", "教": "teach_agent",
    "比": "compare_agent", "查": "search_agent", "理": "organize_agent",
    "编": "coding_agent", "转": "convert_agent", "算": "calculate_agent",
    "记": "memory_agent", "定": "schedule_agent", "说": "voice_agent",
    "试": "experiment_agent", "评": "evaluate_agent",
    "阅": "read_agent", "空": "create_agent", "止": "stop_agent",
    "兼": "combine_agent", "或": "choose_agent",
}

# 默认 Ollama 配置
DEFAULT_OLLAMA_HOST: str = "http://localhost:11434"
DEFAULT_MODEL: str = "qwen2.5:1.5b"


# ============================================================
# Ollama 调用封装
# ============================================================
def _ollama_chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    stream: bool = False,
    host: str = DEFAULT_OLLAMA_HOST,
) -> str:
    """调用 Ollama API 进行对话。

    Args:
        messages: 消息列表
        model: 模型名
        stream: 是否流式输出
        host: Ollama 服务地址

    Returns:
        模型回复文本
    """
    import urllib.request
    import urllib.error

    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "stream": stream,
    }
    url = f"{host}/api/chat"
    data = json.dumps(payload).encode()

    try:
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return result.get("message", {}).get("content", "")
    except urllib.error.URLError:
        return '{"error": "ollama_not_running"}'


def _ollama_chat_stream(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    host: str = DEFAULT_OLLAMA_HOST,
):
    """流式调用 Ollama API。

    Yields:
        每次 yield 一段文本内容
    """
    try:
        import requests

        payload = {
            "model": model or DEFAULT_MODEL,
            "messages": messages,
            "stream": True,
        }
        resp = requests.post(
            f"{host}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        )
        resp.raise_for_status()

        for line in resp.iter_lines(decode_unicode=True):
            if line:
                data = json.loads(line)
                if "message" in data and "content" in data["message"]:
                    yield data["message"]["content"]
                if data.get("done"):
                    break
    except ImportError:
        # requests 不可用时回退到非流式
        result = _ollama_chat(messages, model, stream=False, host=host)
        yield result


# ============================================================
# OODA 循环引擎
# ============================================================
class OODA:
    """OODA 循环引擎：Orient → Decide → Act → Observe。

    用法::

        from fanlang import OODA

        ooda = OODA(max_iterations=3)
        result = ooda.run("帮我写一篇关于AI的科普文章", symbol_char="写")
    """

    def __init__(
        self,
        agent_func: Optional[Callable[[str, str], str]] = None,
        max_iterations: int = 5,
        model: Optional[str] = None,
        chat_func: Optional[Callable] = None,
    ):
        """
        Args:
            agent_func: 执行函数，签名 agent_func(symbol_char, user_input) -> str。
                       如果为 None，将使用默认 Ollama 调用。
            max_iterations: 最大 OODA 循环次数
            model: 默认模型名（如 "qwen2.5:1.5b"）
            chat_func: 自定义聊天函数，签名 chat_func(messages, model) -> str。
                      用于 orient/decide/observe 阶段的 LLM 调用。
        """
        self._agent_func = agent_func
        self.max_iterations = max_iterations
        self.model = model or DEFAULT_MODEL
        self._chat_func = chat_func

    def _chat(self, messages: List[Dict[str, str]]) -> str:
        """内部 LLM 调用。"""
        if self._chat_func:
            return self._chat_func(messages, self.model)
        return _ollama_chat(messages, model=self.model)

    def orient(self, user_input: str, symbol_char: Optional[str] = None) -> Dict[str, Any]:
        """Orient 阶段：检查用户输入是否足够清晰。

        Args:
            user_input: 用户输入
            symbol_char: 符号字符（如"写"）

        Returns:
            {"need_clarify": bool, "question": str, "summary": str}
        """
        sym: Optional[Symbol] = get_symbol(symbol_char) if symbol_char else None
        if not sym:
            return {"need_clarify": False, "summary": user_input}

        rules = CLARITY_RULES.get(symbol_char, [])

        # 短输入直接追问
        if len(user_input.strip()) < 8 and rules:
            return {"need_clarify": True, "question": rules[0] + "?"}

        rules_text = "\n".join("- " + r for r in rules)
        prompt = (
            f"当前模式: {sym.emoji} [{sym.char}] {sym.name_cn}\n"
            f"用户输入: {user_input}\n\n"
            f"需要明确的信息:\n{rules_text}\n\n"
            f"判断用户是否说清楚了? 如果否, 最该先问哪一个问题?(只问一个)\n"
            f'输出JSON: {{"clear": true/false, "next_question": "问题", "summary": "总结"}}'
        )

        resp = self._chat([
            {"role": "system", "content": "你是AI需求分析师,输出JSON。"},
            {"role": "user", "content": prompt},
        ])

        try:
            result = json.loads(resp)
            if "error" in result:
                return {"need_clarify": False, "summary": user_input}
            if result.get("clear"):
                return {"need_clarify": False, "summary": result.get("summary", user_input)}
            else:
                return {
                    "need_clarify": True,
                    "question": result.get("next_question", "能说具体点吗?"),
                }
        except Exception:
            return {"need_clarify": False, "summary": user_input}

    def decide(self, user_input: str, symbol_char: Optional[str] = None) -> Dict[str, Any]:
        """Decide 阶段：选择策略和智能体。

        Args:
            user_input: 用户输入（已澄清）
            symbol_char: 符号字符

        Returns:
            决策结果字典
        """
        sym = get_symbol(symbol_char) if symbol_char else None
        return {
            "agent": SYMBOL_TO_AGENT.get(symbol_char, "general_agent"),
            "symbol_char": symbol_char or "问",
            "symbol_name": sym.name_cn if sym else "问答",
            "user_input": user_input,
        }

    def act(self, decision: Dict[str, Any]) -> str:
        """Act 阶段：执行具体操作。

        Args:
            decision: decide() 返回的决策结果

        Returns:
            AI 执行结果文本
        """
        if self._agent_func:
            return self._agent_func(decision["symbol_char"], decision["user_input"])

        # 默认使用 Ollama 生成
        sym = get_symbol(decision.get("symbol_char"))
        system_prompt = sym.prompt_template if sym else "你是有用的助手。用中文回答。"

        return _ollama_chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": decision["user_input"]},
            ],
            model=self.model,
        )

    def observe(self, user_input: str, result: str) -> Dict[str, Any]:
        """Observe 阶段：评估结果质量。

        Args:
            user_input: 原始用户输入
            result: AI 执行结果

        Returns:
            {"satisfied": bool, "feedback": str}
        """
        prompt = (
            f"用户要求: {user_input}\n"
            f"AI回答: {result[:300]}\n\n"
            f"判断回答是否满足了用户要求? 如果否, 具体要改什么?\n"
            f'输出JSON: {{"satisfied": true/false, "feedback": "改进建议"}}'
        )
        resp = self._chat([
            {"role": "system", "content": "你是质量检查员,输出JSON。"},
            {"role": "user", "content": prompt},
        ])
        try:
            result_data = json.loads(resp)
            satisfied = result_data.get("satisfied", True)
            return {
                "satisfied": satisfied,
                "feedback": result_data.get("feedback", "") if not satisfied else "OK",
            }
        except Exception:
            return {"satisfied": True, "feedback": ""}

    def run(
        self,
        user_input: str,
        symbol_char: Optional[str] = None,
    ) -> Dict[str, Any]:
        """执行完整 OODA 循环。

        Args:
            user_input: 用户输入
            symbol_char: 符号字符（可为 None，此时不进行符号澄清）

        Returns:
            {
                "status": "done" | "clarify",
                "result": str | None,
                "question": str | None,
                "iterations": int,
                "satisfied": bool,
                "feedback": str,
            }
        """
        # Orient: 澄清
        orient_result = self.orient(user_input, symbol_char)
        if orient_result["need_clarify"]:
            return {
                "status": "clarify",
                "result": None,
                "question": orient_result["question"],
                "iterations": 0,
                "satisfied": False,
                "feedback": "",
            }

        clarified_input = orient_result.get("summary", user_input)

        # Decide + Act + Observe 循环
        for iteration in range(1, self.max_iterations + 1):
            decision = self.decide(clarified_input, symbol_char)
            result_text = self.act(decision)
            obs = self.observe(user_input, result_text)

            if obs["satisfied"]:
                return {
                    "status": "done",
                    "result": result_text,
                    "question": None,
                    "iterations": iteration,
                    "satisfied": True,
                    "feedback": obs["feedback"],
                }

        # 达到最大循环次数仍未满足
        return {
            "status": "done",
            "result": result_text,
            "question": None,
            "iterations": self.max_iterations,
            "satisfied": False,
            "feedback": obs.get("feedback", ""),
        }

    def run_stream(
        self,
        user_input: str,
        symbol_char: Optional[str] = None,
    ):
        """流式执行 OODA 循环。

        Yields:
            逐步输出结果片段
        """
        # Orient 阶段
        orient_result = self.orient(user_input, symbol_char)
        if orient_result["need_clarify"]:
            yield {
                "status": "clarify",
                "content": orient_result["question"],
                "question": orient_result["question"],
            }
            return

        clarified_input = orient_result.get("summary", user_input)

        # Decide + Act (流式)
        decision = self.decide(clarified_input, symbol_char)
        sym = get_symbol(decision.get("symbol_char"))
        system_prompt = sym.prompt_template if sym else "你是有用的助手。用中文回答。"

        full_text = ""
        for chunk in _ollama_chat_stream(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": decision["user_input"]},
            ],
            model=self.model,
        ):
            full_text += chunk
            yield {"status": "streaming", "content": chunk, "text": full_text}

        # Observe
        obs = self.observe(user_input, full_text)
        yield {
            "status": "done",
            "content": full_text,
            "satisfied": obs["satisfied"],
            "feedback": obs["feedback"],
        }
