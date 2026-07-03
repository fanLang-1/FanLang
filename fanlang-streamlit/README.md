# FanLang Streamlit

FanLang 符号系统的 Streamlit 集成插件，提供符号按钮栏、符号选择器和术语提示卡片等预构建组件。

## 安装

```bash
pip install fanlang-streamlit
```

## 快速开始

```python
import streamlit as st
from fanlang_streamlit import render_symbol_bar, render_symbol_picker

# 渲染核心符号按钮栏（8 个核心符号）
selected = render_symbol_bar()
if selected:
    st.write(f"你选择了符号：{selected}")

# 渲染展开式符号选择器（按梯队分组）
picked = render_symbol_picker()
if picked:
    st.write(f"选中的符号：{picked}")
```

## 组件说明

### render_symbol_bar(symbols=None, max_cols=8)

渲染一行符号按钮。

- 默认展示 8 个核心符号：写、改、翻、总、问、查、比、理
- 每个按钮包含 emoji + 中文字符
- 支持自定义符号列表和最大列数
- 选中状态通过 session_state 管理并高亮显示
- 返回被点击的符号字符（str）或 None

```python
# 自定义符号列表
custom = [
    {"character": "写", "emoji": "✍️"},
    {"character": "改", "emoji": "✏️"},
]
selected = render_symbol_bar(symbols=custom, max_cols=4)
```

### render_symbol_picker(symbols=None)

展开式符号选择器，按梯队分组展示。

- 一梯队（7 个）：核心高频符号
- 二梯队（5 个）：扩展符号
- 三梯队（8 个）：领域符号
- 四梯队（5 个）：辅助符号
- 使用 st.expander 折叠，节省页面空间
- 返回选中的符号字符（str）或 None

### render_terminology_tooltip(term)

渲染术语提示卡片。

```python
render_terminology_tooltip({
    "term_en": "Translate",
    "term_zh": "翻 - 翻译",
})
```

## 回调函数

```python
from fanlang_streamlit import on_symbol_click, get_selected_symbol, clear_selected_symbol

# 手动写入选中状态
on_symbol_click("写")

# 读取当前选中符号
sym = get_selected_symbol()  # "写"

# 清除选中状态
clear_selected_symbol()
```

## 依赖

- Python >= 3.10
- streamlit >= 1.28
- fanlang >= 0.1.0

## 许可

MIT
