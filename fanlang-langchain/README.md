# pyfanlang-langchain

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
