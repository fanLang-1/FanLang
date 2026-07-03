# -*- coding: utf-8 -*-
"""
FanLang 符号体系测试
=====================
测试所有 25 个单字符号、36 个双词、12 个语法符号及其 API。
"""
import pytest
from fanlang.symbols import (
    Symbol, DoubleWord, GrammarSymbol,
    SINGLE_CHARS, TWO_WORDS, GRAMMAR_SYMBOLS, CORE_7,
    get_symbol, get_all_symbols, get_symbols_by_category,
    get_core_symbols, get_double_word, get_all_double_words,
    get_double_words_by_category, get_grammar,
    get_all_grammar_symbols, detect_symbol,
)


# ============================================================
# Symbol dataclass 基本字段和完整性
# ============================================================

class TestSymbolDataclass:
    """验证 Symbol 数据类的字段和基本行为。"""

    def test_symbol_fields(self):
        """Symbol 应包含全部 9 个字段。"""
        s = SINGLE_CHARS["写"]
        assert s.char == "写"
        assert s.emoji == "✍️"
        assert s.name_cn == "写作"
        assert s.name_en == "write / generate"
        assert s.description
        assert s.category == "内容创作"
        assert s.tier == 1
        assert "写作助手" in s.prompt_template
        assert "人工智能" in s.example

    def test_symbol_immutability_like(self):
        """Symbol 是 dataclass，可通过字段访问但不应被意外覆盖。"""
        s = SINGLE_CHARS["问"]
        assert s.char == "问"
        assert s.name_cn == "问答"
        assert s.tier == 1


class TestSingleCharCountAndCompleteness:
    """验证 25 个单字符号的存在性和完整性。"""

    def test_total_count(self):
        """必须有且仅有 25 个单字符号。"""
        assert len(SINGLE_CHARS) == 25

    def test_all_chars_present(self):
        """验证所有期望的符号字符都存在。"""
        expected = set("写改翻总问画想解教比查理编转算记定说试评阅空止兼或")
        assert set(SINGLE_CHARS.keys()) == expected

    def test_all_symbol_dataclass(self):
        """每个项都必须是 Symbol 实例。"""
        for s in SINGLE_CHARS.values():
            assert isinstance(s, Symbol)

    def test_all_required_fields_nonempty(self):
        """每个符号都必须有非空的 char, emoji, name_cn, name_en, description, category, tier, prompt_template。"""
        for s in SINGLE_CHARS.values():
            assert s.char, f"char 为空: {s}"
            assert s.emoji, f"emoji 为空: {s.char}"
            assert s.name_cn, f"name_cn 为空: {s.char}"
            assert s.name_en, f"name_en 为空: {s.char}"
            assert s.description, f"description 为空: {s.char}"
            assert s.category, f"category 为空: {s.char}"
            assert isinstance(s.tier, int), f"tier 不是 int: {s.char}"
            assert s.prompt_template, f"prompt_template 为空: {s.char}"


class TestTierNumbers:
    """验证各梯队数量。"""

    def test_tier_1_count(self):
        """第一梯队应有 7 个（CORE_7）。"""
        tier1 = [s for s in SINGLE_CHARS.values() if s.tier == 1]
        assert len(tier1) == 7

    def test_tier_2_count(self):
        """第二梯队应有 5 个。"""
        tier2 = [s for s in SINGLE_CHARS.values() if s.tier == 2]
        assert len(tier2) == 5

    def test_tier_3_count(self):
        """第三梯队应有 8 个。"""
        tier3 = [s for s in SINGLE_CHARS.values() if s.tier == 3]
        assert len(tier3) == 8

    def test_tier_4_count(self):
        """第四梯队应有 5 个。"""
        tier4 = [s for s in SINGLE_CHARS.values() if s.tier == 4]
        assert len(tier4) == 5

    def test_all_tiers_valid(self):
        """所有 tiere 值必须在 1-4 范围内。"""
        for s in SINGLE_CHARS.values():
            assert 1 <= s.tier <= 4, f"{s.char} 的 tier={s.tier} 不在 1-4 范围内"


