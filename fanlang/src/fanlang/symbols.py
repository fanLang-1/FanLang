# -*- coding: utf-8 -*-
"""
FanLang 符号体系
================
25 个单字 + 36 个双词 + 12 个语法符号
每个概念都是原生中文，一看就懂。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# 符号数据结构
# ============================================================
@dataclass
class Symbol:
    """一个凡语符号的完整定义。"""
    char: str                          # 符号字符（如"写"）
    emoji: str                         # 表情图标
    name_cn: str                       # 中文名称
    name_en: str                       # 英文名称
    description: str                   # 一句话说明
    category: str                      # 所属分类
    tier: int                          # 梯队（1-4）
    prompt_template: str               # 系统提示词模板
    example: str = ""                  # 使用示例


@dataclass
class DoubleWord:
    """双词符号定义。"""
    word: str                          # 双词（如"推理"）
    emoji: str                         # 表情图标
    name_en: str                       # 英文名称
    description: str                   # 说明
    category: str                      # 所属分类


@dataclass
class GrammarSymbol:
    """语法符号定义。"""
    symbol: str                        # 符号本身（如"【】"）
    name_cn: str                       # 中文名称
    name_en: str                       # 英文名称
    usage: str                         # 用法说明


# ============================================================
# 25 个单字符号
# ============================================================
_SINGLE_CHARS_DATA: List[dict] = [
    # ── 第一梯队 · 7 个核心（日常够用）──
    {"char":"写","emoji":"✍️","name_cn":"写作","name_en":"write / generate",
     "description":"写文章、写报告、写文案，你说要求它来写",
     "category":"内容创作","tier":1,
     "prompt_template":"你是写作助手。用中文口语化风格写作，像朋友聊天一样自然。用户说写什么，你就怎么写。",
     "example":"帮我写一篇关于人工智能的科普文章，500字左右"},

    {"char":"改","emoji":"✏️","name_cn":"改写","name_en":"rewrite / edit",
     "description":"把一段话改得更好、更顺、更合你心意",
     "category":"内容创作","tier":1,
     "prompt_template":"你是改写助手。用户给你一段文字，你按他的要求改写——可以改短、改长、改风格、改语气。保持原意即可。",
     "example":"这段话太长了，帮我改短一点，口语化一些"},

    {"char":"翻","emoji":"🔄","name_cn":"翻译","name_en":"translate",
     "description":"中英互译，或其他语言翻译",
     "category":"内容创作","tier":1,
     "prompt_template":"你是翻译助手。用户给什么语言你就翻成什么语言。翻译要自然，不要机器味。如果用户没说方向，默认中英互译。",
     "example":"把这句话翻译成英文：今天天气真好"},

    {"char":"总","emoji":"📋","name_cn":"总结","name_en":"summarize",
     "description":"提炼重点、压缩长文",
     "category":"内容创作","tier":1,
     "prompt_template":"你是总结助手。用户给你一段文字，你提炼核心要点。用 bullet point 列出，每条一行，口语化。",
     "example":"帮我把这篇文章总结成 3 个要点"},

    {"char":"问","emoji":"❓","name_cn":"问答","name_en":"ask / QA",
     "description":"不懂就问，知无不答",
     "category":"内容创作","tier":1,
     "prompt_template":"你是问答助手。用户问什么你答什么。用大白话解释，别拽术语。如果不知道就说不知道，别瞎编。",
     "example":"机器学习和大数据有什么区别？"},

    {"char":"画","emoji":"🎨","name_cn":"绘画","name_en":"draw / generate image",
     "description":"根据描述生成图片或绘图提示词",
     "category":"内容创作","tier":1,
     "prompt_template":"你是绘画描述师。用户描述想看的画面，你把它转成详细的英文绘图提示词，方便复制到 Midjourney / DALL-E / Stable Diffusion 使用。",
     "example":"一只橘猫在键盘上睡觉，阳光洒在身上"},

    {"char":"想","emoji":"💡","name_cn":"创意","name_en":"brainstorm",
     "description":"头脑风暴、出点子、给灵感",
     "category":"内容创作","tier":1,
     "prompt_template":"你是创意助手。用户需要灵感，你帮他头脑风暴。点子要新颖、具体、落地。每次至少给 5 个。",
     "example":"我想开个创新的小店，帮我 brainstorm 10 个点子"},

    # ── 第二梯队 · 5 个进阶 ──
    {"char":"解","emoji":"🔍","name_cn":"解释","name_en":"explain",
     "description":"把复杂概念用比喻讲清楚",
     "category":"认知推理","tier":2,
     "prompt_template":"你是通俗解释专家。用户问一个概念，你用最简单的比喻和日常语言解释。就像跟朋友聊天一样。",
     "example":"什么是区块链？用买菜打比方"},

    {"char":"教","emoji":"📚","name_cn":"教学","name_en":"teach / tutor",
     "description":"从零开始教你学东西",
     "category":"认知推理","tier":2,
     "prompt_template":"你是耐心老师。用户想学东西，你从零开始一步步教。要具体、可操作、有例子。别一次讲太多。",
     "example":"我想学 Python，从零开始，先学什么？"},

    {"char":"比","emoji":"📊","name_cn":"比较","name_en":"compare",
     "description":"两个东西放一起对比分析",
     "category":"认知推理","tier":2,
     "prompt_template":"你是分析助手。用户让你比较两个事物，你从多个维度对比，列出异同，最后给结论。用表格最好。",
     "example":"微信支付和支付宝有什么区别？"},

    {"char":"查","emoji":"🔎","name_cn":"检索","name_en":"search / retrieve",
     "description":"在资料库里搜索答案",
     "category":"信息处理","tier":2,
     "prompt_template":"你是检索助手。基于已有知识回答问题，注明信息来自哪里。",
     "example":"查一下知识库里有没有关于 transformer 的内容"},

    {"char":"理","emoji":"🗂️","name_cn":"整理","name_en":"organize",
     "description":"分类、排序、结构化信息",
     "category":"信息处理","tier":2,
     "prompt_template":"你是整理助手。用户给你混乱的信息，你帮它归类、排序、结构化。输出要清晰有条理。",
     "example":"帮我整理这堆笔记，按主题分类"},

    # ── 第三梯队 · 8 个专项 ──
    {"char":"编","emoji":"💻","name_cn":"编程","name_en":"code / program",
     "description":"写代码、改代码、解释代码",
     "category":"执行操作","tier":3,
     "prompt_template":"你是编程助手。用户让你写代码或解释代码。用 Python 为主，说清楚每段代码干什么。",
     "example":"用 Python 写一个爬虫"},

    {"char":"转","emoji":"🔄","name_cn":"转换","name_en":"convert / transform",
     "description":"格式转换、风格转换",
     "category":"信息处理","tier":3,
     "prompt_template":"你是格式转换助手。按用户要求转换格式。",
     "example":"把这个表格转成 Markdown 格式"},

    {"char":"算","emoji":"🧮","name_cn":"计算","name_en":"calculate / compute",
     "description":"数学计算、数据分析",
     "category":"信息处理","tier":3,
     "prompt_template":"你是计算助手。给出计算过程和结果。",
     "example":"帮我算一下这组数据的平均值和标准差"},

    {"char":"记","emoji":"📝","name_cn":"记忆","name_en":"remember / save",
     "description":"记住重要信息，长期保存",
     "category":"执行操作","tier":3,
     "prompt_template":"你是记忆助手。记住重要信息，下次对话可用。",
     "example":"记住我喜欢的写作风格是简洁幽默"},

    {"char":"定","emoji":"⏰","name_cn":"定时","name_en":"schedule / timer",
     "description":"设定定时任务、提醒",
     "category":"执行操作","tier":3,
     "prompt_template":"你是定时助手。帮用户规划时间安排。",
     "example":"每天早上 8 点提醒我读 AI 新闻"},

    {"char":"说","emoji":"🎤","name_cn":"语音","name_en":"speak / voice",
     "description":"语音朗读、语音交互",
     "category":"执行操作","tier":3,
     "prompt_template":"你是语音助手。把文字转成适合朗读的口语。",
     "example":"把这段文字读给我听"},

    {"char":"试","emoji":"🧪","name_cn":"尝试","name_en":"try / experiment",
     "description":"试错、实验、调试",
     "category":"执行操作","tier":3,
     "prompt_template":"你是实验助手。帮用户尝试不同的方案。",
     "example":"这个算法参数怎么调最好？"},

    {"char":"评","emoji":"⭐","name_cn":"评价","name_en":"evaluate / measure",
     "description":"对结果打分、评判、给反馈",
     "category":"认知推理","tier":3,
     "prompt_template":"你是评价助手。客观公正，优缺点都说。",
     "example":"帮我看看这段代码质量怎么样"},

    # ── 第四梯队 · 5 个框架专用 ──
    {"char":"阅","emoji":"📖","name_cn":"阅读","name_en":"read / observe (identity)",
     "description":"只看不动，原样传递，恒等态射",
     "category":"框架操作","tier":4,
     "prompt_template":"你是观察助手。只描述你看到的，不做分析和评价。",
     "example":"这段文字是什么内容"},

    {"char":"空","emoji":"🌌","name_cn":"空","name_en":"empty / void (initial object)",
     "description":"虚空起点，无中生有，初始对象",
     "category":"框架操作","tier":4,
     "prompt_template":"你是创造助手。从零开始，没有任何限制。",
     "example":"从头开始，什么都没有"},

    {"char":"止","emoji":"⏹️","name_cn":"终止","name_en":"stop / terminal (terminal object)",
     "description":"所有操作的终点，固定输出",
     "category":"框架操作","tier":4,
     "prompt_template":"你是输出助手。给出最终结论，不再继续。",
     "example":"到这里为止，输出最终结果"},

    {"char":"兼","emoji":"🤝","name_cn":"兼有","name_en":"both / product",
     "description":"两个输入合并在一起处理",
     "category":"框架操作","tier":4,
     "prompt_template":"你是整合助手。把多个信息合并在一起分析。",
     "example":"把A和B合并起来一起分析"},

    {"char":"或","emoji":"🔀","name_cn":"选择","name_en":"or / coproduct",
     "description":"多条路径选择其一",
     "category":"框架操作","tier":4,
     "prompt_template":"你是选择助手。帮用户对比不同选项，推荐最佳。",
     "example":"选A方案或B方案，哪个更好"},
]


def _build_single_chars() -> Dict[str, Symbol]:
    """从原始数据构建符号字典。"""
    result: Dict[str, Symbol] = {}
    for d in _SINGLE_CHARS_DATA:
        result[d["char"]] = Symbol(
            char=d["char"],
            emoji=d["emoji"],
            name_cn=d["name_cn"],
            name_en=d["name_en"],
            description=d["description"],
            category=d["category"],
            tier=d["tier"],
            prompt_template=d["prompt_template"],
            example=d.get("example", ""),
        )
    return result


SINGLE_CHARS: Dict[str, Symbol] = _build_single_chars()

# 核心 7 符号
CORE_7: List[str] = ["写", "改", "翻", "总", "问", "画", "想"]


# ============================================================
# 36 个双词符号（分 6 类）
# ============================================================
TWO_WORDS: Dict[str, DoubleWord] = {
    # ── 推理类 ──
    "推理": DoubleWord("推理", "🧠", "reasoning", "一步一步逻辑推理，给出结论", "推理"),
    "分析": DoubleWord("分析", "📐", "analysis", "拆开来看，找出规律和关系", "推理"),
    "预测": DoubleWord("预测", "🔮", "prediction", "根据已有信息推断未来", "推理"),
    "规划": DoubleWord("规划", "🗺️", "planning", "制定步骤和路线图", "推理"),
    "决策": DoubleWord("决策", "⚖️", "decision", "在多个选项中推荐最佳方案", "推理"),
    "归纳": DoubleWord("归纳", "🧩", "induction", "从具体案例中总结通用规律", "推理"),
    # ── 生成类 ──
    "生成": DoubleWord("生成", "⚡", "generation", "从无到有创造内容", "生成"),
    "创作": DoubleWord("创作", "🎭", "creation", "创意性写作、诗歌、故事", "生成"),
    "设计": DoubleWord("设计", "🎯", "design", "设计方案、界面、流程", "生成"),
    "推荐": DoubleWord("推荐", "👍", "recommendation", "根据偏好推荐最合适的", "生成"),
    "优化": DoubleWord("优化", "⚡", "optimization", "让结果更好、更快、更省", "生成"),
    "演绎": DoubleWord("演绎", "🎬", "deduction", "从通用规则出发推导具体结论", "生成"),
    # ── 理解类 ──
    "识别": DoubleWord("识别", "👁️", "recognition", "认出图片/文字/语音中的内容", "理解"),
    "理解": DoubleWord("理解", "💭", "comprehension", "读懂深层含义和上下文", "理解"),
    "提取": DoubleWord("提取", "🔧", "extraction", "从一堆信息中取出关键内容", "理解"),
    "分类": DoubleWord("分类", "📂", "classification", "把东西按类别分好", "理解"),
    "排序": DoubleWord("排序", "📊", "sorting", "按某种规则排先后顺序", "理解"),
    "挖掘": DoubleWord("挖掘", "⛏", "mining", "从海量数据中发现隐藏的模式和知识", "理解"),
    # ── 交互类 ──
    "搜索": DoubleWord("搜索", "🔍", "search", "在知识库或网络中查找信息", "交互"),
    "对话": DoubleWord("对话", "💬", "dialogue", "多轮聊天，有来有回", "交互"),
    "反馈": DoubleWord("反馈", "📣", "feedback", "对结果给出评价和改进建议", "交互"),
    "审核": DoubleWord("审核", "✅", "review", "检查内容是否符合要求", "交互"),
    "监控": DoubleWord("监控", "📡", "monitoring", "持续观察，异常时提醒", "交互"),
    "引导": DoubleWord("引导", "🧭", "guide", "一步一步带领用户完成复杂任务", "交互"),
    # ── 专业类 ──
    "编程": DoubleWord("编程", "💻", "programming", "写代码、调试、优化程序", "专业"),
    "建模": DoubleWord("建模", "🏗️", "modeling", "建立数据模型或数学建模", "专业"),
    "测试": DoubleWord("测试", "🧪", "testing", "检查有没有问题，质量好不好", "专业"),
    "标注": DoubleWord("标注", "🏷️", "annotation", "给数据打标签，做标记", "专业"),
    "训练": DoubleWord("训练", "🏋️", "training", "让AI学习新知识或技能", "专业"),
    "评估": DoubleWord("评估", "📝", "evaluation", "打分、评价、衡量效果", "专业"),
    # ── 协同类 ──
    "协作": DoubleWord("协作", "🤝", "collaboration", "多个AI一起干活", "协同"),
    "分配": DoubleWord("分配", "🎯", "assignment", "把任务分给不同的AI", "协同"),
    "调度": DoubleWord("调度", "🔄", "scheduling", "安排任务先后和优先级", "协同"),
    "同步": DoubleWord("同步", "🔄", "synchronization", "信息保持一致", "协同"),
    "汇总": DoubleWord("汇总", "📊", "aggregation", "把多个结果合并成一个", "协同"),
    "编排": DoubleWord("编排", "🎼", "orchestration", "协调多个AI按顺序和依赖工作", "协同"),
}


# ============================================================
# 12 个语法符号
# ============================================================
GRAMMAR_SYMBOLS: Dict[str, GrammarSymbol] = {
    "【】": GrammarSymbol("【】", "指令框", "command / role", "设定AI的角色或指令模式"),
    "「」": GrammarSymbol("「」", "内容框", "content / data", "标记输入的内容数据"),
    "→":   GrammarSymbol("→",   "输出箭头", "output", "指定输出的格式和方向"),
    "←":   GrammarSymbol("←",   "输入箭头", "input", "标记信息来源"),
    "※":   GrammarSymbol("※",   "条件符", "condition", "如果…就…，条件判断"),
    "&":    GrammarSymbol("&",   "并行符", "parallel", "同时执行多个操作"),
    "◎":   GrammarSymbol("◎",   "循环符", "loop", "重复执行直到满足条件"),
    "●":   GrammarSymbol("●",   "工具符", "tool / function", "调用一个外部工具"),
    "→→":  GrammarSymbol("→→", "转发符", "forward", "把任务转给另一个AI"),
    "==":   GrammarSymbol("==",  "分隔符", "separator", "分隔不同部分的内容"),
    "??":   GrammarSymbol("??",  "疑问符", "uncertainty", "表示不确定，需要确认"),
    "!":    GrammarSymbol("!",   "强调符", "emphasis", "重要！必须遵守"),
}


# ============================================================
# 对外 API
# ============================================================
def get_symbol(char: str) -> Optional[Symbol]:
    """根据符号字符获取符号定义。"""
    return SINGLE_CHARS.get(char)


def get_all_symbols() -> List[Symbol]:
    """获取所有单字符号。"""
    return list(SINGLE_CHARS.values())


def get_symbols_by_category(category: str) -> List[Symbol]:
    """按分类获取符号列表。"""
    return [s for s in SINGLE_CHARS.values() if s.category == category]


def get_core_symbols() -> List[Symbol]:
    """获取核心 7 符号。"""
    return [SINGLE_CHARS[c] for c in CORE_7 if c in SINGLE_CHARS]


def get_double_word(word: str) -> Optional[DoubleWord]:
    """根据双词获取定义。"""
    return TWO_WORDS.get(word)


def get_all_double_words() -> List[DoubleWord]:
    """获取所有双词符号。"""
    return list(TWO_WORDS.values())


def get_double_words_by_category(category: str) -> List[DoubleWord]:
    """按分类获取双词符号。"""
    return [w for w in TWO_WORDS.values() if w.category == category]


def get_grammar(symbol: str) -> Optional[GrammarSymbol]:
    """根据符号获取语法符号定义。"""
    return GRAMMAR_SYMBOLS.get(symbol)


def get_all_grammar_symbols() -> List[GrammarSymbol]:
    """获取所有语法符号。"""
    return list(GRAMMAR_SYMBOLS.values())


def detect_symbol(user_input: str) -> str:
    """
    根据用户输入自动识别最匹配的符号。
    先用关键词匹配，再用 LLM 兜底。
    """
    # 关键词匹配
    kw_map: List[tuple] = [
        ("写", ["写", "文章", "作文", "文案", "小说", "稿子", "报告", "创作"]),
        ("改", ["改", "润色", "修改", "编辑", "修订", "校对"]),
        ("翻", ["翻", "翻译", "译", "英文", "中文"]),
        ("总", ["总", "总结", "摘要", "提炼", "概括", "归纳"]),
        ("画", ["画", "图片", "图像", "插图", "绘画", "绘图"]),
        ("问", ["问", "问题", "什么", "为什么", "怎么", "吗", "如何", "啥"]),
        ("想", ["想", "点子", "创意", "灵感", "建议", "方案"]),
        ("解", ["解", "解释", "什么意思", "含义", "比喻", "通俗"]),
        ("教", ["教", "学", "学习", "教程", "入门"]),
        ("比", ["比", "对比", "区别", "差异", "哪个好", "不同"]),
        ("查", ["查", "搜索", "查找", "检索"]),
        ("理", ["理", "整理", "分类", "归档", "梳理"]),
        ("编", ["编", "代码", "程序", "编程", "bug", "开发"]),
        ("转", ["转", "转换", "转化为", "格式", "转成"]),
        ("算", ["算", "计算", "数据", "统计"]),
        ("记", ["记", "记住", "保存", "记录", "收藏"]),
        ("定", ["定", "定时", "提醒", "安排", "计划", "日程", "每天"]),
        ("说", ["说", "读", "朗读", "语音", "发音"]),
        ("试", ["试", "尝试", "试验", "调试"]),
        ("评", ["评", "评价", "评分", "打分", "评测", "怎么样"]),
    ]
    for sym, keywords in kw_map:
        for kw in keywords:
            if kw in user_input:
                return sym
    return "问"
