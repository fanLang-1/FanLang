# 一分钟上手

## 符号查询

```python
from fanlang import get_symbol, get_all_symbols

# 单个符号
sym = get_symbol("写")
print(f"{sym.emoji} {sym.char} — {sym.name_cn}: {sym.description}")
# ✍️ 写 — 写作: 写作创作与内容生产

# 所有符号
all_syms = get_all_symbols()
print(f"共 {len(all_syms)} 个符号")

# 按分类
syms = get_all_symbols(category="内容生产")
```

## OODA 循环

```python
from fanlang import OODA

ooda = OODA(max_iterations=3)
result = ooda.run("帮我写一篇科普文章", symbol_char="写")
print(result["result"])
```

## QuickRAG

```python
from fanlang import QuickRAG

rag = QuickRAG()
rag.add_documents("./my_docs")
result = rag.query("什么是机器学习？")
print(result[0])
```

## 盗火者研讨厅

```python
from fanlang.seminar import quick_seminar, quick_pipeline

hall = quick_seminar()
pipeline = quick_pipeline(hall)
result = pipeline.execute("写一篇关于 AI 的文章")
print(result["result"])
```

## Streamlit 应用

```python
import streamlit as st
from fanlang_streamlit import render_symbol_bar

symbol = render_symbol_bar(["写", "改", "翻", "问"])
if symbol:
    st.write(f"选择了：{symbol}")
```
