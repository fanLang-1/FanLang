# OODA vs LangChain Chain: 两种AI交互范式的对决

> 当你写下 `prompt | model | StrOutputParser()` 时，你选择的是可预测性。
> 当你选择 OODA 循环时，你选择的是自适应质量。
> 这两种范式不该是对立的——它们应该是互补的。

---

## 一、引言

2023 年，LangChain 用 `|` 操作符重新定义了 AI 应用的构建方式。开发者终于可以用一种声明式、可组合的方式来编排 LLM 调用链：

```python
chain = prompt | model | StrOutputParser()
result = chain.invoke({"topic": "AI 趋势"})
```

简单、优雅、可预测。这就是 LangChain 表达式语言（LCEL）的魅力。

但问题也随之而来：**现实世界的 AI 任务不总是线性的。**

你要写一篇文章——第一版 LLM 输出太泛，你需要追问细节；第二版太长，需要精简；第三版风格不对，需要调整。这不是一条流水线，而是一个**迭代循环**。

于是有了 OODA。

凡语（FanLang）的 OODA 循环——Orient（定向）、Decide（决策）、Act（执行）、Observe（观察）——为 AI 交互提供了一种与 LCEL 截然不同的范式：**自适应的、反馈驱动的迭代循环**。

本文将从设计哲学、代码实现、适用场景三个维度，深入对比这两种范式的异同，并探讨如何在实际系统中取长补短。

---

## 二、LangChain Chain: 声明式流水线的美学

### 2.1 设计哲学

LCEL 的核心思想来自函数式编程：**每一个组件都是一个 `Runnable`，通过 `|` 操作符组合成 DAG（有向无环图）。**

```python
# LCEL 链：从输入到输出，路径固定
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
```

这条链一旦定义，执行路径就确定了。`retriever` 输出 `context`，`prompt` 填入模板，`model` 生成文本，`StrOutputParser` 解析为字符串——像工厂流水线一样，每个工位做固定的事情。

### 2.2 优点

- **可预测性高**：给定相同输入，链的输出是确定的（在 temperature=0 时）。这对于测试、调试、监控至关重要。
- **可组合性强**：`|` 操作符让链的构建像管道一样直观，可以自由组合 retriever、prompt、model、parser。
- **内置观察能力**：LangSmith 可以追踪每一步的输入输出，方便调试和优化。

### 2.3 局限

LCEL 擅长的是**确定性流程**——即你知道每一步应该做什么，且步骤数量是固定的。

但在以下场景中，它会显得力不从心：

- **写作任务**：第一版输出可能方向不对，需要重新定向
- **代码生成**：生成的代码可能有 bug，需要调试和重试
- **分析任务**：初步分析可能遗漏关键点，需要补充数据
- **翻译任务**：译文可能太生硬，需要根据语境调整风格

这些任务的共同特征是：**你无法预先知道需要多少步才能达到满意的质量。**

```python
# 用 LCEL 表达"写文章 → 不满意 → 重写"循环
# 你需要在链外手动写 while 循环
chain = prompt | model | StrOutputParser()
result = chain.invoke(...)

while not is_satisfied(result):
    refine_prompt = PromptTemplate.from_template("改进：{text}")
    result = (refine_prompt | model | StrOutputParser()).invoke({"text": result})
```

注意看：这里已经没有 `|` 的优雅了。反馈循环需要你自己管理状态、判断条件和迭代次数。

这就是痛点所在：**LCEL 可以表达 DAG，但很难表达循环。**

---

## 三、OODA 循环: 自适应迭代的哲学

### 3.1 设计哲学

OODA 循环最初是军事战略家 John Boyd 提出的决策框架，用于描述战斗机飞行员在空战中的决策过程。它的核心思想是：**在不确定的环境中，快速循环比完美计划更重要。**

凡语将其引入 AI 交互领域，形成了一套四步循环：

```
          ┌─────────────┐
          │   Orient    │  ← 理解需求、澄清歧义
          │   (定向)     │
          └──────┬──────┘
                 │
          ┌──────▼──────┐
          │   Decide    │  ← 选择策略、规划步骤
          │   (决策)     │
          └──────┬──────┘
                 │
          ┌──────▼──────┐
          │    Act      │  ← 执行生成、调用工具
          │   (执行)     │
          └──────┬──────┘
                 │
          ┌──────▼──────┐
          │  Observe    │  ← 评估质量、收集反馈
          │   (观察)     │
          └──────┬──────┘
                 │
          (未满意) │   (已满意 → 输出)
                 │
          ┌──────▼──────┐
          │   Orient    │  ← 基于反馈重新定向
          │   (下一轮)    │
          └─────────────┘
```

### 3.2 核心区别: 不是流水线，是反馈回路

