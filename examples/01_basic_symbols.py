# -*- coding: utf-8 -*-
"""
凡语示例 1: 符号体系入门
=========================
展示凡语 25 个单字符号 + 36 个双词符号 + 12 个语法符号的基本用法。
不需要 Ollama / LLM，纯 API 演示。
"""

from fanlang import (
    Symbol,
    DoubleWord,
    GrammarSymbol,
    get_symbol,
    get_all_symbols,
    get_core_symbols,
    get_symbols_by_category,
    get_double_word,
    get_all_double_words,
    get_double_words_by_category,
    get_grammar,
    get_all_grammar_symbols,
    detect_symbol,
)
from fanlang.terminology import explain, get_en, get_all_terms


def demo_single_chars():
    """展示 25 个单字符号。"""
    print("=" * 60)
    print("【写】凡语 25 个单字符号")
    print("=" * 60)

    all_symbols = get_all_symbols()
    print(f"\n共 {len(all_symbols)} 个符号，分 4 个梯队：\n")

    for tier in range(1, 5):
        tier_symbols = [s for s in all_symbols if s.tier == tier]
        print(f"  第 {tier} 梯队（{len(tier_symbols)} 个）：")
        for s in tier_symbols:
            print(f"    {s.emoji} {s.char}  — {s.name_cn}")
        print()

    # 按分类展示
    print("-" * 40)
    print("按分类查看：")
    categories = set(s.category for s in all_symbols)
    for cat in sorted(categories):
        syms = get_symbols_by_category(cat)
        names = ", ".join(f"{s.emoji}{s.char}" for s in syms)
        print(f"  【{cat}】: {names}")

    # 核心 7 符号
    print("-" * 40)
    core = get_core_symbols()
    print("核心 7 符号（日常够用）：")
    for s in core:
        print(f"  {s.emoji} {s.char}  {s.name_cn}: {s.description}")


def demo_double_words():
    """展示 36 个双词符号。"""
    print("\n" + "=" * 60)
    print("【理】凡语 36 个双词符号（分 6 类）")
    print("=" * 60)

    all_dw = get_all_double_words()
    categories = sorted(set(w.category for w in all_dw))
    for cat in categories:
        words = get_double_words_by_category(cat)
        names = ", ".join(f"{w.emoji}{w.word}" for w in words)
        print(f"  {cat}: {names}")


def demo_grammar():
    """展示 12 个语法符号。"""
    print("\n" + "=" * 60)
    print("【解】凡语 12 个语法符号")
    print("=" * 60)

    for g in get_all_grammar_symbols():
        print(f"  {g.symbol:6s}  {g.name_cn:6s}  {g.name_en:12s}  {g.usage}")


def demo_single_symbol():
    """展示单个符号的详细定义。"""
    print("\n" + "=" * 60)
    print("【查】单个符号详细信息")
    print("=" * 60)

    sym = get_symbol("写")
    if sym:
        print(f"\n  字符:      {sym.char}")
        print(f"  Emoji:     {sym.emoji}")
        print(f"  中文名:    {sym.name_cn}")
        print(f"  英文名:    {sym.name_en}")
        print(f"  描述:      {sym.description}")
        print(f"  分类:      {sym.category}")
        print(f"  梯队:      {sym.tier}")
        print(f"  Prompt:    {sym.prompt_template[:60]}...")
        print(f"  示例:      {sym.example}")


def demo_detect():
    """展示输入文本自动匹配符号。"""
    print("\n" + "=" * 60)
    print("【问】自动识别符号：detect_symbol()")
    print("=" * 60)

    test_inputs = [
        "帮我写一篇关于AI的科普文章",
        "这段话帮我润色一下",
        "把这句话翻译成英文",
        "这篇文章的核心观点是什么",
        "机器学习和大数据有什么区别",
        "帮我搜一下关于Transformer的资料",
        "用Python写一个爬虫程序",
    ]
    for text in test_inputs:
        sym = detect_symbol(text)
        matched = get_symbol(sym)
        print(f"  「{text[:20]}...」→ {matched.emoji}【{matched.char}】{matched.name_cn}")


def demo_terminology():
    """展示术语翻译。"""
    print("\n" + "=" * 60)
    print("【翻】AI 术语翻译：explain()")
    print("=" * 60)

    terms = ["prompt", "RAG", "embedding", "inference", "agent", "fine-tune"]
    for t in terms:
        result = explain(t)
        reverse = get_en(result)
        print(f"  {t:15s} → {result:20s}  {'(' + reverse + ')' if reverse and reverse != t else ''}")

    print(f"\n共有 {len(get_all_terms())} 条术语映射。")


if __name__ == "__main__":
    demo_single_chars()
    demo_double_words()
    demo_grammar()
    demo_single_symbol()
    demo_detect()
    demo_terminology()
    print()