class TestCategories:
    """验证分类完整性。"""

    def test_all_categories(self):
        """验证所有 5 个分类都存在。"""
        cats = set(s.category for s in SINGLE_CHARS.values())
        expected = {"内容创作", "认知推理", "信息处理", "执行操作", "框架操作"}
        assert cats == expected

    def test_content_creation_count(self):
        """内容创作类应有 7 个（写改翻总问卷画想）。"""
        cc = [s for s in SINGLE_CHARS.values() if s.category == "内容创作"]
        assert len(cc) == 7

    def test_cognitive_count(self):
        """认知推理类应有 4 个（解教比评）。"""
        cogs = [s for s in SINGLE_CHARS.values() if s.category == "认知推理"]
        assert len(cogs) == 4

    def test_info_processing_count(self):
        """信息处理类应有 4 个（查理转算）。"""
        ip = [s for s in SINGLE_CHARS.values() if s.category == "信息处理"]
        assert len(ip) == 4

    def test_execution_count(self):
        """执行操作类应有 5 个（编记定说试）。"""
        exe = [s for s in SINGLE_CHARS.values() if s.category == "执行操作"]
        assert len(exe) == 5

    def test_framework_count(self):
        """框架操作类应有 5 个（阅空止兼或）。"""
        fw = [s for s in SINGLE_CHARS.values() if s.category == "框架操作"]
        assert len(fw) == 5


# ============================================================
# CORE_7 验证
# ============================================================

class TestCore7:
    """验证核心 7 符号。"""

    def test_core_7_list_length(self):
        """CORE_7 必须正好有 7 个元素。"""
        assert len(CORE_7) == 7

    def test_core_7_contents(self):
        """CORE_7 必须包含正确的 7 个字符。"""
        assert CORE_7 == ["写", "改", "翻", "总", "问", "画", "想"]

    def test_core_7_all_tier_1(self):
        """CORE_7 中所有符号的 tier 必须为 1。"""
        for char in CORE_7:
            assert SINGLE_CHARS[char].tier == 1

    def test_get_core_symbols_returns_symbols(self):
        """get_core_symbols() 必须返回 Symbol 实例。"""
        cores = get_core_symbols()
        assert len(cores) == 7
        for s in cores:
            assert isinstance(s, Symbol)
            assert s.char in CORE_7


# ============================================================
# 对外 API 测试
# ============================================================

class TestGetSymbol:
    """测试 get_symbol()。"""

    def test_get_existing(self):
        s = get_symbol("写")
        assert s is not None
        assert s.char == "写"
        assert isinstance(s, Symbol)

    def test_get_non_existing(self):
        s = get_symbol("X")
        assert s is None

    def test_get_empty(self):
        s = get_symbol("")
        assert s is None

    def test_get_none(self):
        s = get_symbol(None)
        assert s is None  # dict.get(None) returns None


class TestGetAllSymbols:
    """测试 get_all_symbols()。"""

    def test_count(self):
        symbols = get_all_symbols()
        assert len(symbols) == 25
        assert all(isinstance(s, Symbol) for s in symbols)

    def test_unique_chars(self):
        symbols = get_all_symbols()
        chars = [s.char for s in symbols]
        assert len(set(chars)) == 25


class TestGetSymbolsByCategory:
    """测试 get_symbols_by_category()。"""

    def test_existing_category(self):
        symbols = get_symbols_by_category("内容创作")
        assert len(symbols) == 7
        assert all(s.category == "内容创作" for s in symbols)

    def test_non_existing_category(self):
        symbols = get_symbols_by_category("不存在的分类")
        assert symbols == []

    def test_empty_category(self):
        symbols = get_symbols_by_category("")
        assert symbols == []


class TestGetCoreSymbols:
    """测试 get_core_symbols()。"""

    def test_returns_7(self):
        cores = get_core_symbols()
        assert len(cores) == 7

    def test_all_core_chars(self):
        cores = get_core_symbols()
        chars = [s.char for s in cores]
        assert chars == CORE_7


# ============================================================
# 双词符号测试
# ============================================================

