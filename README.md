# 凡语 FanLang

<p align="center">
  <img src="assets/banner.svg" alt="凡语 FanLang Banner" width="100%">
</p>

<p align="center">
  <strong>用中文单字操控 AI，一行代码接入交互层。</strong><br>
  <em>AI interaction in Chinese characters — one import, one line.</em>
</p>

<p align="center">
  <a href="#快速开始"><strong>快速开始</strong></a> ·
  <a href="#凡语解决了什么"><strong>为什么凡语</strong></a> ·
  <a href="#组件"><strong>组件</strong></a> ·
  <a href="#安装"><strong>安装</strong></a> ·
  <a href="https://fanlang-1.github.io/FanLang/"><strong>文档站</strong></a>
</p>

<p align="center">
  <a href="https://pypi.org/project/pyfanlang/"><img src="https://img.shields.io/pypi/v/pyfanlang?color=blue&label=pyfanlang" alt="PyPI"></a>
  <a href="https://pypi.org/project/pyfanlang-streamlit/"><img src="https://img.shields.io/pypi/v/pyfanlang-streamlit?color=blue&label=pyfanlang-streamlit" alt="PyPI"></a>
  <a href="https://pypi.org/project/pyfanlang-langchain/"><img src="https://img.shields.io/pypi/v/pyfanlang-langchain?color=blue&label=pyfanlang-langchain" alt="PyPI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT"></a>
  <a href="https://github.com/fanLang-1/FanLang/actions"><img src="https://img.shields.io/github/actions/workflow/status/fanLang-1/FanLang/ci.yml?branch=main" alt="CI"></a>
</p>

---

## 凡语解决了什么

**全世界的 AI 交互界面长一个样：一个空输入框。** 用户不知道 AI 能做什么，不知道怎么表达需求，不知道下次怎么复现好结果。

凡语提供一套**可嵌入的能力菜单**——不是给普通用户装一个软件，而是给开源 AI 项目开发者一行 import，让他们的用户不再面对空白输入框茫然打字。

| 你的项目 | 接入凡语后 |
|:--|:--|
| `st.text_input("请输入问题")` | `render_symbol_bar()` → 8 个设计好的能力按钮 |
| 用户写完，不满意，不知道怎么改 | OODA 循环自动追问 + 反馈 → 结果迭代优化 |
| 项目里到处是英文 AI 术语 | `explain("embedding")` → "向量嵌入" |

---

## 组件

凡语是一个 **monorepo**，包含三个独立的 pip 包。各取所需，不互相强制依赖。

### `fanlang` — 核心包

**[symbols] [ooda] [rag] [terminology] [wolfpack]**

```bash
pip install fanlang
```

```python
from fanlang import Symbol, OODA, Terminology

# 获取符号定义
sym = Symbol.get("写")  # Symbol(char='写', emoji='✍️', name='写作', category='内容创作')

# OODA 循环引擎
ooda = OODA(agent_func=my_chat_fn)
result = ooda.run("帮我写点东西")  # 自动追问→执行→反馈，最多5轮

# 术语翻译
Terminology.explain("prompt")  # "提示词"
```

### `fanlang-streamlit` — Streamlit 插件

**一行代码渲染能力按钮栏。**

```bash
pip install fanlang-streamlit
```

```python
from fanlang_streamlit import render_symbol_bar

selected = render_symbol_bar(["写","改","翻","总","问","查","比","理"])
if selected:
    st.write(f"用户选择了：{selected}")
```

---

### `fanlang-langchain` — LangChain 集成

**OODA Agent + FanLang Retriever 节点。**

```bash
pip install fanlang-langchain
```

```python
from fanlang_langchain import OODAAgent

agent = OODAAgent(llm=my_llm, tools=[...])
result = agent.run("整理这些资料并做对比分析")
```

---

## 安装

```bash
# 核心包
pip install fanlang

# Streamlit 插件（需要 streamlit）
pip install fanlang-streamlit

# LangChain 集成（需要 langchain）
pip install fanlang-langchain

# 全部安装
pip install fanlang[full]
```

---

## 5 分钟 Demo

```python
# demo.py — 一个带凡语符号栏的 Streamlit AI 聊天应用

import streamlit as st
from fanlang_streamlit import render_symbol_bar
from fanlang.ooda import OODA

st.title("📚 我的 AI 助手")

# 一行代码：渲染能力符号栏
symbol = render_symbol_bar(["写", "改", "翻", "总", "问", "查", "比", "理"])

if symbol:
    user_input = st.chat_input(f"[{symbol}] 请输入...")
    if user_input:
        ooda = OODA(agent_func=your_chat_fn)
        result = ooda.run(user_input, symbol_char=symbol)
        st.write(result)
```

---

## 符号体系一览

### 核心符号（8 个）

| 符号 | 名称 | 功能 |
|:--|:--|:--|
| ✍️ 写 | 写作 | 写文章、报告、文案 |
| 🔄 改 | 改写 | 修改风格、语气、长度 |
| 🌐 翻 | 翻译 | 中英互译 |
| 📝 总 | 总结 | 提炼核心要点 |
| ❓ 问 | 问答 | 回答各类问题 |
| 🔍 查 | 检索 | 搜索信息 |
| ⚖️ 比 | 对比 | 多维度对比分析 |
| 🗂️ 理 | 整理 | 分类、排序、结构化 |

### 完整符号体系

25 个单字符号 × 36 个双词符号 × 12 个语法符号 = **一套完整的 AI 交互语言**

→ [完整符号表](https://github.com/desshu/FanLang/wiki)

---

## OODA 循环

凡语的内核——一个源自军事决策的 4 层交互框架：

```
问 → 追问问清晰 → 策略选定 → 执行 → 不滿意？重來一遍
Orient    →     Decide    →   Act   →   Observe
```

- **Orient（理解）**：用户说了"帮我写点东西"→ 追问"什么类型？什么主题？多长？"
- **Decide（决定）**：选择策略（直接生成 / 先检索 / 多轮对话）
- **Act（执行）**：调用 LLM 或工具
- **Observe（观察）**：检查结果质量，"满意吗？哪里需要调整？"

最多循环 5 次。不需要用户会写 prompt。

---

## 仓库结构

```
FanLang/
├── fanlang/                # 核心 pip 包
│   ├── symbols.py          # 完整符号体系
│   ├── ooda.py             # OODA 循环引擎
│   ├── rag.py              # QuickRAG
│   ├── terminology.py      # 英中术语映射
│   └── wolfpack.py         # 狼群模型路由器
├── fanlang-streamlit/      # Streamlit 插件
│   └── components.py       # render_symbol_bar() 等
├── fanlang-langchain/      # LangChain 集成
│   ├── ooda_agent.py       # OODAAgent
│   └── retriever.py        # FanLangRetriever
├── examples/               # 5 个 Demo 项目
├── apps/                   # 独立应用（Streamlit）
├── docs/                   # 文档源文件
└── README.md               # 本文件
```

---

## 许可证

MIT © 2026 [desshu](https://github.com/desshu)

---

## 致谢

- [Ollama](https://ollama.com) — 本地 LLM 推理引擎
- [Streamlit](https://streamlit.io) — Python Web UI 框架
- [LangChain](https://langchain.com) — LLM 应用框架
- [ChromaDB](https://trychroma.com) — 向量数据库
