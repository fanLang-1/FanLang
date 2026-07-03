# -*- coding: utf-8 -*-
"""
FanLang 术语映射
=================
英文 AI 术语 → 中文符号的翻译表。
让大众不用学英文也能理解 AI 概念。
"""

from typing import Dict, List, Optional


# ============================================================
# EN_TO_CN 映射表（22 个英文 AI 术语 → 中文符号）
# ============================================================
EN_TO_CN: Dict[str, str] = {
    "prompt": "【指令】",
    "system prompt": "【设】",
    "agent": "智能体",
    "RAG": "【查】+【总】",
    "embedding": "向量化",
    "fine-tune": "微调",
    "inference": "推理",
    "training": "训练",
    "generation": "生成",
    "summarization": "总结",
    "classification": "分类",
    "extraction": "提取",
    "reasoning": "推理",
    "planning": "规划",
    "memory": "记忆",
    "tool use": "●工具",
    "workflow": "工作流",
    "multi-agent": "多智能体协作",
    "chain of thought": "【推理】一步步想",
    "retrieval": "【查】",
    "context window": "上下文窗口",
    "token": "词元",
    "hallucination": "AI幻觉",
    "alignment": "对齐",
}

# 反向映射表（中文 → 英文），构建时忽略大小写
CN_TO_EN: Dict[str, str] = {}


def _build_reverse():
    """构建反向映射表。"""
    global CN_TO_EN
    CN_TO_EN.clear()
    for en_val, cn_val in EN_TO_CN.items():
        # 清理中文符号中的特殊字符作为 key
        clean_cn = cn_val.replace("【", "").replace("】", "").replace("●", "")
        CN_TO_EN[clean_cn] = en_val
        # 同时保留原始形式
        CN_TO_EN[cn_val] = en_val


_build_reverse()


# ============================================================
# 对外 API
# ============================================================
def explain(term: str) -> str:
    """
    返回英文术语的中文解释。
    如果 term 已经是中文，尝试反向查询。

    Args:
        term: 英文 AI 术语或中文符号

    Returns:
        对应的中文符号或英文术语
    """
    # 正向查询：英文 → 中文
    result = EN_TO_CN.get(term)
    if result:
        return result
    result = EN_TO_CN.get(term.lower())
    if result:
        return result
    # 反向查询：中文 → 英文
    result = CN_TO_EN.get(term)
    if result:
        return result
    return term


def get_en(cn_term: str) -> Optional[str]:
    """
    反向查询：中文 → 英文。

    Args:
        cn_term: 中文符号或术语

    Returns:
        对应的英文术语，未找到返回 None
    """
    return CN_TO_EN.get(cn_term)


def get_all_terms() -> Dict[str, str]:
    """
    获取全部英文→中文映射表。

    Returns:
        完整的 EN_TO_CN 字典
    """
    return dict(EN_TO_CN)
