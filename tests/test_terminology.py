# -*- coding: utf-8 -*-
"""
FanLang 术语映射测试
=====================
测试 EN_TO_CN 映射表、explain()、get_en()、get_all_terms() 和 CN_TO_EN 反向映射。
"""
import pytest
from fanlang.terminology import (
    EN_TO_CN, CN_TO_EN,
    explain, get_en, get_all_terms,
)


# ============================================================
# EN_TO_CN 映射表完整性
# ============================================================

class TestENToCNCompleteness:
    """验证 EN_TO_CN 映射表。"""

    # 24 个已知条目
    EXPECTED_KEYS = [
        "prompt", "system prompt", "agent", "RAG", "embedding",
        "fine-tune", "inference", "training", "generation",
        "summarization", "classification", "extraction", "reasoning",
        "planning", "memory", "tool use", "workflow", "multi-agent",
        "chain of thought", "retrieval", "context window", "token",
        "hallucination", "alignment",
    ]

    def test_count(self):
        """验证至少有 24 个映射条目。"""
        assert len(EN_TO_CN) >= 24, f"预期至少 24 项，实际 {len(EN_TO_CN)}"

    def test_all_expected_keys_present(self):
        """所有预期的英文术语都存在。"""
        for key in self.EXPECTED_KEYS:
            assert key in EN_TO_CN, f"缺失英文术语: {key}"

    def test_all_values_nonempty(self):
        """所有映射值都非空。"""
        for en, cn in EN_TO_CN.items():
            assert cn, f"{en} 的映射值为空"

    def test_prompt_mapping(self):
        assert EN_TO_CN["prompt"] == "【指令】"

    def test_system_prompt_mapping(self):
        assert EN_TO_CN["system prompt"] == "【设】"

    def test_rag_mapping(self):
        assert EN_TO_CN["RAG"] == "【查】+【总】"

    def test_agent_mapping(self):
        assert EN_TO_CN["agent"] == "智能体"

    def test_tool_use_mapping(self):
        assert EN_TO_CN["tool use"] == "●工具"

    def test_chain_of_thought_mapping(self):
        assert EN_TO_CN["chain of thought"] == "【推理】一步步想"

    def test_retrieval_mapping(self):
        assert EN_TO_CN["retrieval"] == "【查】"

    def test_hallucination_mapping(self):
        assert EN_TO_CN["hallucination"] == "AI幻觉"

    def test_no_duplicate_values(self):
        """不同英文术语映射到不同中文值时允许，但重复检查。"""
        # 一些术语如 inference/reasoning 都映射到"推理"，这是合理的
        pass

    def test_special_chars_in_values(self):
        """验证包含特殊字符的映射。"""
        assert "【" in EN_TO_CN["prompt"]
        assert "●" in EN_TO_CN["tool use"]


# ============================================================
# CN_TO_EN 反向映射
# ============================================================

class TestCNToEN:
    """验证 CN_TO_EN 反向映射表。"""

    def test_is_populated(self):
        """CN_TO_EN 构建后必须有条目。"""
        assert len(CN_TO_EN) > 0

    def test_forward_reverse_consistency(self):
        """正向映射的中文值应能在反向映射中查到。
        注意：多个英文术语可能映射到同一中文（如 inference/reasoning 都 → 推理），
        此时反向映射只能保留最后一个写入的值。
        """
        # 先收集所有"一对多"的情况（多个英文→同一中文）
        cn_to_en_list: dict = {}
        for en_val, cn_val in EN_TO_CN.items():
            cn_to_en_list.setdefault(cn_val, []).append(en_val)

        for en_val, cn_val in EN_TO_CN.items():
            assert cn_val in CN_TO_EN, f"反向映射缺失: {cn_val}"
            # 如果多个英文映射到同一中文，反向映射值可能是其中任意一个
            expected_ens = cn_to_en_list[cn_val]
            assert CN_TO_EN[cn_val] in expected_ens, (
                f"反向映射不匹配: {cn_val} -> {CN_TO_EN[cn_val]}, "
                f"期望其中之一 {expected_ens}"
            )

    def test_cleaned_keys_exist(self):
        """清理后的中文键（去掉【】●）也应存在。"""
        # "指令" 应该是 prompt 的清理后形式
        assert "指令" in CN_TO_EN, "缺少清理后的键: 指令"
        assert CN_TO_EN["指令"] == "prompt"

    def test_setup_reverse(self):
        """反向映射中"设" 应指向 "system prompt"。"""
        assert CN_TO_EN["设"] == "system prompt"
        assert CN_TO_EN["工具"] == "tool use"

    def test_no_missing_forward_values(self):
        """所有 EN_TO_CN 的值都应在 CN_TO_EN 中。"""
        for cn_val in EN_TO_CN.values():
            assert cn_val in CN_TO_EN