与 LCEL 的最大区别在于：**OODA 不认为 LLM 的第一次输出就是最终答案。** 每一次输出都是"暂定的"——它需要经过 Observe 阶段的评估，如果质量不达标，就会再次进入 Orient 阶段，开启新一轮循环。

来看一个具体的例子：

```python
from fanlang import OODAContext

context = OODAContext(llm=llm)
context.set_symbol("写")  # 设定能力符号

# 第一轮执行
context.orient("帮我写一篇关于 AI 代理的文章")
context.decide()     # 选择策略：先列提纲，再展开
context.act()        # 生成初稿
context.observe()    # 自我评估："文章结构清晰但缺少案例"

# 第二轮——不需要用户手动输入
# OODA 自动基于 Observe 的反馈重新 Orient
context.orient("补充真实世界的 AI 代理案例")
context.decide()     # 策略：搜索案例并插入
context.act()        # 生成补充内容
context.observe()    # 评估："现在内容充实度达标"

# 输出最终结果
print(context.result)
```

### 3.3 OODA 的关键机制

凡语的 OODA 实现包含以下几个关键机制：

**1. 自动澄清（Orient 阶段）**

当用户输入模糊时，OODA 会自动追问缺失的信息：

```
用户: "写篇文章"
系统 -> Orient: "请问主题是什么？目标受众是谁？大概多少字？"
```

这解决了 LCEL 链中"垃圾进垃圾出"的问题——模型不是被动地接受输入，而是**主动确保输入质量**。

**2. 策略选择（Decide 阶段）**

根据任务类型，OODA 选择不同的执行策略：

- 写作任务：提纲 → 分段生成 → 统一风格
- 代码任务：架构 → 编写 → 测试 → 修复
- 分析任务：数据收集 → 初步分析 → 深化 → 总结

**3. 自我评估（Observe 阶段）**

这是 OODA 的核心创新：**系统自己判断输出质量。**

```python
class OODAContext:
    def observe(self) -> EvaluationResult:
        eval_prompt = """评估以下输出质量：
        任务：{task}
        输出：{output}
        
        请检查：
        1. 是否完整回答了问题？
        2. 是否有逻辑缺陷？
        3. 是否缺乏具体细节？
        
        返回评分(1-5)和改进建议。"""
        
        result = llm.invoke(eval_prompt)
        return EvaluationResult(
            score=result.score,
            suggestions=result.suggestions,
            needs_revision=result.score < 4
        )
```

如果评分低于阈值，系统自动进入下一轮循环——不需要用户手动触发。

---

## 四、正面交锋: 范式对比

### 4.1 抽象层次

| 维度 | LangChain LCEL | 凡语 OODA |
|------|---------------|-----------|
| 范式 | 声明式 | 命令式 |
| 流程 | 静态 DAG | 自适应循环 |
| 组合方式 | `\|` 操作符 | 四阶段上下文 |
| 状态管理 | 显式（PassThrough / ItemGetter） | 隐式（Context 自动维护） |
| 错误恢复 | 需手动处理 | 内置重试和回退 |
| 不确定性 | 低（路径固定） | 高（路径自适应） |
| 适合任务 | 确定性流程 | 开放性创作 |

### 4.2 代码对比

**场景：写一篇产品分析报告**

```python
# ── LangChain 方式 ──
prompt = ChatPromptTemplate.from_template(
    "写一篇关于 {product} 的产品分析报告，{constraints}"
)
chain = prompt | model | StrOutputParser()
report = chain.invoke({
    "product": "ChatGPT",
    "constraints": "1000字左右，包含竞品对比"
})
# 如果不够好，你得在外面手动重来
```

```python
# ── 凡语 OODA 方式 ──
ctx = OODAContext(llm=llm)
ctx.orient("写一篇关于 ChatGPT 的产品分析报告")
# 系统主动追问："目标读者？侧重维度？)"
ctx.act()          # 生成初稿
obs = ctx.observe()  # 自我评估：评分 3/5，缺少数据支撑
ctx.orient(obs.suggestions)  # 自动定向：补充数据
ctx.act()          # 生成改进版
ctx.observe()      # 评分 4.5/5 → 输出
```

### 4.3 适用场景决策树

```
你的任务是什么？
│
├─ 确定性流程（输入 → 固定步骤 → 输出）
│   ├─ 数据提取 / 分类 / 标注 → LangChain LCEL
│   ├─ 简单的 Q&A → LangChain LCEL
│   └─ 结构化输出（JSON Schema）→ LangChain LCEL
│
├─ 开放性创作（输入模糊 → 迭代改进 → 高质量输出）
│   ├─ 写作 / 翻译 / 改写 → OODA
│   ├─ 代码生成 / 调试 → OODA
│   └─ 分析 / 研究 / 头脑风暴 → OODA
│
└─ 混合场景
    └─ OODA 内部包含 LCEL 子链 → 两者结合
```

---

## 五、珠联璧合: OODA + LangChain 的混合架构

