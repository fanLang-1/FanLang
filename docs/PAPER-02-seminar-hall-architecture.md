# 盗火者研讨厅：架构、技术规格与设计权衡

## 一个基于组织形态学的 AI 多智能体协作框架

<p align="right"><em>盗火者研讨厅 · 技术报告 002 · 2026 年 7 月</em></p>

---

## 摘要

盗火者研讨厅（Prometheus Seminar Hall）是多智能体协作引擎 `fanlang.seminar` 的完整技术规格文档。本文描述其三层架构（角色层 / 组织形态层 / 元控制层）、核心类设计、关键设计权衡，并给出完整的 API 参考与使用模式。研讨厅的核心创新在于：将经典组织理论中的三类基本组织结构——流水线、评议制、对撞式——形式化为可复用的 Python 对象，并通过 OODA 循环实现组织形态的动态选择。

---

## 1. 设计原则

### 1.1 架构前提

1. **组织形态决定输出质量，而非模型参数。** 研讨厅的场景假设：7 个 1.5B 模型的角色 × 3 轮协作，在逻辑严密性上应当优于单个 7B 模型的单次输出。这一假设尚未被严格验证，但研讨厅的设计以此为目标。

2. **角色 > 模板。** 不是给一个 prompt 起名字就叫角色。角色需要：独立的人格参数、连续的记忆体、明确的职责边界。

3. **最小侵入性。** 研讨厅不要求用户理解任何多智能体理论。`quick_pipeline()` 和 `quick_adversarial()` 就是全部入口。想做更复杂的配置，才需要操作 Role 和 SeminarHall 的底层接口。

### 1.2 命名起源

"盗火者"取自希腊神话的普罗米修斯——盗取众神的火焰，带给凡人。在 AI 语境下，这隐喻了：将原本属于"大模型 + 专业 Prompt Engineer"的产出能力，通过组织形态学的结构化手段，降维到"任何人配置一波虚拟人就能获得"的水平。

"研讨厅"（Seminar Hall）取自钱学森 1992 年提出的"从定性到定量的综合集成研讨厅体系"——一个将专家群体、数据、信息与计算机技术有机结合的决策框架。本文的研讨厅是其 AI 实现：专家 → 虚拟角色，数据/信息 → LLM 知识 + RAG 记忆，计算机技术 → Python + Ollama。

---

## 2. 系统架构

### 2.1 三层分层

```
┌──────────────────────────────────────────────────────┐
│ Layer 3: 元控制层 (Meta-Control)                      │
│ ┌──────────────────────────────────────────────────┐ │
│ │         OODA 循环                                  │ │
│ │  Orient ──→ Decide ──→ Act ──→ Observe            │ │
│ │  (追问)    (选组织)    (执行)    (验收→回退)      │ │
│ └──────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────┤
│ Layer 2: 组织形态层 (Organizational Morphology)      │
│ ┌────────────┐  ┌────────────┐  ┌────────────────┐  │
│ │PipelineOrg │  │ PanelOrg   │  │AdversarialOrg  │  │
│ │ 串行接力    │  │ 并行评议    │  │ 正反对撞        │  │
│ │ n 角色顺序  │  │ n 角色并行  │  │ 2 角色交替     │  │
│ │ O(n) tokens │  │ O(n*k)     │  │ O(2r*k)        │  │
│ └────────────┘  └────────────┘  └────────────────┘  │
├──────────────────────────────────────────────────────┤
│ Layer 1: 角色层 (Role Pool)                          │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐     │
│ │王写手│ │李编辑│ │张校对│ │赵创意│ │孙批判│ ...  │
│ │  ✍️写 │ │  🔄改 │ │  🔍查 │ │  💡想 │ │  🔑解 │     │
│ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘     │
└──────────────────────────────────────────────────────┘
```

### 2.2 核心类关系

```
SeminarHall (角色池 + 讨论协调器)
    ├── roles: Dict[str, Role]
    ├── log: List[RoundResult]
    ├── chat_fn: Callable
    ├── discuss(role, message) → RoundResult
    └── summary() → str

Role (虚拟人)
    ├── name: str
    ├── symbol_char: str        ← 绑定凡语符号
    ├── expertise: str           ← 专长领域
    ├── personality: str         ← 性格参数
    ├── temperature: float       ← 创造性
    ├── memory: List[Dict]       ← 持久化记忆
    ├── system_prompt: str       ← 自动生成本
    ├── remember(content, meta)  ← 写入记忆
    └── recall(n) → str          ← 读取记忆

RoundResult (一轮发言)
    ├── role_name: str
    ├── content: str
    ├── round_num: int
    └── metadata: Dict

组织形态 (三种)
    PipelineOrg(hall, roles).execute(task) → {result, stages, rounds}
    PanelOrg(hall, panel, chief).execute(task) → {result, versions, synthesis}
    AdversarialOrg(hall, pro, con, judge).execute(task) → {result, transcripts}
```

### 2.3 数据流

```
用户输入
  │
  ▼
OODA.Orient: 追问 → 澄清需求
  │
  ▼
OODA.Decide: 选组织形态 → PipelineOrg/PanelOrg/AdversarialOrg(...)
  │
  ▼
org.execute(task)
  │
  ├── Pipeline: Role_A.discuss → Role_B.discuss → Role_C.discuss
  ├── Panel:    Role_A/B/C.discuss (并行) → Chief.discuss (融合)
  └── Adversarial: Pro.discuss ⇄ Con.discuss (N轮) → Judge.discuss
  │
  ▼
OODA.Observe: 评估质量 → 通过或回退
  │
  ▼
返回最终结果
```

---

## 3. 质量比较矩阵

