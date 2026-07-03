"""
🐉 中文口语化 AI 符号系统
==========================
每个符号 = 一个字（或词），中文母语者一看就懂。
不用学任何英文术语，这就是"大众的 AI 脚手架"。
"""

from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# 符号定义
# ============================================================
@dataclass
class AISymbol:
    """一个 AI 符号"""
    char: str              # 符号字符（如"写"）
    emoji: str             # emoji 图标
    name: str              # 名称
    desc: str              # 一句话说明（口语化）
    prompt_template: str   # 系统提示词模板
    color: str             # 主题色
    example: str = ""      # 示例用法

# ============================================================
# 🐉 AI 七龙珠（核心 7 个）
# ============================================================
CORE_SYMBOLS = [
    AISymbol(
        char="写", emoji="✍️", name="写作",
        desc="写文章、写报告、写文案，你说要求它来写",
        color="#FF6B6B",
        example="帮我写一篇关于人工智能的科普文章，500字左右",
        prompt_template="你是写作助手。用中文口语化的风格写作，像朋友聊天一样自然。用户说写什么，你就怎么写。",
    ),
    AISymbol(
        char="改", emoji="✏️", name="改写",
        desc="把一段话改得更好、更顺、更合你心意",
        color="#FFA502",
        example="这段话太长了，帮我改短一点，口语化一些",
        prompt_template="你是改写助手。用户给你一段文字，你按他的要求改写——可以改短、改长、改风格、改语气。保持原意即可。",
    ),
    AISymbol(
        char="翻", emoji="🔄", name="翻译",
        desc="中译英、英译中，随便什么语言都可以",
        color="#2ED573",
        example="把这句话翻译成英文：今天天气真好",
        prompt_template="你是翻译助手。用户给什么语言你就翻成什么语言。翻译要自然，不要机器味。如果用户没说方向，默认中英互译。",
    ),
    AISymbol(
        char="总", emoji="📋", name="总结",
        desc="长文章太长不想看？让它给你总结重点",
        color="#1E90FF",
        example="帮我把这篇文章总结成 3 个要点",
        prompt_template="你是总结助手。用户给你一段文字，你提炼核心要点。用 bullet point 列出，每条一行，口语化。",
    ),
    AISymbol(
        char="问", emoji="❓", name="问答",
        desc="有啥不懂的，直接问它，像问朋友一样",
        color="#A855F7",
        example="机器学习和大数据有什么区别？",
        prompt_template="你是问答助手。用户问什么你答什么。用大白话解释，别拽术语。如果不知道就说不知道，别瞎编。",
    ),
    AISymbol(
        char="画", emoji="🎨", name="绘画",
        desc="描述你想看的画面，它来生成图片描述",
        color="#FF69B4",
        example="一只橘猫在键盘上睡觉，阳光洒在身上",
        prompt_template="你是绘画描述师。用户描述想看的画面，你把它转成详细的英文绘图提示词（prompt），方便复制到 Midjourney / DALL·E / Stable Diffusion 使用。",
    ),
    AISymbol(
        char="想", emoji="💡", name=" brainstorm",
        desc="没思路？让它帮你头脑风暴，出点子",
        color="#F43F5E",
        example="我想开个创新的小店，帮我 brainstorm 10 个点子",
        prompt_template="你是创意助手。用户需要灵感，你帮他头脑风暴。点子要新颖、具体、落地。每次至少给 5 个。",
    ),
]

# ============================================================
# 🛠️ 工具符号（进阶 5 个）
# ============================================================
TOOL_SYMBOLS = [
    AISymbol(
        char="解", emoji="🔍", name="解释",
        desc="复杂概念听不懂？让它用人话解释给你听",
        color="#10B981",
        example="什么是区块链？用我能听懂的话解释",
        prompt_template="你是通俗解释专家。用户问一个概念，你用最简单的比喻和日常语言解释。就像跟朋友聊天一样。",
    ),
    AISymbol(
        char="教", emoji="📚", name="教学",
        desc="想学什么东西？让它一步步教你，像老师一样",
        color="#6366F1",
        example="我想学 Python，从零开始，先学什么？",
        prompt_template="你是耐心老师。用户想学东西，你从零开始一步步教。要具体、可操作、有例子。别一次讲太多。",
    ),
    AISymbol(
        char="编", emoji="💻", name="编程",
        desc="写代码、改代码、解释代码，都行",
        color="#22C55E",
        example="用 Python 写一个计算器程序",
        prompt_template="你是编程助手。用户让你写代码或解释代码。用 Python 为主，要说清楚每段代码干什么。",
    ),
    AISymbol(
        char="比", emoji="📊", name="比较",
        desc="两个东西有啥区别？让它帮你对比分析",
        color="#F59E0B",
        example="比较一下微信和抖音的商业模式",
        prompt_template="你是分析助手。用户让你比较两个事物，你从多个维度对比，列出异同，最后给结论。用表格最好。",
    ),
    AISymbol(
        char="理", emoji="🗂️", name="整理",
        desc="乱七八糟的信息，让它帮你理清楚、分好类",
        color="#8B5CF6",
        example="帮我把这些笔记整理成思维导图的大纲",
        prompt_template="你是整理助手。用户给你混乱的信息，你帮它归类、排序、结构化。输出要清晰有条理。",
    ),
]

ALL_SYMBOLS = CORE_SYMBOLS + TOOL_SYMBOLS
SYMBOL_MAP = {s.char: s for s in ALL_SYMBOLS}

def get_symbol(char: str) -> Optional[AISymbol]:
    """根据符号字符获取符号定义"""
    return SYMBOL_MAP.get(char)

def get_prompt(char: str, user_input: str = "") -> str:
    """根据符号和用户输入生成完整 prompt"""
    sym = get_symbol(char)
    if not sym:
        return ""
    return f"{sym.prompt_template}\n\n用户说：{user_input}"
