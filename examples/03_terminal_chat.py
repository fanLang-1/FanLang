# -*- coding: utf-8 -*-
"""
凡语示例 3: 终端交互式聊天
===========================
带符号选择的终端聊天客户端。
需要 Ollama 运行，默认使用 qwen2.5:1.5b。

用法：
    python examples/03_terminal_chat.py
"""

import sys
from typing import Optional

from fanlang import OODA, get_symbol, get_all_symbols


def print_header():
    """打印启动头。"""
    print()
    print("╔════════════════════════════════════╗")
    print("║     凡语 FanLang — 终端聊天        ║")
    print("║   AI interaction in Chinese chars  ║")
    print("╚════════════════════════════════════╝")
    print()


def print_symbol_menu():
    """打印符号菜单。"""
    print("符号选择（输入符号字符切换模式，当前模式：问）：\n")

    all_syms = get_all_symbols()
    for tier in range(1, 5):
        tier_syms = [s for s in all_syms if s.tier == tier]
        line = "  ".join(f"{s.emoji} {s.char}({s.name_cn})" for s in tier_syms)
        print(f"  T{tier}: {line}")
    print()


def get_user_symbol() -> str:
    """让用户选择符号。"""
    while True:
        choice = input("  符号 [写/改/翻/...] 或回车默认(问): ").strip()
        if not choice:
            return "问"
        sym = get_symbol(choice)
        if sym:
            return choice
        print(f"  未知符号「{choice}」，请输入 25 个单字符号之一。")


class ChatApp:
    """终端聊天应用。"""

    def __init__(self):
        self.ooda = OODA(max_iterations=3)
        self.current_symbol: str = "问"

    def run(self):
        print_header()
        print_symbol_menu()

        self.current_symbol = get_user_symbol()
        sym = get_symbol(self.current_symbol)
        print(f"\n当前模式：{sym.emoji} {sym.char} — {sym.name_cn}")
        if sym and sym.example:
            print(f"示例输入：{sym.example}")
        print()

        print("输入 '!help' 查看命令，'!sym' 切换符号，'!exit' 退出\n")

        while True:
            try:
                # 获取用户输入
                user_input = input(f"\n[{sym.emoji}{sym.char}] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break

            if not user_input:
                continue

            # 命令处理
            if user_input == "!exit":
                print("再见！")
                break
            elif user_input == "!help":
                print("  !sym    切换符号模式")
                print("  !status 显示当前状态")
                print("  !help   显示此帮助")
                print("  !exit   退出")
                continue
            elif user_input == "!sym":
                self.current_symbol = get_user_symbol()
                sym = get_symbol(self.current_symbol)
                print(f"已切换到：{sym.emoji} {sym.char} — {sym.name_cn}")
                continue
            elif user_input == "!status":
                sym = get_symbol(self.current_symbol)
                print(f"  当前符号：{sym.emoji} {sym.char} {sym.name_cn}")
                print(f"  提示词：{sym.prompt_template[:80]}...")
                continue

            # 执行 OODA 循环
            result = self.ooda.run(user_input, symbol_char=self.current_symbol)

            if result["status"] == "clarify":
                # 需要追问
                print(f"\n🤖 {result['question']}")
                clarify_input = input(f"\n[{sym.emoji}{sym.char}] > ").strip()
                if clarify_input:
                    result = self.ooda.run(
                        f"{user_input}。补充：{clarify_input}",
                        symbol_char=self.current_symbol,
                    )

            if result["status"] == "done":
                print(f"\n🤖 {result['result']}")
                if result.get("feedback"):
                    print(f"\n[评估] {result['feedback']}")
                print(f"[迭代 {result['iterations']} 轮 | 满意: {result['satisfied']}]")


if __name__ == "__main__":
    app = ChatApp()
    app.run()