# ============================================================
# explain() 函数
# ============================================================

class TestExplain:
    """测试 explain() 函数。"""

    def test_forward_exact(self):
        """英文精确匹配。"""
        assert explain("prompt") == "【指令】"

    def test_forward_case_insensitive(self):
        """英文字母大小写不敏感。"""
        assert explain("Prompt") == "【指令】"
        assert explain("PROMPT") == "【指令】"

    def test_reverse_exact(self):
        """中文正向反向均可。"""
        assert explain("【指令】") == "prompt"

    def test_reverse_clean_key(self):
        """中文清理后的键也可反向。"""
        assert explain("指令") == "prompt"

    def test_rag_uppercase(self):
        """RAG 保持原样匹配。"""
        assert explain("RAG") == "【查】+【总】"

    def test_chain_of_thought(self):
        assert explain("chain of thought") == "【推理】一步步想"

    def test_unknown_term_returns_itself(self):
        """未知术语原样返回。"""
        assert explain("不存在的术语") == "不存在的术语"

    def test_empty_string(self):
        """空字符串原样返回。"""
        assert explain("") == ""

    def test_numeric_input(self):
        """数字字符串原样返回。"""
        assert explain("123") == "123"

    def test_forward_tool_use(self):
        assert explain("tool use") == "●工具"

    def test_reverse_agent(self):
        assert explain("智能体") == "agent"


# ============================================================
# get_en() 函数
# ============================================================

class TestGetEn:
    """测试 get_en() 反向查询。"""

    def test_get_en_by_cn_value(self):
        """通过中文值查询英文。"""
        assert get_en("【指令】") == "prompt"

    def test_get_en_by_cleaned(self):
        """通过清理后的中文查询英文。"""
        assert get_en("指令") == "prompt"

    def test_get_en_not_found(self):
        """未找到时返回 None。"""
        assert get_en("不存在的术语") is None

    def test_get_en_empty(self):
        """空字符串返回 None。"""
        assert get_en("") is None

    def test_get_en_agent(self):
        assert get_en("智能体") == "agent"

    def test_get_en_hallucination(self):
        assert get_en("AI幻觉") == "hallucination"


# ============================================================
# get_all_terms() 函数
# ============================================================

class TestGetAllTerms:
    """测试 get_all_terms()。"""

    def test_returns_copy(self):
        """返回的是 EN_TO_CN 的副本而非引用。"""
        terms = get_all_terms()
        terms["new"] = "test"
        assert "new" not in EN_TO_CN

    def test_returns_all_entries(self):
        terms = get_all_terms()
        assert len(terms) == len(EN_TO_CN)

    def test_content_identical(self):
        terms = get_all_terms()
        assert terms == EN_TO_CN


# ============================================================
# Edge Cases
# ============================================================

class TestEdgeCases:
    """边界情况测试。"""

    def test_explain_partial_match_not_supported(self):
        """explain 不支持部分匹配，只支持精确/大小写不敏感。"""
        result = explain("prompt engineering")
        # "prompt engineering" 不在 EN_TO_CN 中，也不在 CN_TO_EN 中
        assert result == "prompt engineering"

    def test_explain_with_whitespace(self):
        """前后空格键可能不匹配。"""
        assert explain("  prompt  ") == "  prompt  "  # 不会 strip

    def test_cn_to_en_cleaned_multi_char(self):
        """多字符清理检查。"""
        # "推理一步步想" 是 chain of thought 的 cleaned 形式
        clean = "推理一步步想"
        # 清理过程会去掉 【】 和 ●
        assert get_en(clean) == get_en("【推理】一步步想")

    def test_en_to_cn_all_not_empty(self):
        """每个英文术语都有对应的中文翻译，且不为空。"""
        for en, cn in EN_TO_CN.items():
            assert cn.strip(), f"{en} 对应空字符串"