class TestDoubleWordDataclass:
    """验证 DoubleWord 数据类。"""

    def test_double_word_fields(self):
        dw = TWO_WORDS["推理"]
        assert dw.word == "推理"
        assert dw.emoji == "🧠"
        assert dw.name_en == "reasoning"
        assert dw.description
        assert dw.category == "推理"

    def test_all_double_words_are_instances(self):
        for dw in TWO_WORDS.values():
            assert isinstance(dw, DoubleWord)


class TestDoubleWordCounts:
    """验证 36 个双词符号的完整性。"""

    def test_total_count(self):
        assert len(TWO_WORDS) == 36

    def test_six_categories(self):
        cats = set(dw.category for dw in TWO_WORDS.values())
        expected = {"推理", "生成", "理解", "交互", "专业", "协同"}
        assert cats == expected

    def test_each_category_has_6(self):
        for cat in ["推理", "生成", "理解", "交互", "专业", "协同"]:
            items = [dw for dw in TWO_WORDS.values() if dw.category == cat]
            assert len(items) == 6, f"{cat} 应有 6 个，实际 {len(items)}"

    def test_all_double_words_have_fields(self):
        for dw in TWO_WORDS.values():
            assert dw.word
            assert dw.emoji
            assert dw.name_en
            assert dw.description
            assert dw.category


class TestDoubleWordApi:
    """测试双词 API 函数。"""

    def test_get_double_word_existing(self):
        dw = get_double_word("分析")
        assert dw is not None
        assert dw.word == "分析"
        assert isinstance(dw, DoubleWord)

    def test_get_double_word_non_existing(self):
        assert get_double_word("不存在") is None

    def test_get_all_double_words(self):
        all_dw = get_all_double_words()
        assert len(all_dw) == 36
        assert all(isinstance(dw, DoubleWord) for dw in all_dw)

    def test_get_double_words_by_category_existing(self):
        words = get_double_words_by_category("推理")
        assert len(words) == 6
        assert all(w.category == "推理" for w in words)

    def test_get_double_words_by_category_non_existing(self):
        assert get_double_words_by_category("不存在") == []


# ============================================================
# 语法符号测试
# ============================================================

class TestGrammarSymbolDataclass:
    """验证 GrammarSymbol 数据类。"""

    def test_grammar_fields(self):
        gs = GRAMMAR_SYMBOLS["【】"]
        assert gs.symbol == "【】"
        assert gs.name_cn == "指令框"
        assert gs.name_en == "command / role"
        assert gs.usage

    def test_all_are_instances(self):
        for gs in GRAMMAR_SYMBOLS.values():
            assert isinstance(gs, GrammarSymbol)


class TestGrammarSymbolCounts:
    """验证 12 个语法符号。"""

    def test_total_count(self):
        assert len(GRAMMAR_SYMBOLS) == 12

    def test_expected_symbols(self):
        expected = {"【】", "「」", "→", "←", "※", "&", "◎", "●", "→→", "==", "??", "!"}
        assert set(GRAMMAR_SYMBOLS.keys()) == expected

    def test_all_grammar_have_fields(self):
        for gs in GRAMMAR_SYMBOLS.values():
            assert gs.symbol
            assert gs.name_cn
            assert gs.name_en
            assert gs.usage


class TestGrammarApi:
    """测试语法 API 函数。"""

    def test_get_grammar_existing(self):
        gs = get_grammar("【】")
        assert gs is not None
        assert gs.symbol == "【】"
        assert isinstance(gs, GrammarSymbol)

    def test_get_grammar_non_existing(self):
        assert get_grammar("@@") is None

    def test_get_all_grammar_symbols(self):
        all_gs = get_all_grammar_symbols()
        assert len(all_gs) == 12
        assert all(isinstance(gs, GrammarSymbol) for gs in all_gs)


# ============================================================
# detect_symbol 测试
# ============================================================

