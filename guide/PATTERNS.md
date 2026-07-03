# 凡语 · 可复用模式库

> 从凡语开发过程中沉淀的代码模式、设计经验、常见陷阱。
> 可直接复制到新场景。

---

## 【编】代码模式

### 模式 1: 研讨会一行启动

```python
# ✅ 这样做
from fanlang.seminar import quick_seminar, quick_pipeline

hall = quick_seminar()
result = quick_pipeline(hall).execute("你的任务")

# ❌ 不要这样做
hall = SeminarHall()
hall.add(Role("王写手", "写", ...))
hall.add(Role("李编辑", "改", ...))
# ... 手动配 5+ 个角色
p = PipelineOrg(hall, ["王写手", "李编辑", ...])
```
**为什么**: quick_* 工厂封装了 7 个角色的配置。只在需要定制时走底层。

### 模式 2: 自定义角色时只改差异部分

```python
# ✅ 这样做
hall = quick_seminar()
hall.add(Role("周主编", "评", "内容战略", "大局观，长线思维"))
# 周主编替代或补充陈裁判

# ❌ 不要这样做
hall = SeminarHall()
# 重新手动配置全部 7 个角色
```
**为什么**: 继承工厂，避免重复。

### 模式 3: chat_fn 注入

```python
# ✅ 测试/演示环境用 mock
def mock_chat(system, user):
    return f"[{system[:20]}...] 收到: {user[:50]}"

hall = SeminarHall(chat_fn=mock_chat)

# ✅ 生产环境用 Ollama
hall = SeminarHall()  # 默认就是 Ollama

# ✅ 自定义模型
def deepseek_chat(system, user):
    return requests.post("http://localhost:11434/api/chat", json={
        "model": "deepseek-r1:1.5b",
        "messages": [...],
    }).json()["message"]["content"]

hall = SeminarHall(chat_fn=deepseek_chat)
```
**为什么**: SeminarHall 不绑定特定 LLM 实现，测试和切换极方便。

### 模式 4: 角色异质化（关键）

```python
# ✅ 不同温度产生认知多样性
hall.add(Role("激进派", "想", "创意", temperature=0.9))
hall.add(Role("保守派", "想", "创意", temperature=0.3))

# ❌ 相同 temperature 的同类角色 = 同质化输出
```

### 模式 5: OODA 已有 4 个阶段可直接复用

```python
# fanlang.ooda 原始模块
from fanlang.ooda import OODA

ooda = OODA(agent_func=my_chat_fn)
result = ooda.run("帮我写点东西")

# 等价于——
# Orient: 追问澄清
# Decide: 选策略
# Act: 调用LLM
# Observe: 评估结果
```

---

## 【理】设计经验

### 经验 1: 小模型需要更多组织

1.5B 模型单次输出方差大 → 用 Pipeline 降低方差。7B+ 模型单次已经不错 → Pipeline 收益递减。**模型越小，组织结构越重要。**

### 经验 2: 不要所有任务都用多角色

快速问答、简单翻译、格式转换——单次 LLM 调用即可。启动研讨厅的门槛：**任务复杂度 ≥ 需要两个人协作才能做好的事**。

### 经验 3: 角色同质化是第一杀手

所有角色底层同一个模型时，流水线的第二环往往会"同意"第一环的输出而非真正改进。缓解方案：
- 不同 temperature (0.3 vs 0.9)
- 不同系统 prompt 风格
- 不同模型 (猎手 vs 智囊)

### 经验 4: 研讨厅日志是宝藏

`hall.summary()` 输出的讨论记录，比最终结果更有价值——它记录了思考过程。**日志本身可以作为下一次研讨厅的输入。**

---

## 【改】常见陷阱

| 陷阱 | 表现 | 修复 |
|:--|:--|:--|
| 过度组织化 | 简单翻译用了 Panel（3角色并行） | 先判复杂度，再选组织 |
| 角色职责模糊 | 编辑也在写内容、校对也在改文风 | 每个角色只能做一个符号的事 |
| 无终止条件 | Adversarial 模式无限循环 | max_rounds=2（1立论+1反驳+裁决） |
| chat_fn 耦合 | 直接在 seminar.py 里硬编码 Ollama | 构造函数注入 |

---

## 【记】已验证的有效配置

### 写作质量最高的配置

```python
hall = quick_seminar()
# 提高写手温度增加创造力
hall.get_role("王写手").temperature = 0.85
# 降低编辑温度增加精确度
hall.get_role("李编辑").temperature = 0.3
PipelineOrg(hall, ["王写手", "李编辑", "张校对"]).execute(task)
```

### 决策最严密的配置

```python
hall = quick_seminar()
# 批判角色更尖锐
hall.get_role("孙批判").personality = "极其尖锐、逻辑至上、不留情面"
# 裁判更冷静
hall.get_role("陈裁判").personality = "绝对中立、只看证据、不预设立场"
AdversarialOrg(hall, "王写手", "孙批判", "陈裁判", max_rounds=2).execute(task)
```

### 创意最大化的配置

```python
hall = quick_seminar()
# 三个创意角色，不同温度和性格
hall.add(Role("赵创意", "想", "脑洞创意", "天马行空", temperature=0.95))
hall.add(Role("钱务实", "想", "务实创意", "可落地", temperature=0.3))
hall.add(Role("孙跨界", "想", "跨领域创意", "打破常规", temperature=0.7))
PanelOrg(hall, ["赵创意", "钱务实", "孙跨界"], "陈裁判").execute(task)
```
