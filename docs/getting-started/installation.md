# 安装

凡语分为三个独立的 pip 包，按需安装。

## 核心包

```bash
pip install pyfanlang
```

包含：符号体系、OODA 循环引擎、QuickRAG、术语映射、盗火者研讨厅、狼群模型路由器。

## Streamlit 插件

```bash
pip install pyfanlang-streamlit
```

包含：`render_symbol_bar()`、`render_symbol_picker()`、`render_terminology_tooltip()`。

## LangChain 集成

```bash
pip install pyfanlang-langchain
```

包含：`OODAAgent`、`FanLangRetriever`。

## RAG 支持（可选）

```bash
pip install pyfanlang[rag]
```

安装 QuickRAG 所需的向量数据库和文档解析依赖。

## 全部安装

```bash
pip install pyfanlang[full]
```

## 环境要求

- Python >= 3.10
- 建议：Ollama 或兼容的 LLM API 用于 OODA 循环和研讨厅

## 验证安装

```python
from fanlang import get_symbol, get_all_symbols
print(f"凡语 v{get_symbol.__module__} 安装成功")
print(f"共 {len(get_all_symbols())} 个符号")
```
