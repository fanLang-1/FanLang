# 凡语 FanLang

<p align="center">
  <img src="https://raw.githubusercontent.com/fanLang-1/FanLang/main/assets/banner.svg" alt="凡语 FanLang Banner" width="100%">
</p>

<p align="center" style="font-size:1.2em; color:var(--md-primary-fg-color);">
  <strong>用中文单字操控 AI，一行代码接入交互层。</strong><br>
  <em>AI interaction in Chinese characters — one import, one line.</em>
</p>

---

## 什么是凡语？

**凡语（FanLang）** 是一套面向 AI 应用开发者的交互层框架。它解决一个简单但重要的问题：

> **用户面对 AI 的空白输入框，不知道该说什么。**

凡语提供：

- 🀄 **25 个单字符号** — 用「写」「改」「翻」「问」等中文单字表达 AI 能力
- 🔄 **OODA 循环引擎** — Orient → Decide → Act → Observe，自动追问和结果优化
- 🏛️ **盗火者研讨厅** — 三种多智能体组织形态（Pipeline / Panel / Adversarial）
- 🔍 **QuickRAG** — 一行代码启动本地文档检索
- 📦 **三合一 pip 包** — 核心包 + Streamlit 插件 + LangChain 集成

```bash
pip install pyfanlang
```

---

## 三行代码上手

```python
from fanlang import get_symbol

sym = get_symbol("写")
print(f"{sym.emoji} {sym.char} — {sym.name_cn}")
# ✍️ 写 — 写作
```

---

## 谁应该用凡语？

| 如果你... | 凡语能帮你... |
|:--|:--|
| **开发 AI 应用**（Streamlit / Gradio / 网页） | 一行代码给用户加上能力菜单 |
| **搭建多智能体系统** | 三种组织形态即插即用 |
| **做 AI 产品原型** | 免去反复写 prompt 的麻烦 |
| **研究 AI 交互设计** | 符号体系提供了形式化基础 |

---

## 快速导航

<div class="grid cards" markdown>

-   :material-rocket-launch: **快速开始**
    ---
    安装、一分钟上手、符号体系、OODA 循环。

    [:octicons-arrow-right-24: 开始](getting-started/installation.md)

-   :material-puzzle: **组件**
    ---
    Streamlit 插件、LangChain 集成、QuickRAG、研讨厅。

    [:octicons-arrow-right-24: 查看组件](components/streamlit.md)

-   :material-file-document: **论文**
    ---
    组织形态学视角下的多智能体协作、研讨厅架构设计。

    [:octicons-arrow-right-24: 阅读论文](papers/paper-01.md)

-   :material-book-open-variant: **指南**
    ---
    项目语境、应用场景、架构决策、设计模式、路线图。

    [:octicons-arrow-right-24: 浏览指南](guide/context.md)

</div>