基于理论分析（非实验验证），三种组织形态在不同维度上的预期表现：

| 维度 | 单次调用 | Pipeline | Panel | Adversarial |
|:--|:--|:--|:--|:--|
| 事实准确性 | 中 | 中→高 | 中 | 高 |
| 逻辑严密性 | 低 | 中 | 中 | 高 |
| 创意多样性 | 中 | 低 | 高 | 中 |
| 输出一致性 | 低（高方差） | 高 | 中→高 | 高 |
| Token 消耗 | 1× | 3× | 4-5× | 5-7× |
| 执行时间 | 1× | 3× | 1× (并行) | 5-7× |
| 适用任务 | 快速原型 | 写作/翻译 | 创意/方案 | 论证/决策 |

### 关键观察

- **Pipeline 降低方差**：编辑和校对环节消除写手的随机波动，使输出趋于稳定。
- **Panel 增加多样性**：并行产出确保不会掉入单一思路的局部最优。
- **Adversarial 逼近真值**：每轮攻击都剥除一层不坚固的论证，最终剩下的是经过反复检验的结论。

---

## 4. 角色人格设计规范

### 4.1 人格参数

每个 Role 的 `personality` 字段不是自由文本，而是结构化的**人格矢量**。推荐格式：

```
"dominant_trait/sub_trait, 语言风格, 行为倾向"
```

示例：
```
王写手: "流畅/生动, 口语化书面语, 偏好短句与并列结构"
李编辑: "挑剔/精准, 规范的新闻体, 删减>增添"
孙批判: "尖锐/逻辑, 简洁冷峻的质询风格, 质疑前提>质疑结论"
```

### 4.2 符号绑定规则

一个角色只能绑定一个凡语符号。符号决定了这个角色的**核心能力域**：

| 符号 | 适合角色 | 不擅长的领域 |
|:--|:--|:--|
| 写 | 撰稿人、内容输出 | 不是事实核查 |
| 改 | 编辑、润色 | 不是内容创作 |
| 查 | 事实核查、研究员 | 不是创意构思 |
| 想 | 创意策划、脑暴 | 不是执行细节 |
| 评 | 裁判、评审 | 不是进攻/辩论 |
| 解 | 逻辑分析、批判 | 不是建设性建议 |

### 4.3 角色组合原则

有效的组织不是任意角色堆砌，需要满足：

1. **最小完备性**：至少覆盖"产出→审视→裁决"三个职能
2. **无角色重叠**：两个相同符号的角色不增加价值
3. **对抗性互补**：写 vs 解，想 vs 评 —— 符号本身暗示了天然的对立关系

---

## 5. API 分级

### 5.1 入门级（零配置）

```python
from fanlang.seminar import (
    quick_seminar, quick_pipeline, quick_panel, quick_adversarial
)

hall = quick_seminar()

# 一行代码，三种模式
quick_pipeline(hall).execute("你的任务")
quick_panel(hall).execute("你的任务")
quick_adversarial(hall).execute("你的任务")
```

### 5.2 中级（自定义角色）

```python
from fanlang.seminar import SeminarHall, Role, PipelineOrg, AdversarialOrg

hall = SeminarHall(chat_fn=my_ollama_chat)

# 自定义角色
hall.add(Role("周主编", "评", "内容决策", temperature=0.3))
hall.add(Role("钱律师", "解", "法律论证", "严谨，逐条对照法条"))
hall.add(Role("赵总", "定", "商业判断", "务实，看投入产出比"))

# 自定义组织
org = AdversarialOrg(hall, pro_role="钱律师", con_role="赵总", judge_role="周主编")
result = org.execute("这个合同条款是否应当接受？")
```

### 5.3 高级（完全自定义）

```python
from fanlang.seminar import SeminarHall, Role, RoundResult

hall = SeminarHall()
hall.add(Role("..."))

# 手动编排讨论流程
result1 = hall.discuss(hall.get_role("甲"), "问题")
result2 = hall.discuss(hall.get_role("乙"), result1.content)
result3 = hall.discuss(hall.get_role("甲"), result2.content)

# 查看完整日志
print(hall.summary())
```

---

## 6. 局限性声明

1. **未经实验验证**。本文的效能论断基于组织形态学理论推导，尚未通过受控实验验证。尤其是"7 个 1.5B 角色 > 1 个 7B 模型"的假设。

2. **模型同质化**是所有三类组织的共同硬伤。真正的异质角色池需要不同模型不同温度不同上下文窗口，当前版本未完整实现。

3. **Token 经济性**。在实际使用中，Adversarial 模式可能比单次调用多消耗 7 倍 token，需权衡成本与收益。

4. **角色人格塌缩**。随着对话轮次增加，所有角色可能逐渐趋同——"编辑也变得像写手"。这是长期对话的共性问题，尚未在前 3 轮中得到充分观察。

---

## 7. 版本历史

| 版本 | 日期 | 变更 |
|:--|:--|:--|
| 0.1.0 | 2026-07 | 初始发布：SeminarHall, Role, PipelineOrg, PanelOrg, AdversarialOrg, quick_* |

---

## 参考文献

- 钱学森, 于景元, 戴汝为 (1990). "一个科学新领域——开放的复杂巨系统及其方法论." 《自然杂志》.
- Boyd, J. R. (1995). *The Essence of Winning and Losing.*
- Mintzberg, H. (1979). *The Structuring of Organizations.* Prentice-Hall.

---

<p align="center">
  <em>技术报告 002 · 盗火者研讨厅 · 凡语 FanLang · MIT 开源</em><br>
  <a href="https://github.com/desshu/FanLang">github.com/desshu/FanLang</a>
</p>
