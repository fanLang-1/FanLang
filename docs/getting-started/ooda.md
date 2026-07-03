# OODA 循环

凡语的内核——一个源自军事决策的 4 层交互框架。

## 流程

```
Orient（理解） → Decide（决策） → Act（执行） → Observe（评估）
```

- **Orient**: 用户输入模糊时自动追问（"什么类型？什么主题？多长？"）
- **Decide**: 根据任务类型选择合适的策略
- **Act**: 执行生成/检索/对话操作
- **Observe**: 评估结果质量，不满足则循环

最多 5 轮迭代。

## 代码示例

```python
from fanlang import OODA

ooda = OODA(
    max_iterations=3,
    agent_func=my_chat_fn  # 自定义 LLM 调用
)

result = ooda.run("帮我写点东西", symbol_char="写")
# 自动追问 → 执行 → 反馈，最多 3 轮
```

## 输出

```python
{
    "status": "done",      # 或 "clarify"
    "result": "...",       # 最终结果
    "iterations": 2,       # 迭代轮数
    "satisfied": True,     # 是否满意
    "feedback": "质量好",   # 评估反馈
}
```

## 流式输出

```python
for chunk in ooda.run_stream("解释下神经网络", symbol_char="解"):
    if chunk["status"] == "streaming":
        print(chunk["content"], end="")
```
