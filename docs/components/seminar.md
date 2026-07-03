# 盗火者研讨厅

三种多智能体组织形态，即插即用。

## Pipeline（流水线）

串行执行：写手 → 编辑 → 校对

```python
from fanlang.seminar import quick_seminar, quick_pipeline

hall = quick_seminar()
pipeline = quick_pipeline(hall)

result = pipeline.execute("写一篇科普文章")
print(result["result"])
```

## Panel（评议制）

并行产出 + 主编汇总

```python
from fanlang.seminar import quick_panel

hall = quick_seminar()
panel = quick_panel(hall)

result = panel.execute("想 5 个宣传口号")
print(f"各版本：{result['versions']}")
print(f"融合：{result['result']}")
```

## Adversarial（对撞式）

正方 vs 反方 → 裁判裁决

```python
from fanlang.seminar import quick_adversarial

hall = quick_seminar()
adv = quick_adversarial(hall)

result = adv.execute("本地 AI 还是云端 AI？")
print(f"裁决：{result['result']}")
```

## 自定义角色

```python
from fanlang.seminar import Role, SeminarHall

hall = SeminarHall(chat_fn=my_chat)
hall.add(Role("周总编", "评", "内容战略", "大局观强"))
hall.add(Role("吴翻译", "翻", "中英翻译", "双语流利"))
```

## 预制角色

| 角色 | 符号 | 专长 |
|:--|:--|:--|
| 王写手 | 写 | 写作内容产出 |
| 李编辑 | 改 | 内容修改润色 |
| 张校对 | 查 | 事实校验勘误 |
| 赵创意 | 想 | 灵感创意发散 |
| 刘顾问 | 问 | 专业知识问答 |
| 孙批判 | 评 | 反向论证批评 |
| 陈裁判 | 理 | 总结裁决收口 |
