# pyfanlang

<p align="center">
  <img src="../assets/banner.svg" alt="凡语 FanLang Banner" width="80%">
</p>

<p align="center">
  <a href="https://pypi.org/project/pyfanlang/"><img src="https://img.shields.io/pypi/v/pyfanlang?color=blue" alt="PyPI"></a>
  <a href="https://github.com/fanLang-1/FanLang"><img src="https://img.shields.io/badge/source-GitHub-blue" alt="GitHub"></a>
</p>

凡语 FanLang — AI interaction in Chinese characters.

## 安装

```bash
pip install pyfanlang
```

## 一分钟上手

```python
from fanlang import get_symbol, get_all_symbols

# 获取符号
s = get_symbol("写")
print(f"{s.emoji} {s.char}  {s.name_cn} — {s.description}")
# ✍️ 写  写作 — 写作创作与内容生产

# 列出所有符号
all_symbols = get_all_symbols()
print(f"共 {len(all_symbols)} 个符号")

# OODA 循环
from fanlang import OODA
ooda = OODA()
result = ooda.run("帮我写一篇科普文章", symbol_char="写")

# 盗火者研讨厅
from fanlang.seminar import quick_seminar, quick_pipeline
hall = quick_seminar()
pipeline = quick_pipeline(hall)
result = pipeline.execute("写一篇关于 AI 的文章")

# QuickRAG
from fanlang import QuickRAG
rag = QuickRAG()
rag.add_documents("./docs")
answer = rag.query("什么是深度学习？")
```

## 包结构

| 包 | pip 安装 | 用途 |
|:--|:--|:--|
| `pyfanlang` | `pip install pyfanlang` | 核心包 |
| `pyfanlang-streamlit` | `pip install pyfanlang-streamlit` | Streamlit 插件 |
| `pyfanlang-langchain` | `pip install pyfanlang-langchain` | LangChain 集成 |

## License

MIT
