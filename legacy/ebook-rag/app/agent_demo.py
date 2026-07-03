"""
🤖 用中文符号搭智能体 —— 替代英文 agent framework
=====================================================
不用学 LangChain、Function Call、Tool Use
用【知】【记】【感】【应】【定】【联】就能搭。

【智能体 = 知 + 记 + 感 + 应 + 定 + 联】
"""

from dataclasses import dataclass
from app.chinese_ai_lang import AGENT_PRIMITIVES, SINGLE_CHARS

@dataclass
class AgentBlueprint:
    name: str
    desc: str
    primitives: list
    workflow: str
    chinese_def: str
    when_to_use: str

from dataclasses import dataclass

@dataclass
class AgentBlueprint:
    name: str
    desc: str
    primitives: list
    workflow: str
    chinese_def: str
    when_to_use: str

AGENT_TEMPLATES = [
    AgentBlueprint(
        name="学习助手",
        desc="帮你读书、学知识、答疑解惑",
        primitives=["知", "记", "感"],
        workflow="""用户提问 → 【查】知识库 → 找不到？→ 【问】用户补充 → 【解】通俗回答 → 【记】学习记录""",
        chinese_def="""【定】学习助手
【知】连接到你的电子书库
【记】记住你学过什么、哪里不懂
【感】支持上传 PDF/EPUB
※ 提问 → 【查】书库 → 【解】回答
※ 看完一章 → 【总】重点 → 【记】进度""",
        when_to_use="想从自己的书库里学东西的时候"
    ),
    AgentBlueprint(
        name="写作助手",
        desc="帮你写文章、改文章、出文案",
        primitives=["记", "应", "联"],
        workflow="""用户说要求 → 【记】风格偏好 → 【写】初稿 → 【应】展示 → 用户反馈 → 【改】完善""",
        chinese_def="""【定】写作助手
【记】记住你喜欢的风格和常用词汇
【应】输出到 Markdown / Word
【联】可连接到你的知识库查资料
※ 自由写作 → 用【写】模式
※ 改文章 → 用【改】模式""",
        when_to_use="需要写东西、改东西的时候"
    ),
    AgentBlueprint(
        name="信息管家",
        desc="帮你整理信息、搜索资料、监控变化",
        primitives=["知", "感", "定", "联"],
        workflow="""【定】每天自动执行 → 【感】读取新资料 → 【理】分类 → 【总】摘要 → 【联】推送到微信""",
        chinese_def="""【定】信息管家
【定】每天早上8点执行
【感】读取指定文件夹的新文件
【理】按主题自动分类
【总】生成每日摘要
【联】推送到你的邮箱或微信""",
        when_to_use="信息太多，需要自动整理的时候"
    ),
    AgentBlueprint(
        name="编程伙伴",
        desc="帮你写代码、改 bug、学编程",
        primitives=["知", "感", "应"],
        workflow="""用户发代码 → 【感】读取 → 【编】分析 → 【教】解释 → 【改】优化建议""",
        chinese_def="""【定】编程伙伴
【感】支持粘贴代码或上传文件
【知】参考你的项目代码风格
※ 写代码 → 【编】生成
※ 改bug → 【试】调试分析
※ 学编程 → 【教】零基础教学""",
        when_to_use="写代码或者学编程的时候"
    ),
    AgentBlueprint(
        name="翻译官",
        desc="翻译、跨语言沟通、本地化",
        primitives=["记", "应"],
        workflow="""输入原文 → 【翻】翻译 → 【改】润色自然 → 【应】展示双语对照""",
        chinese_def="""【定】翻译官
【记】记住你偏好的翻译风格（正式/口语）
※ 中译英 → 【翻】直译 → 【改】润色
※ 英译中 → 【翻】意译 → 【改】本土化
→ 输出双语对照""",
        when_to_use="需要翻译任何内容的时候"
    ),
]

def show_all_agents():
    for agent in AGENT_TEMPLATES:
        print(f"\n{'='*60}")
        print(f"🤖 {agent.name}")
        print(f"   {agent.desc}")
        print(f"\n【中文定义】:")
        print(agent.chinese_def)
        print(f"\n【工作流程】:")
        print(f"   {agent.workflow}")
        print(f"\n💡 适用场景：{agent.when_to_use}")

if __name__ == "__main__":
    show_all_agents()
