# 为什么你的 AI 工具需要一个能力菜单（而不是一个空输入框）

> 全世界的 AI 聊天界面都长一个样：一个空白文本框。
> 这就是问题所在。

---

## 一、空白输入框的问题

打开 ChatGPT。空白框。

打开 DeepSeek。空白框。

打开 Kimi。空白框。

打开你自己用 Streamlit 搭的 AI 工具。空——白——框。

这个设计的潜台词是："你什么都可以问我，请自由地打字吧。"

但实际效果是：用户在空白框前发呆 30 秒，打了一行字，得到结果，发现不是自己想要的，不知道怎么改进，关掉窗口。

**空白输入框不是自由，是负担。** 它把"AI 能做什么"的认知负担全部甩给了用户。

---

## 二、菜单的力量

想想我们日常用的其他工具。

打开 Photoshop：工具栏上一排图标——画笔、橡皮擦、裁剪、文字……每个图标背后是一个明确的能力。

打开 Excel：顶栏上一排菜单——公式、数据、审阅、视图……你不用记住所有函数名，知道"公式"栏里能找到就够了。

打开任何一个设计良好的软件，你看到的是一个 ** 能力菜单 **，而非一个写着"想做啥？"的空白框。

AI 工具凭什么例外？

---

## 三、凡语：AI 的能力菜单

凡语（FanLang）不是一个产品。它是一套**可嵌入的能力菜单体系**——你可以把它想象成"AI 世界的 Ant Design 按钮组"。

核心概念：25 个汉字，每个代表一个 AI 能力。

```
写 ✍️   改 🔄   翻 🌐   总 📝   问 ❓   画 🎨   想 💡
解 🔑   教 📖   比 ⚖️   查 🔍   理 🗂️
编 💻   转 🔀   算 🔢   记 🧠   定 ⏰   说 🗣️   试 🧪   评 ⭐
阅 📖   空 🚀   止 🛑   兼 🤝   或 🔀
```

用户不需要理解"prompt engineering"、"chain-of-thought"、"few-shot prompting"——他们只需要认识自己从小学的汉字。

---

## 四、不只是按钮——OODA 循环

菜单解决了"用户不知道 AI 能做什么"的问题。但还有一个问题：**用户说了想做什么，但说得很模糊。**

凡语的 OODA 循环处理这个问题：

```
用户: [写] 帮我写点东西

Orient: "什么类型？公众号文章还是述职报告？主题是什么？大约多少字？"

用户: 述职报告，500 字左右，我是产品经理

Decide: 采用"结构化生成"策略，查询述职报告模板

Act: 生成报告

Observe: "看起来怎么样？需要调整部分内容吗？"

用户: 第二段加点数据支撑

→ 重新生成 → 满意 ✓
```

**不需要用户学 prompt engineering。** 系统自然会追问他缺少的信息。

---

## 五、一行代码接入

凡语是给开发者的，不是给终端用户的。接入方式：**一行 import。**

```python
# Streamlit 项目
from fanlang_streamlit import render_symbol_bar

symbol = render_symbol_bar(["写", "改", "翻", "总", "问", "查", "比", "理"])
```

```python
# LangChain 项目  
from fanlang_langchain import OODAAgent

agent = OODAAgent(llm=my_llm, tools=[...])
result = agent.run(user_input, symbol_char="写")
```

```python
# 任何 Python 项目
from fanlang import Terminology

Terminology.explain("RAG")  # "检索增强生成"
```

---

## 六、这玩意儿跟竞品有什么区别？

坦白说：豆包、DeepSeek、Kimi 已经很好用了。它们不需要"凡语"来帮用户写作。

但开源 AI 项目需要。

LangChain、LlamaIndex、Dify、Open-WebUI、Quivr……这些项目的 UI 层都在重复造轮子——每个项目的开发者都在自己写"怎么让用户更好地跟 AI 交互"。

凡语做的是：**把这件事抽象成一个标准组件，让所有开源 AI 项目共享一套交互设计语言。**

就像 React 没发明 UI，但它提供了组件化——让前端开发者不用从头写按钮。

---

## 七、试试看

```bash
pip install fanlang
```

```python
from fanlang import Symbol
for s in Symbol.get_core():
    print(f"{s.emoji} {s.char} — {s.name}: {s.description}")
```

输出：

```
✍️ 写 — 写作: 写文章、写报告、写文案  
🔄 改 — 改写: 修改风格、语气、长度  
🌐 翻 — 翻译: 中英互译，自然流畅  
📝 总 — 总结: 提炼核心要点  
❓ 问 — 问答: 回答各种问题  
🔍 查 — 检索: 搜索信息，找资料  
⚖️ 比 — 对比: 多维度对比分析  
🗂️ 理 — 整理: 分类、排序、结构化
```

---

[GitHub: desshu/FanLang](https://github.com/desshu/FanLang)

[GitCode: desshu/FanLang](https://gitcode.com/desshu/FanLang)

MIT 开源。给个 Star ⭐