class TestDetectSymbol:
    """测试 detect_symbol() 关键词匹配。"""

    def test_detect_write(self):
        """包含 '写文章' 应匹配 '写'。"""
        assert detect_symbol("帮我写一篇文章") == "写"

    def test_detect_rewrite(self):
        assert detect_symbol("帮我修改这段话") == "改"

    def test_detect_translate(self):
        assert detect_symbol("翻译这句话成英文") == "翻"

    def test_detect_summarize(self):
        assert detect_symbol("帮我总结一下内容") == "总"

    def test_detect_draw(self):
        assert detect_symbol("画一只猫") == "画"

    def test_detect_ask(self):
        """包含 '?' 相关词应匹配 '问'。"""
        assert detect_symbol("机器学习和大数据有啥区别") == "问"

    def test_detect_brainstorm(self):
        assert detect_symbol("给我一些创意点子") == "想"

    def test_detect_explain(self):
        assert detect_symbol("用比喻解释区块链") == "解"

    def test_detect_teach(self):
        assert detect_symbol("零基础学Python") == "教"

    def test_detect_compare(self):
        assert detect_symbol("对比A和B的差异") == "比"

    def test_detect_search(self):
        assert detect_symbol("搜索相关资料") == "查"

    def test_detect_organize(self):
        assert detect_symbol("整理这些笔记") == "理"

    def test_detect_code(self):
        assert detect_symbol("帮我编程实现排序算法") == "编"

    def test_detect_convert(self):
        assert detect_symbol("转换成PDF格式") == "转"

    def test_detect_calculate(self):
        assert detect_symbol("计算这组数据的平均值") == "算"

    def test_detect_remember(self):
        assert detect_symbol("记住这个设置") == "记"

    def test_detect_schedule(self):
        assert detect_symbol("每天早上提醒我") == "定"

    def test_detect_speak(self):
        assert detect_symbol("朗读这段文字") == "说"

    def test_detect_experiment(self):
        assert detect_symbol("试验一下这个新方法") == "试"

    def test_detect_evaluate(self):
        assert detect_symbol("请您评价一下这段文字") == "评"

    def test_detect_default_to_ask(self):
        """无匹配时默认返回 '问'。"""
        assert detect_symbol("你好啊今天天气真好") == "问"

    def test_detect_empty_string(self):
        """空字符串默认返回 '问'。"""
        assert detect_symbol("") == "问"

    def test_detect_write_article(self):
        assert detect_symbol("帮我写一篇报告") == "写"

    def test_detect_edit_rewrite(self):
        assert detect_symbol("润色一下这段话") == "改"

    def test_detect_chain_of_keywords(self):
        """包含多个关键词时应匹配第一个。"""
        # '写' 的关键词列表排在前面
        assert detect_symbol("我想写一篇文章并画图") == "写"


# ============================================================
# Prompt Templates 验证
# ============================================================

class TestPromptTemplates:
    """验证所有符号的 prompt_template 不为空且包含有效内容。"""

    def test_all_templates_not_empty(self):
        for s in SINGLE_CHARS.values():
            assert s.prompt_template, f"{s.char} 的 prompt_template 为空"
            assert len(s.prompt_template) > 10, f"{s.char} 的 prompt_template 太短"

    def test_write_prompt_meaningful(self):
        s = get_symbol("写")
        assert "写作助手" in s.prompt_template

    def test_ask_prompt_meaningful(self):
        s = get_symbol("问")
        assert "问答助手" in s.prompt_template


# ============================================================
# Data Integrity
# ============================================================

class TestDataIntegrity:
    """跨模块数据一致性测试。"""

    def test_core_7_are_in_single_chars(self):
        for c in CORE_7:
            assert c in SINGLE_CHARS, f"{c} 不在 SINGLE_CHARS 中"

    def test_no_duplicate_chars(self):
        assert len(SINGLE_CHARS) == len(set(SINGLE_CHARS.keys()))

    def test_no_duplicate_double_words(self):
        assert len(TWO_WORDS) == len(set(TWO_WORDS.keys()))

    def test_no_duplicate_grammar(self):
        assert len(GRAMMAR_SYMBOLS) == len(set(GRAMMAR_SYMBOLS.keys()))

    def test_tier_1_matches_core_7(self):
        tier1 = set(s.char for s in SINGLE_CHARS.values() if s.tier == 1)
        assert tier1 == set(CORE_7)
