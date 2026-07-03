"""
FanLang-LangChain 集成包。

提供 OODA 智能代理（OODAAgent）和 FanLang 检索引擎（FanLangRetriever），
可直接嵌入 LangChain 工作流中使用。

导出:
    - OODAAgent: 基于 OODA (Observe-Orient-Decide-Act) 循环的智能代理
    - FanLangRetriever: 封装 fanlang.rag.QuickRAG 的 LangChain 检索器
"""

from fanlang_langchain.ooda_agent import OODAAgent
from fanlang_langchain.retriever import FanLangRetriever

__all__ = ["OODAAgent", "FanLangRetriever"]
__version__ = "0.1.0"
