# pyfanlang-langchain

<p align="center">
  <img src="../assets/banner.svg" alt="凡语 FanLang Banner" width="80%">
</p>

<p align="center">
  <a href="https://pypi.org/project/pyfanlang-langchain/"><img src="https://img.shields.io/pypi/v/pyfanlang-langchain?color=blue" alt="PyPI"></a>
  <a href="https://github.com/fanLang-1/FanLang"><img src="https://img.shields.io/badge/source-GitHub-blue" alt="GitHub"></a>
</p>

凡语 FanLang 的 LangChain 集成包。

## 安装

```bash
pip install pyfanlang-langchain
```

## 使用

```python
from fanlang_langchain import OODAAgent, FanLangRetriever

# OODA 循环智能代理
agent = OODAAgent(llm=your_llm)
result = agent.run("帮我写一篇科普文章")

# RAG 检索器
retriever = FanLangRetriever.from_documents(docs)
```

## License

MIT
