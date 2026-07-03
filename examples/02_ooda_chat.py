# -*- coding: utf-8 -*-
"""
凡语示例 2: OODA 循环聊天
===========================
使用 OODA 循环引擎的交互式命令行聊天。
需要 Ollama 运行，默认使用 qwen2.5:1.5b。
"""

import sys
from fanlang import OODA, get_symbol


def simple_chat(symbol_char: str, user_input: str) -> str:
    """
    简单的聊天函数（可替换为真实的 LLM 调用）。
    这里用输入回显 + 模拟回复来演示 OODA 流程。
    生产环境应该替换为真正的 agent_func。
    """
    sym = get_symbol(symbol_char)
    name = sym.name_cn if sym else "问答"
    return f"[{name}模式] 收到你的输入：{user_input[:50]}...\n（此处应由 LLM 生成内容）"


def demo_ooda_basic():
    """OODA 循环基本用法：自动追问 + 多轮优化。"""
    print("=" * 60)
    print("【问】OODA 循环引擎 — Orient → Decide → Act → Observe")
    print("=" * 60)

    # 创建 OODA 实例
    ooda = OODA(agent_func=simple_chat, max_iterations=3)

    # 测试用例 1: 输入够清晰 → 直接执行
    print("\n--- 用例 1: 清晰输入 ---")
    result = ooda.run("帮我写一篇关于机器学习的科普文章，500字左右", symbol_char="写")
    if result["status"] == "clarify":
        print(f"  AI追问: {result['question']}")
    else:
        print(f"  状态: {result['status']}")
        print(f"  迭代: {result['iterations']} 轮")
        print(f"  满意: {result['satisfied']}")
        print(f"  结果:\n{result['result']}")

    # 测试用例 2: 输入模糊 → 触发追问
    print("\n--- 用例 2: 模糊输入（触发 Orient 追问）---")
    result = ooda.run("帮我写点东西", symbol_char="写")
    if result["status"] == "clarify":
        print(f"  AI追问: {result['question']}")
        print("  → 用户补充回答后进入下一轮")

    # 测试用例 3: 不指定符号 → 通用问答
    print("\n--- 用例 3: 不指定符号（通用问答）---")
    result = ooda.run("什么是深度学习？")
    if result["status"] == "done":
        print(f"  迭代: {result['iterations']} 轮")
        print(f"  结果:\n{result['result']}")


def demo_ooda_stream():
    """OODA 流式输出演示。"""
    print("\n" + "=" * 60)
    print("【编】OODA 流式输出：run_stream()")
    print("=" * 60)

    ooda = OODA(agent_func=simple_chat, max_iterations=2)

    print("\n流式输出（模拟）：")
    for chunk in ooda.run_stream("解释一下什么是神经网络", symbol_char="解"):
        status = chunk.get("status", "")
        if status == "clarify":
            print(f"\n[AI追问] {chunk['content']}")
        elif status == "streaming":
            print(chunk["content"], end="", flush=True)
        elif status == "done":
            print(f"\n\n[完成] 满意: {chunk.get('satisfied')}")


if __name__ == "__main__":
    demo_ooda_basic()
    demo_ooda_stream()
    print()
