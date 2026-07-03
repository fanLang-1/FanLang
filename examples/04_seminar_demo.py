# -*- coding: utf-8 -*-
"""
凡语示例 4: 盗火者研讨厅 — 多智能体协作
=======================================
展示三种组织形态：Pipeline（流水线）、Panel（评议制）、Adversarial（对撞式）。
需要 Ollama 运行。

用法：
    python examples/04_seminar_demo.py
"""

from fanlang.seminar import (
    SeminarHall,
    Role,
    PipelineOrg,
    PanelOrg,
    AdversarialOrg,
    quick_seminar,
    quick_pipeline,
    quick_panel,
    quick_adversarial,
)


def mock_chat(system: str, user: str) -> str:
    """
    模拟 chat 函数（无需 LLM 即可演示）。
    生产环境请替换为真实的 LLM 调用。
    """
    # 从 system prompt 中提取角色名
    import re
    match = re.search(r"你是 (.+?)[，。]", system)
    role_name = match.group(1) if match else "AI"
    return f"【{role_name}的回复】\n已收到您的任务。这是我的处理结果：\n{user[:80]}...\n\n[此内容应由 LLM 生成]"


def demo_pipeline():
    """流水线组织：写手 → 编辑 → 校对。"""
    print("=" * 60)
    print("【编】Pipeline 流水线 — 王写手 → 李编辑 → 张校对")
    print("=" * 60)

    hall = quick_seminar(chat_fn=mock_chat)
    pipeline = quick_pipeline(hall)

    print("\n任务：写一篇关于 AI 发展的科普文章\n")
    result = pipeline.execute("写一篇关于人工智能发展的科普文章，500字")

    print(f"\n最终输出（{result['rounds']} 轮）：")
    print(result["result"][:200] + "..." if len(result["result"]) > 200 else result["result"])

    print("\n各阶段输出：")
    for name, content in result["stages"].items():
        preview = content[:80].replace("\n", " ")
        print(f"  【{name}】: {preview}...")


def demo_panel():
    """评议制组织：多角色并行产出 + 主编汇总。"""
    print("\n" + "=" * 60)
    print("【想】Panel 评议制 — 王写手+赵创意+刘顾问 → 陈裁判汇总")
    print("=" * 60)

    hall = quick_seminar(chat_fn=mock_chat)
    panel = quick_panel(hall)

    print("\n任务：为新产品想 5 个宣传口号\n")
    result = panel.execute("为一个 AI 写作助手产品想 5 个宣传口号")

    print(f"\n各版本（{len(result['versions'])} 个）：")
    for name, content in result["versions"].items():
        preview = content[:60].replace("\n", " ")
        print(f"  【{name}的版本】: {preview}...")

    print(f"\n主编融合结果（{result['rounds']} 轮）：")
    print(result["result"][:200] + "..." if len(result["result"]) > 200 else result["result"])


def demo_adversarial():
    """对撞式组织：正方 vs 反方 → 裁判裁决。"""
    print("\n" + "=" * 60)
    print("【评】Adversarial 对撞式 — 王写手 vs 孙批判 → 陈裁判裁决")
    print("=" * 60)

    hall = quick_seminar(chat_fn=mock_chat)
    adv = quick_adversarial(hall)

    print("\n命题：中小企业应该用本地 AI 还是云端 AI？\n")
    result = adv.execute("中小企业应该用本地 AI 还是云端 AI？")

    print(f"\n辩论记录（{result['rounds']} 轮）：")
    for t in result.get("transcripts", []):
        preview = t["content"][:60].replace("\n", " ")
        print(f"  第{t['round']}轮 【{t['role']} - {t['action']}】: {preview}...")

    print(f"\n裁判裁决：")
    print(result["result"][:300] + "..." if len(result["result"]) > 300 else result["result"])


def demo_custom_roles():
    """自定义角色 + 流水线。"""
    print("\n" + "=" * 60)
    print("【兼】自定义角色 — 继承工厂 + 自定义角色")
    print("=" * 60)

    hall = quick_seminar(chat_fn=mock_chat)

    # 自定义角色
    hall.add(Role("周总编", "评", "内容战略与最终把关", "大局观强，长线思维"))
    hall.add(Role("吴翻译", "翻", "中英文翻译", "双语流利，地道自然"))

    print("现有角色：")
    for name, role in hall.roles.items():
        print(f"  {name} → 符号【{role.symbol_char}】 {role.expertise}")

    print(f"\n共 {len(hall.roles)} 个角色。使用 PipelineOrg 或 PanelOrg 自由组合。")


def demo_summary():
    """展示研讨厅日志。"""
    print("\n" + "=" * 60)
    print("【总】研讨厅日志 — hall.summary()")
    print("=" * 60)

    hall = quick_seminar(chat_fn=mock_chat)
    pipeline = quick_pipeline(hall)
    pipeline.execute("简要日志测试")

    print("\n" + hall.summary()[:300])


if __name__ == "__main__":
    demo_pipeline()
    demo_panel()
    demo_adversarial()
    demo_custom_roles()
    demo_summary()
    print()
