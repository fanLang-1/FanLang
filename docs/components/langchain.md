# LangChain 集成

`pyfanlang-langchain` 提供 OODA 循环智能代理和 RAG 检索器。

## 安装

```bash
pip install pyfanlang-langchain
```

## OODAAgent

基于 OODA 循环的智能代理。

```python
from langchain.chat_models import ChatOllama
from fanlang_langchain import OODAAgent

llm = ChatOllama(model="qwen2.5:1.5b")

agent = OODAAgent(
    llm=llm,
    tools=[...],       # 可选工具列表
    max_iterations=3   # 最大迭代轮数
)

result = agent.run("帮我写一篇科普文章")
```

### 内部流程

```
Orient:  分析用户输入 → 生成计划
Decide:  选择工具或直接生成
Act:     执行操作
Observe: 评估结果 → 循环或结束
```

## FanLangRetriever

LangChain 兼容的检索器。

```python
from fanlang_langchain import FanLangRetriever

retriever = FanLangRetriever(
    persist_dir="./chroma_db",
    top_k=4
)

# 从文档创建
docs = ["文档内容1", "文档内容2"]
retriever = FanLangRetriever.from_documents(docs)

# 检索
results = retriever.invoke("什么是机器学习？")
```
