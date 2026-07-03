# Streamlit 插件

`pyfanlang-streamlit` 提供一行代码渲染的 UI 组件。

## 安装

```bash
pip install pyfanlang-streamlit
```

## render_symbol_bar()

渲染一行符号按钮栏。

```python
import streamlit as st
from fanlang_streamlit import render_symbol_bar

# 默认 8 个核心符号
selected = render_symbol_bar()

# 自定义符号
selected = render_symbol_bar(
    symbols=["写", "改", "翻", "总", "问", "查", "比", "理"],
    max_cols=8
)

if selected:
    st.write(f"选择了：{selected}")
```

## render_symbol_picker()

展开式符号选择器（按梯队分组）。

```python
from fanlang_streamlit import render_symbol_picker

picked = render_symbol_picker()
if picked:
    st.write(f"选中的符号：{picked}")
```

## render_terminology_tooltip()

术语提示卡片。

```python
from fanlang_streamlit import render_terminology_tooltip

render_terminology_tooltip({
    "term_en": "Translate",
    "term_zh": "翻 - 翻译",
})
```

## 回调 API

```python
from fanlang_streamlit import on_symbol_click, get_selected_symbol, clear_selected_symbol

on_symbol_click("写")       # 选中
sym = get_selected_symbol() # 读取
clear_selected_symbol()     # 清除
```
