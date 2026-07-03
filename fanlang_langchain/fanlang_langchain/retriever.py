"""
FanLang 检索引擎（FanLangRetriever）。

封装 fanlang.rag.QuickRAG 为 LangChain BaseRetriever，支持自定义 Embedding 模型，
可直接用于 LangChain 的 RetrievalQA、ConversationalRetrievalChain 等检索增强流程。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)

# --- LangChain 优雅降级 ---
try:
    from langchain_core.callbacks import CallbackManagerForRetrieverRun
    from langchain_core.documents import Document
    from langchain_core.retrievers import BaseRetriever

    _LANGCHAIN_AVAILABLE = True
except ImportError:  # pragma: no cover
    _LANGCHAIN_AVAILABLE = False

    BaseRetriever = object  # type: ignore[misc,assignment]
    Document = Any  # type: ignore[misc,assignment]
    CallbackManagerForRetrieverRun = Any  # type: ignore[misc,assignment]

# --- fanlang 优雅降级 ---
try:
    from fanlang.rag import QuickRAG  # type: ignore[import-untyped]

    _FANLANG_RAG_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FANLANG_RAG_AVAILABLE = False
    QuickRAG = None  # type: ignore[misc,assignment]


# ---------------------------------------------------------------------------
# 异常定义
# ---------------------------------------------------------------------------

class FanLangRetrieverError(Exception):
    """FanLangRetriever 运行时异常。"""


class LangChainNotInstalledError(ImportError):
    """LangChain 未安装时抛出的异常。

    请执行: pip install langchain
    """


class FanLangRAGNotInstalledError(ImportError):
    """fanlang[rag] 未安装时抛出的异常。

    请执行: pip install fanlang[rag]
    """


# ---------------------------------------------------------------------------
# FanLangRetriever
# ---------------------------------------------------------------------------

class FanLangRetriever(BaseRetriever):
    """封装 fanlang.rag.QuickRAG 的 LangChain 检索器。

    该类桥接 fanlang 的 RAG 引擎与 LangChain 的检索器接口，
    可无缝嵌入 RetrievalQA、ConversationalRetrievalChain 等流程。

    Usage::

        # 从文档目录构建
        retriever = FanLangRetriever.from_documents("./my_docs/")

        # 直接构造
        rag_engine = QuickRAG(source_dir="./my_docs/")
        retriever = FanLangRetriever(rag_engine=rag_engine)

        # 在 LangChain 中使用
        from langchain.chains import RetrievalQA
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        qa.run("这个项目的主要功能是什么？")
    """

    # LangChain BaseRetriever 要求定义的字段
    rag_engine: Any = None
    """fanlang QuickRAG 实例。"""

    k: int = 4
    """默认返回的文档数量。"""

    _LANGCHAIN_LOADED: ClassVar[bool] = _LANGCHAIN_AVAILABLE
    _FANLANG_RAG_LOADED: ClassVar[bool] = _FANLANG_RAG_AVAILABLE

    # ------------------------------------------------------------------
    # 构造
    # ------------------------------------------------------------------

    def __init__(
        self,
        rag_engine: Optional[Any] = None,
        k: int = 4,
        **kwargs: Any,
    ) -> None:
        """初始化 FanLangRetriever。

        Args:
            rag_engine: fanlang.rag.QuickRAG 实例。如未提供，
                需在子类或构造后通过 from_documents 设置。
            k: 默认返回的文档数量，默认 4。
            **kwargs: 传递给 BaseRetriever 的额外参数。

        Raises:
            LangChainNotInstalledError: langchain 未安装。
            FanLangRAGNotInstalledError: fanlang[rag] 未安装。
        """
        if not _LANGCHAIN_AVAILABLE:
            raise LangChainNotInstalledError(
                "langchain 未安装。请执行: pip install langchain"
            )
        if not _FANLANG_RAG_AVAILABLE:
            raise FanLangRAGNotInstalledError(
                "fanlang[rag] 未安装。请执行: pip install fanlang[rag]"
            )

        super().__init__(**kwargs)
        self.rag_engine = rag_engine
        self.k = k

    # ------------------------------------------------------------------
    # 类方法: 从文档构建
    # ------------------------------------------------------------------

    @classmethod
    def from_documents(
        cls: Type["FanLangRetriever"],
        dir_path: Union[str, Path],
        embedding_model: Optional[Any] = None,
        **kwargs: Any,
    ) -> "FanLangRetriever":
        """从文档目录构建 FanLangRetriever。

        Args:
            dir_path: 包含文档的目录路径（支持 .txt、.md、.pdf 等）。
            embedding_model: 可选的自定义 Embedding 模型。
                如未提供，使用 fanlang 默认嵌入。
            **kwargs: 传递给构造函数的额外参数（如 k）。

        Returns:
            FanLangRetriever 实例。

        Raises:
            FanLangRAGNotInstalledError: fanlang[rag] 未安装。
            FileNotFoundError: 目录不存在。
            FanLangRetrieverError: 引擎构建失败。
        """
        if not _FANLANG_RAG_AVAILABLE:
            raise FanLangRAGNotInstalledError(
                "fanlang[rag] 未安装。请执行: pip install fanlang[rag]"
            )

        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"文档目录不存在: {dir_path}")
        if not dir_path.is_dir():
            raise NotADirectoryError(f"路径不是目录: {dir_path}")

        try:
            engine = QuickRAG(  # type: ignore[misc]
                source_dir=str(dir_path),
                embedding_model=embedding_model,
            )
        except Exception as exc:
            raise FanLangRetrieverError(
                f"构建 QuickRAG 引擎失败: {exc}"
            ) from exc

        instance = cls(rag_engine=engine, **kwargs)
        return instance

    # ------------------------------------------------------------------
    # 核心检索
    # ------------------------------------------------------------------

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """检索与查询相关的文档（LangChain 检索器核心方法）。

        Args:
            query: 查询文本。
            run_manager: LangChain 回调管理器（可选）。
            **kwargs: 额外参数，可包含:
                - k (int): 覆盖实例默认的返回数量。

        Returns:
            List[Document]: 相关文档列表，按相关性降序排列。

        Raises:
            FanLangRetrieverError: 引擎未初始化或检索失败。
        """
        if self.rag_engine is None:
            raise FanLangRetrieverError(
                "rag_engine 未初始化。请先调用 from_documents() 或传入 QuickRAG 实例。"
            )

        k = kwargs.get("k", self.k)

        try:
            # 尝试 fanlang QuickRAG 的 query / search 接口
            if hasattr(self.rag_engine, "query"):
                raw_results = self.rag_engine.query(query, top_k=k)
            elif hasattr(self.rag_engine, "search"):
                raw_results = self.rag_engine.search(query, top_k=k)
            elif hasattr(self.rag_engine, "retrieve"):
                raw_results = self.rag_engine.retrieve(query, top_k=k)
            else:
                # 回退: 尝试直接调用
                raw_results = self.rag_engine(query)  # type: ignore[operator]
        except Exception as exc:
            raise FanLangRetrieverError(
                f"QuickRAG 检索失败: {exc}"
            ) from exc

        # 统一转换为 LangChain Document 列表
        documents: List[Document] = []
        for item in raw_results:
            if isinstance(item, Document):
                documents.append(item)
            elif isinstance(item, dict):
                documents.append(Document(
                    page_content=item.get("content", item.get("text", "")),
                    metadata=item.get("metadata", item.get("meta", {})),
                ))
            elif isinstance(item, str):
                documents.append(Document(page_content=item))
            else:
                # 尝试转换为字符串
                documents.append(Document(page_content=str(item)))

        return documents

    # ------------------------------------------------------------------
    # 异步检索（同步桥接）
    # ------------------------------------------------------------------

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """异步检索文档。

        当前通过同步方法桥接实现。子类可覆盖以实现真正的异步检索。

        Args:
            query: 查询文本。
            run_manager: LangChain 回调管理器（可选）。
            **kwargs: 额外参数。

        Returns:
            List[Document]: 相关文档列表。
        """
        return self._get_relevant_documents(
            query, run_manager=run_manager, **kwargs
        )
