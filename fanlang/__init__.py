# -*- coding: utf-8 -*-
"""
FanLang —— 凡语
================
AI interaction in Chinese characters. A UI/interaction layer for open-source AI projects.

核心 API：
    Symbol, DoubleWord, GrammarSymbol — 符号数据结构
    OODA — OODA 循环引擎
    QuickRAG — 检索增强生成
    WolfPackRouter — 狼群模型路由
    explain, get_en, get_all_terms — 术语翻译
"""

# 符号体系
from fanlang.symbols import (
    Symbol,
    DoubleWord,
    GrammarSymbol,
    SINGLE_CHARS,
    TWO_WORDS,
    GRAMMAR_SYMBOLS,
    CORE_7,
    get_symbol,
    get_all_symbols,
    get_symbols_by_category,
    get_core_symbols,
    get_double_word,
    get_all_double_words,
    get_double_words_by_category,
    get_grammar,
    get_all_grammar_symbols,
    detect_symbol,
)

# OODA 循环引擎
from fanlang.ooda import (
    OODA,
    CLARITY_RULES,
)

# RAG 检索增强生成
from fanlang.rag import (
    QuickRAG,
    extract_text,
    SUPPORTED_EXTS,
)

# 术语映射
from fanlang.terminology import (
    EN_TO_CN,
    CN_TO_EN,
    explain,
    get_en,
    get_all_terms,
)

# 狼群模型配置
from fanlang.wolfpack import (
    WOLF_PACK,
    EMBED_MODEL,
    MAIN_MODEL,
    REASON_MODEL,
    VISION_MODEL,
    WolfPackRouter,
)

__all__ = [
    # 符号
    "Symbol",
    "DoubleWord",
    "GrammarSymbol",
    "SINGLE_CHARS",
    "TWO_WORDS",
    "GRAMMAR_SYMBOLS",
    "CORE_7",
    "get_symbol",
    "get_all_symbols",
    "get_symbols_by_category",
    "get_core_symbols",
    "get_double_word",
    "get_all_double_words",
    "get_double_words_by_category",
    "get_grammar",
    "get_all_grammar_symbols",
    "detect_symbol",
    # OODA
    "OODA",
    "CLARITY_RULES",
    # RAG
    "QuickRAG",
    "extract_text",
    "SUPPORTED_EXTS",
    # 术语
    "EN_TO_CN",
    "CN_TO_EN",
    "explain",
    "get_en",
    "get_all_terms",
    # 狼群
    "WOLF_PACK",
    "EMBED_MODEL",
    "MAIN_MODEL",
    "REASON_MODEL",
    "VISION_MODEL",
    "WolfPackRouter",
]

__version__ = "0.1.0"
