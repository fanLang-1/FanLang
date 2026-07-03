# -*- coding: utf-8 -*-
"""
FanLang LangChain 检索引擎模块（retriever.py）的 pytest 测试。

测试范围：
  - FanLangRetriever 初始化（正常 / langchain 未安装 / fanlang[rag] 未安装）
  - from_documents() 类方法（正常 / 目录不存在 / 非目录路径 / 引擎构建失败）
  - _get_relevant_documents() 检索结果转换（Document / dict / str / other）
  - 异步 _aget_relevant_documents 桥接
  - 错误处理（引擎未初始化 / 检索失败 / 缺少依赖）
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

# ── 添加项目根目录到 sys.path ──
PROJECT_ROOT = Path("C:/Work/FanLang").resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════
# Fixture: mock 所有外部依赖
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _mock_dependencies():
    """mock langchain_core 和 fanlang 依赖，使一切可用。"""
    # Mock langchain_core
    mock_doc = MagicMock()
    mock_doc.page_content = ""
    mock_doc.metadata = {}

    mock_modules = {
        "langchain_core": MagicMock(),
        "langchain_core.callbacks": MagicMock(
            CallbackManagerForRetrieverRun=MagicMock(),
        ),
        "langchain_core.documents": MagicMock(Document=mock_doc.__class__),
        "langchain_core.retrievers": MagicMock(BaseRetriever=object),
    }

    for mod_name, mod_obj in mock_modules.items():
        sys.modules[mod_name] = mod_obj

    # Mock fanlang.rag
    mock_quick_rag = MagicMock()
    mock_quick_rag.query.return_value = [
        {"content": "文档1内容", "metadata": {"source": "doc1"}},
        {"content": "文档2内容", "metadata": {"source": "doc2"}},
    ]
    mock_fanlang_rag = MagicMock()
    mock_fanlang_rag.QuickRAG = MagicMock(return_value=mock_quick_rag)

    sys.modules["fanlang"] = MagicMock()
    sys.modules["fanlang.rag"] = mock_fanlang_rag

    for key in list(sys.modules.keys()):
        if "fanlang_langchain" in key:
            del sys.modules[key]

    # 验证 mock 生效
    from fanlang_langchain.retriever import _LANGCHAIN_AVAILABLE, _FANLANG_RAG_AVAILABLE
    assert _LANGCHAIN_AVAILABLE, "LangChain mock 应可用"
    assert _FANLANG_RAG_AVAILABLE, "fanlang[rag] mock 应可用"

    yield mock_quick_rag

    for key in list(sys.modules.keys()):
        if key in mock_modules or key.startswith("fanlang") or "fanlang_langchain" in key:
            sys.modules.pop(key, None)


# ═══════════════════════════════════════════════════════════════
# tests: 初始化
# ═══════════════════════════════════════════════════════════════

class TestFanLangRetrieverInit:
    """FanLangRetriever 初始化。"""

    def test_init_with_rag_engine(self, _mock_dependencies) -> None:
        from fanlang_langchain.retriever import FanLangRetriever

        rag_engine = MagicMock()
        retriever = FanLangRetriever(rag_engine=rag_engine, k=3)
        assert retriever.rag_engine is rag_engine
        assert retriever.k == 3

    def test_init_default_k(self, _mock_dependencies) -> None:
        from fanlang_langchain.retriever import FanLangRetriever

        retriever = FanLangRetriever(rag_engine=MagicMock())
        assert retriever.k == 4

    def test_init_without_rag_engine(self, _mock_dependencies) -> None:
        """不传 rag_engine 时初始化为 None。"""
        from fanlang_langchain.retriever import FanLangRetriever

        retriever = FanLangRetriever()
        assert retriever.rag_engine is None
        assert retriever.k == 4

    def test_class_vars(self, _mock_dependencies) -> None:
        from fanlang_langchain.retriever import FanLangRetriever

        assert FanLangRetriever._LANGCHAIN_LOADED is True
        assert FanLangRetriever._FANLANG_RAG_LOADED is True


# ═══════════════════════════════════════════════════════════════
# tests: from_documents()
# ═══════════════════════════════════════════════════════════════

class TestFromDocuments:
    """FanLangRetriever.from_documents 类方法。"""

    def test_from_documents_with_existing_dir(self, _mock_dependencies, tmp_path) -> None:
        """从存在的目录构建检索引擎。"""
        from fanlang_langchain.retriever import FanLangRetriever
        from fanlang.rag import QuickRAG

        # 创建临时目录
        doc_dir = tmp_path / "my_docs"
        doc_dir.mkdir()
        (doc_dir / "readme.md").write_text("test")

        retriever = FanLangRetriever.from_documents(str(doc_dir), k=5)
        assert retriever.k == 5
        assert retriever.rag_engine is not None
        # 验证 QuickRAG 被正确调用
        QuickRAG.assert_called_once()
        call_kwargs = QuickRAG.call_args[1]
        assert "source_dir" in call_kwargs

    def test_from_documents_with_embedding_model(self, _mock_dependencies, tmp_path) -> None:
        """传入 embedding_model 参数。"""
        from fanlang_langchain.retriever import FanLangRetriever
        from fanlang.rag import QuickRAG

        doc_dir = tmp_path / "docs2"
        doc_dir.mkdir()

        emb_model = "text-embedding-3-small"
        FanLangRetriever.from_documents(str(doc_dir), embedding_model=emb_model)
        call_kwargs = QuickRAG.call_args[1]
        assert call_kwargs["embedding_model"] == emb_model

    def test_from_documents_dir_not_exists(self, _mock_dependencies) -> None:
        """目录不存在时抛出 FileNotFoundError。"""
        from fanlang_langchain.retriever import FanLangRetriever

        with pytest.raises(FileNotFoundError, match="文档目录不存在"):
            FanLangRetriever.from_documents("/nonexistent/path")

    def test_from_documents_not_a_directory(self, _mock_dependencies, tmp_path) -> None:
        """路径是文件而非目录时抛出 NotADirectoryError。"""
        from fanlang_langchain.retriever import FanLangRetriever

        f = tmp_path / "file.txt"
        f.write_text("not a dir")

        with pytest.raises(NotADirectoryError):
            FanLangRetriever.from_documents(str(f))

    def test_from_documents_engine_build_fails(self, _mock_dependencies, tmp_path) -> None:
        """QuickRAG 构建失败时抛出 FanLangRetrieverError。"""
        from fanlang_langchain.retriever import FanLangRetriever, FanLangRetrieverError
        from fanlang.rag import QuickRAG

        doc_dir = tmp_path / "docs3"
        doc_dir.mkdir()

        QuickRAG.side_effect = RuntimeError("引擎初始化失败")

        with pytest.raises(FanLangRetrieverError, match="构建 QuickRAG 引擎失败"):
            FanLangRetriever.from_documents(str(doc_dir))


# ═══════════════════════════════════════════════════════════════
# tests: _get_relevant_documents
# ═══════════════════════════════════════════════════════════════

class TestGetRelevantDocuments:
    """_get_relevant_documents 检索与结果转换。"""

    def test_engine_not_initialized_raises_error(self, _mock_dependencies) -> None:
        """rag_engine 未初始化时抛出 FanLangRetrieverError。"""
        from fanlang_langchain.retriever import FanLangRetriever, FanLangRetrieverError

        retriever = FanLangRetriever()  # 不传 rag_engine
        with pytest.raises(FanLangRetrieverError, match="未初始化"):
            retriever._get_relevant_documents("query")

    def test_query_method_on_engine(self, _mock_dependencies) -> None:
        """引擎有 query 方法时调用 query。"""
        from fanlang_langchain.retriever import FanLangRetriever

        engine = MagicMock()
        engine.query.return_value = [
            {"content": "结果1", "metadata": {"source": "a"}},
        ]
        retriever = FanLangRetriever(rag_engine=engine)

        docs = retriever._get_relevant_documents("测试查询")
        assert len(docs) == 1
        engine.query.assert_called_once_with("测试查询", top_k=4)

    def test_search_method_on_engine(self, _mock_dependencies) -> None:
        """引擎只有 search 方法时调用 search。"""
        from fanlang_langchain.retriever import FanLangRetriever

        engine = MagicMock()
        # 没有 query，只有 search
        del engine.query
        engine.search.return_value = [
            {"content": "搜索1"},
        ]
        retriever = FanLangRetriever(rag_engine=engine)

        docs = retriever._get_relevant_documents("查询")
        assert len(docs) == 1
        engine.search.assert_called_once()

    def test_retrieve_method_on_engine(self, _mock_dependencies) -> None:
        """引擎只有 retrieve 方法时调用 retrieve。"""
        from fanlang_langchain.retriever import FanLangRetriever

        engine = MagicMock()
        del engine.query
        del engine.search
        engine.retrieve.return_value = [
            {"content": "检索结果"},
        ]
        retriever = FanLangRetriever(rag_engine=engine)

        docs = retriever._get_relevant_documents("查询")
        assert len(docs) == 1
        engine.retrieve.assert_called_once()

    def test_direct_call_fallback(self, _mock_dependencies) -> None:
        """引擎没有 query / search / retrieve 时直接调用。"""
        from fanlang_langchain.retriever import FanLangRetriever

        engine = MagicMock()
        del engine.query
        del engine.search
        del engine.retrieve
        engine.return_value = [{"content": "直接调用结果"}]
        retriever = FanLangRetriever(rag_engine=engine)

        docs = retriever._get_relevant_documents("查询")
        assert len(docs) == 1

    def test_custom_k_parameter(self, _mock_dependencies) -> None:
        """传递自定义 k 参数。"""
        from fanlang_langchain.retriever import FanLangRetriever

        engine = MagicMock()
        retriever = FanLangRetriever(rag_engine=engine, k=4)

        retriever._get_relevant_documents("查询", k=10)
        engine.query.assert_called_once_with("查询", top_k=10)

    def test_result_conversion_from_document(self, _mock_dependencies) -> None:
        """结果已是 Document 对象时直接使用。"""
        from fanlang_langchain.retriever import FanLangRetriever
        from langchain_core.documents import Document

        engine = MagicMock()
        doc = Document(page_content="已有文档", metadata={"key": "val"})
        engine.query.return_value = [doc]
        retriever = FanLangRetriever(rag_engine=engine)

        docs = retriever._get_relevant_documents("查询")
        assert len(docs) == 1
        assert docs[0].page_content == "已有文档"
        assert docs[0].metadata["key"] == "val"

    def test_result_conversion_from_dict(self, _mock_dependencies) -> None:
        """结果从 dict 转换。"""
        from fanlang_langchain.retriever import FanLangRetriever

        engine = MagicMock()
        engine.query.return_value = [
            {"content": "内容", "metadata": {"src": "file1"}},
        ]
        retriever = FanLangRetriever(rag_engine=engine)

        docs = retriever._get_relevant_documents("查询")
        assert docs[0].page_content == "内容"
        assert docs[0].metadata["src"] == "file1"

    def test_result_conversion_from_dict_text_key(self, _mock_dependencies) -> None:
        """dict 使用 text/meta 键名兼容。"""
        from fanlang_langchain.retriever import FanLangRetriever

        engine = MagicMock()
        engine.query.return_value = [
            {"text": "文本内容", "meta": {"k": "v"}},
        ]
        retriever = FanLangRetriever(rag_engine=engine)

        docs = retriever._get_relevant_documents("查询")
        assert docs[0].page_content == "文本内容"
        assert docs[0].metadata["k"] == "v"

    def test_result_conversion_from_string(self, _mock_dependencies) -> None:
        """结果从字符串转换。"""
        from fanlang_langchain.retriever import FanLangRetriever

        engine = MagicMock()
        engine.query.return_value = ["纯字符串结果"]
        retriever = FanLangRetriever(rag_engine=engine)

        docs = retriever._get_relevant_documents("查询")
        assert docs[0].page_content == "纯字符串结果"

    def test_result_conversion_from_other(self, _mock_dependencies) -> None:
        """结果从其他类型（数字等）通过 str() 转换。"""
        from fanlang_langchain.retriever import FanLangRetriever

        engine = MagicMock()
        engine.query.return_value = [42, 3.14]
        retriever = FanLangRetriever(rag_engine=engine)

        docs = retriever._get_relevant_documents("查询")
        # 42 → str 是 "42"
        assert docs[0].page_content == "42"
        assert docs[1].page_content == "3.14"

    def test_retrieval_exception(self, _mock_dependencies) -> None:
        """检索异常时抛出 FanLangRetrieverError。"""
        from fanlang_langchain.retriever import FanLangRetriever, FanLangRetrieverError

        engine = MagicMock()
        engine.query.side_effect = RuntimeError("检索失败")
        retriever = FanLangRetriever(rag_engine=engine)

        with pytest.raises(FanLangRetrieverError, match="QuickRAG 检索失败"):
            retriever._get_relevant_documents("查询")


# ═══════════════════════════════════════════════════════════════
# tests: _aget_relevant_documents
# ═══════════════════════════════════════════════════════════════

class TestAGetRelevantDocuments:
    """异步检索桥接到同步方法。"""

    @pytest.mark.asyncio
    async def test_async_bridges_to_sync(self, _mock_dependencies) -> None:
        from fanlang_langchain.retriever import FanLangRetriever

        engine = MagicMock()
        engine.query.return_value = [{"content": "异步结果"}]
        retriever = FanLangRetriever(rag_engine=engine)

        docs = await retriever._aget_relevant_documents("查询")
        assert len(docs) == 1
        assert docs[0].page_content == "异步结果"


# ═══════════════════════════════════════════════════════════════
# tests: 错误处理 — 缺少依赖
# ═══════════════════════════════════════════════════════════════

class TestMissingDependencies:
    """缺少依赖时的错误处理。"""

    def test_langchain_not_available(self, _mock_dependencies) -> None:
        """langchain 不可用时抛出 LangChainNotInstalledError。"""
        # langchain_core 实际已安装（v1.4.8），所以直接 patch 模块级 _LANGCHAIN_AVAILABLE
        from fanlang_langchain.retriever import FanLangRetriever, LangChainNotInstalledError

        with patch("fanlang_langchain.retriever._LANGCHAIN_AVAILABLE", False):
            with pytest.raises(LangChainNotInstalledError, match="langchain 未安装"):
                FanLangRetriever(rag_engine=MagicMock())

    def test_fanlang_rag_not_available(self, _mock_dependencies) -> None:
        """fanlang[rag] 不可用时抛出 FanLangRAGNotInstalledError。"""
        from fanlang_langchain.retriever import FanLangRetriever, FanLangRAGNotInstalledError

        with patch("fanlang_langchain.retriever._FANLANG_RAG_AVAILABLE", False):
            with pytest.raises(FanLangRAGNotInstalledError, match="fanlang"):
                FanLangRetriever(rag_engine=MagicMock())

    def test_from_documents_fanlang_rag_not_available(self, _mock_dependencies) -> None:
        """from_documents 中 fanlang[rag] 不可用。"""
        from fanlang_langchain.retriever import FanLangRetriever, FanLangRAGNotInstalledError

        with patch("fanlang_langchain.retriever._FANLANG_RAG_AVAILABLE", False):
            with pytest.raises(FanLangRAGNotInstalledError, match="fanlang"):
                FanLangRetriever.from_documents("/some/path")