这是最有趣的部分：**OODA 和 LCEL 不是非此即彼的。** 在凡语的实现中，OODA 的每个阶段内部可以调用 LCEL 链。

### 5.1 Act 阶段使用 LCEL

```python
from fanlang import OODAContext
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

ctx = OODAContext(llm=llm)

# OODA 的 Act 阶段使用 LCEL 链
ctx.set_action("write", lambda context: (
    ChatPromptTemplate.from_template(
        "按以下提纲写文章:\n{outline}\n\n风格: {style}"
    )
    | model
    | StrOutputParser()
).invoke({
    "outline": context.get("outline"),
    "style": context.get("style", "专业")
}))
```

### 5.2 Observe 阶段使用 LCEL

```python
# Observe 阶段也是 LCEL 链
ctx.set_observer(lambda context: (
    ChatPromptTemplate.from_template(
        """评估以下文章质量:
        {content}
        
        评分标准:
        - 完整性 (1-5)
        - 准确性 (1-5)
        - 可读性 (1-5)
        
        输出 JSON: {{"scores": {{...}}, "needs_revision": bool}}"""
    )
    | model
    | JsonOutputParser()
).invoke({"content": context.last_output}))
```

### 5.3 最佳实践: 外层 OODA + 内层 LCEL

在实际应用中，推荐这样的分层架构：

```
外层 OODA（质量循环）
  │
  ├─ Orient: 用户意图理解 + 需求澄清
  ├─ Decide: 策略选择（按任务类型匹配合适的 LCEL 链）
  ├─ Act: 调用 LCEL 链执行（prompt | model | parser）
  └─ Observe: 质量评估（也是 LCEL 链）
       │
       └─ 不达标 → 回到 Orient（基于反馈重新定向）
```

这种架构的优势在于：
- **外层**负责"做什么"——通过 OODA 的反馈循环确保整体质量
- **内层**负责"怎么做"——通过 LCEL 的可组合性确保每一步的执行效率

---

## 六、深层洞察: 两种世界观

归根结底，LCEL 和 OODA 的差异不只是技术选择——它们是**两种 AI 交互世界观的体现**。

**LCEL 的世界观**: "如果你能清晰地描述问题，LLM 就能给出正确的答案。"

这对应的是传统软件工程的"规约式"思维：先定义好输入、输出、流程，然后执行。它在确定性场景中完美工作，但在面对模糊的、开放式的任务时，把"清晰化"的责任留给了开发者或用户。

**OODA 的世界观**: "问题本身就是在对话中逐渐清晰的。第一次回答只是对话的开始，不是结束。"

这对应的是"迭代式"思维：承认 LLM 的不确定性，用反馈循环来逼近高质量输出。它把"清晰化"作为系统的一部分——系统主动追问、自我评估、自动改进。

**更深一层：OODA 是对"LLM 输出即最终答案"这一默认假设的否定。**

当你使用 LCEL 时，你默认认为 `model` 的输出就是你要的最终结果。当你使用 OODA 时，你默认认为 `model` 的输出是"暂定的"——它需要经过评估、可能需要改进。

这不是说哪个更好——而是说**不同的假设适用于不同的问题**。

```
确定性任务 → 输出就是答案 → LCEL
开放性任务 → 输出是草稿 → OODA
```

---

## 七、总结: 如何选择？

### 选择 LangChain LCEL 当：
- 你的任务流程是确定的、已知的
- 你需要高吞吐量和低延迟
- 测试和可观测性是首要关注点
- 输入质量由上游保证

### 选择凡语 OODA 当：
- 你的任务需要多轮迭代才能达到高质量
- 用户输入可能模糊或不完整
- 你希望系统能自我评估和改进
- 质量比速度更重要

### 两者结合当：
- 复杂的 AI 应用通常需要两者的组合
- 外层 OODA 负责质量和用户体验
- 内层 LCEL 负责高效的确定性执行

---

## 八、试试看

```bash
pip install pyfanlang
```

```python
from fanlang import OODAContext
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()
ctx = OODAContext(llm=llm)

# 试试开放性任务
ctx.orient("写一个 Python 脚本，分析我的 CSV 文件")
result = ctx.run(max_loops=3)

print(result)
# OODA 会自动澄清需求 → 生成 → 评估 → 改进
```

---

**OODA 不是替代 LCEL——它是 LCEL 的上层抽象。** 它用反馈循环包裹确定性执行，让 AI 应用在保持效率的同时，获得了自我改进的能力。

如果 LCEL 是 AI 应用的"肌肉"（高效执行），那 OODA 就是"大脑"（知道什么时候该做什么、什么时候该重来）。

[GitHub: fanLang-1/FanLang](https://github.com/fanLang-1/FanLang)

[GitCode: fanLang-1/FanLang](https://gitcode.com/fanLang-1/FanLang)

MIT 开源。欢迎 Star、Issue、PR。
