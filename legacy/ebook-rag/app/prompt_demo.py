"""
📖 中文符号写提示词 —— 替代英文 prompt engineering
=====================================================
不用学 "system prompt"、"few-shot"、"chain-of-thought"
用【】「」→※ 这些符号 + 中文单字就能写提示词。
"""

from app.chinese_ai_lang import SINGLE_CHARS, TWO_WORDS, GRAMMAR_SYMBOLS
from dataclasses import dataclass
from typing import List

@dataclass
class PromptExample:
    name: str
    desc: str
    chinese_prompt: str      # 用符号写的提示词
    english_prompt: str      # 传统的英文提示词
    note: str                # 对比说明

EXAMPLES = [
    PromptExample(
        name="写一篇科技文章",
        desc="用符号代替 system prompt",
        chinese_prompt="""【写】你是科技作者。
「文风」口语化，像跟朋友聊天
「字数」500字左右
「要求」多用比喻，少用术语
→ 输出 Markdown

主题：人工智能在医疗领域的应用""",
        english_prompt="""System: You are a tech writer. 
Write in a conversational style, 
about 500 words, use metaphors,
avoid jargon. Output in Markdown.

User: Write about AI applications in healthcare.""",
        note="【写】= system prompt 角色设定\n「」= 参数设定\n→ = 输出格式"
    ),
    PromptExample(
        name="对比分析",
        desc="用【比】替代 compare and contrast",
        chinese_prompt="""【比】从以下维度对比：
「维度」价格、功能、用户体验、适用场景
→ 表格输出

微信支付 vs 支付宝""",
        english_prompt="""Compare WeChat Pay and Alipay 
across these dimensions: price, features, 
user experience, use cases. 
Output as a table.""",
        note="【比】一个字就表达了 compare 的意思"
    ),
    PromptExample(
        name="深度推理",
        desc="用【推理】替代 chain-of-thought",
        chinese_prompt="""【推理】一步步想，给出最终答案
「要求」先列出已知条件
「要求」每一步都要解释原因
→ 结论放在最后

问题：一个水池，进水管3小时注满，排水管5小时排空，两个同时开，多久能满？""",
        english_prompt="""Let's think step by step.
First list known conditions.
Explain each step.
Put the conclusion at the end.

A pool fills in 3 hours, drains in 5 hours. 
How long to fill if both are open?""",
        note="【推理】= chain-of-thought，但中文一目了然"
    ),
    PromptExample(
        name="查书问答（RAG）",
        desc="用【查】+【总】替代 RAG 流程",
        chinese_prompt="""【查】在我的知识库中搜索
「关键词」transformer 原理
「范围」C:\我的AI电子书
==
【总】搜索到的相关内容
→ 用大白话解释给我听""",
        english_prompt="""Search my knowledge base for 
"transformer architecture" in my AI ebooks.
Summarize the results.
Explain in plain language.""",
        note="【查】= retrieval，【总】= summarization，两个字代替 RAG 整个概念"
    ),
    PromptExample(
        name="创建智能体",
        desc="用中文原语定义 Agent",
        chinese_prompt="""【定】创建一个学习助手智能体

● 【知】连接到知识库：C:\编程书籍
● 【记】记住用户的学习进度
● 【感】支持上传代码文件

※ 用户发代码 → 【教】解释这段代码
※ 用户提问 → 【查】知识库 → 【解】通俗回答
※ 用户做完练习 → 【评】给出反馈

==
【应】每次回答后，问用户是否要继续""",
        english_prompt="""Create a learning assistant agent.
Knowledge base: C:\programming books
Memory: track user progress
Input: accept code files

If user sends code -> explain it
If user asks question -> search KB -> explain simply
If user completes exercise -> give feedback

After each response, ask if they want to continue.""",
        note="【定】= create agent，【知】= knowledge base，【记】= memory，纯中文定义智能体"
    ),
]

def show_all_examples():
    for ex in EXAMPLES:
        print(f"\n{'='*60}")
        print(f"📌 {ex.name}")
        print(f"   {ex.desc}")
        print(f"\n【中文符号版】:")
        print(ex.chinese_prompt)
        print(f"\n【英文传统版】:")
        print(ex.english_prompt)
        print(f"\n💡 {ex.note}")

# 如果直接运行，打印所有示例
if __name__ == "__main__":
    show_all_examples()
