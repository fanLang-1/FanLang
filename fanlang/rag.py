# -*- coding: utf-8 -*-
"""
FanLang QuickRAG — 检索增强生成
================================
一行代码启动本地 RAG。自动扫描、索引、检索、回答。
"""

import hashlib
import os
import re
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple


# ============================================================
# 文件解析器（内置，不依赖外部库时自动降级）
# ============================================================
def _extract_text_from_txt(filepath: str) -> str:
    """从 TXT 文件提取文本。"""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _extract_text_from_md(filepath: str) -> str:
    """从 Markdown 文件提取文本。"""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _extract_text_from_html(filepath: str) -> str:
    """从 HTML 文件提取文本。"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("需要 beautifulsoup4 来解析 HTML 文件。请执行: pip install beautifulsoup4")

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f.read(), "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n")


def _extract_text_from_pdf(filepath: str) -> str:
    """从 PDF 文件提取文本。"""
    try:
        import pypdf
    except ImportError:
        raise ImportError("需要 pypdf 来解析 PDF 文件。请执行: pip install pypdf")

    text_parts: List[str] = []
    try:
        reader = pypdf.PdfReader(filepath)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    except Exception as e:
        raise RuntimeError(f"PDF 读取失败: {e}")
    return "\n".join(text_parts)


def _extract_text_from_epub(filepath: str) -> str:
    """从 EPUB 文件提取文本。"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("需要 beautifulsoup4 来解析 EPUB 文件。请执行: pip install beautifulsoup4")

    import zipfile

    text_parts: List[str] = []
    try:
        with zipfile.ZipFile(filepath, "r") as z:
            html_files = [
                f for f in z.namelist()
                if f.endswith((".html", ".xhtml", ".htm"))
            ]
            html_files.sort()
            for fname in html_files:
                try:
                    content = z.read(fname)
                    soup = BeautifulSoup(content, "lxml")
                    for tag in soup(["script", "style", "nav"]):
                        tag.decompose()
                    text_parts.append(soup.get_text(separator="\n"))
                except Exception:
                    pass
    except Exception as e:
        raise RuntimeError(f"EPUB 读取失败: {e}")
    return "\n".join(text_parts)


def _extract_text_from_docx(filepath: str) -> str:
    """从 DOCX 文件提取文本。"""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("需要 python-docx 来解析 DOCX 文件。请执行: pip install python-docx")

    try:
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        raise RuntimeError(f"DOCX 读取失败: {e}")


# 格式 → 解析器映射
_PARSER_MAP: Dict[str, Callable[[str], str]] = {
    ".txt": _extract_text_from_txt,
    ".md": _extract_text_from_md,
    ".html": _extract_text_from_html,
    ".htm": _extract_text_from_html,
    ".pdf": _extract_text_from_pdf,
    ".epub": _extract_text_from_epub,
    ".docx": _extract_text_from_docx,
}

# 支持的扩展名
SUPPORTED_EXTS: set = {".txt", ".md", ".html", ".htm", ".pdf", ".epub", ".docx"}


def extract_text(filepath: str) -> Optional[str]:
    """自动识别格式并提取文本。

    Args:
        filepath: 文件路径

    Returns:
        提取的文本，如果格式不支持或内容太短返回 None
    """
    ext = os.path.splitext(filepath)[1].lower()
    handler = _PARSER_MAP.get(ext)
    if not handler:
        return None

    try:
        text = handler(filepath)
    except (ImportError, RuntimeError):
        raise
    except Exception:
        return None

    # 清理
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {3,}", "  ", text)
    text = text.strip()

    return text if len(text) > 50 else None


# ============================================================
# QuickRAG 类
# ============================================================
class QuickRAG:
    """一行代码启动本地 RAG。

    用法::

        from fanlang import QuickRAG

        rag = QuickRAG()
        rag.add_documents("./my_books/")
        answer = rag.query("这本书讲了什么？")
    """

    # 默认配置
    DEFAULT_EMBED_MODEL: str = "shaw/dmeta-embedding-zh"
    DEFAULT_CHAT_MODEL: str = "qwen2.5:1.5b"
    DEFAULT_OLLAMA_HOST: str = "http://localhost:11434"
    DEFAULT_CHUNK_SIZE: int = 512
    DEFAULT_CHUNK_OVERLAP: int = 64
    DEFAULT_TOP_K: int = 3

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = "fanlang_rag",
        embed_model: Optional[str] = None,
        chat_model: Optional[str] = None,
        ollama_host: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        top_k: int = DEFAULT_TOP_K,
        chat_func: Optional[Callable] = None,
    ):
        """
        Args:
            persist_dir: ChromaDB 持久化目录。默认为当前目录下的 chroma_db/
            collection_name: 集合名称
            embed_model: Embedding 模型名
            chat_model: 对话模型名
            ollama_host: Ollama 服务地址
            chunk_size: 分块大小
            chunk_overlap: 分块重叠
            top_k: 检索数量
            chat_func: 自定义聊天函数。签名: chat_func(messages, model) -> str
        """
        self.persist_dir = persist_dir or os.path.join(os.getcwd(), "chroma_db")
        self.collection_name = collection_name
        self.embed_model = embed_model or self.DEFAULT_EMBED_MODEL
        self.chat_model = chat_model or self.DEFAULT_CHAT_MODEL
        self.ollama_host = ollama_host or self.DEFAULT_OLLAMA_HOST
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self._chat_func = chat_func

        # 索引记录（文件路径 → 文件 hash）
        self._index_record: Dict[str, str] = {}

        # 延迟初始化
        self._client: Any = None
        self._collection: Any = None
        self._initialized: bool = False

    def _ensure_init(self):
        """确保 ChromaDB 已初始化。"""
        if self._initialized:
            return

        try:
            import chromadb
        except ImportError:
            raise ImportError(
                "QuickRAG 需要 chromadb。请执行: pip install fanlang[rag]"
            )

        os.makedirs(self.persist_dir, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=chromadb.config.Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # 加载索引记录
        self._load_index_record()

        self._initialized = True

    def _load_index_record(self):
        """加载索引记录。"""
        record_path = os.path.join(self.persist_dir, "indexed_files.json")
        if os.path.exists(record_path):
            import json
            with open(record_path, "r", encoding="utf-8") as f:
                self._index_record = json.load(f)

    def _save_index_record(self):
        """保存索引记录。"""
        import json
        record_path = os.path.join(self.persist_dir, "indexed_files.json")
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump(self._index_record, f, ensure_ascii=False, indent=2)

    def _get_file_hash(self, filepath: str) -> str:
        """快速计算文件 hash（只读前 1MB）。"""
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            h.update(f.read(1024 * 1024))
        return h.hexdigest()

    def _scan_directory(self, dir_path: str) -> List[str]:
        """扫描目录下所有支持的文件。

        Args:
            dir_path: 目录路径

        Returns:
            文件路径列表
        """
        all_files: List[str] = []
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in SUPPORTED_EXTS:
                    all_files.append(os.path.join(root, f))
        return all_files

    def _embed(self, texts: List[str]) -> List[Any]:
        """调用 Ollama embedding API。

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        import requests

        resp = requests.post(
            f"{self.ollama_host}/api/embed",
            json={"model": self.embed_model, "input": texts},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["embeddings"]

    def _split_text(self, text: str) -> List[str]:
        """将文本切分成块。

        Args:
            text: 原始文本

        Returns:
            文本块列表
        """
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
        except ImportError:
            raise ImportError(
                "QuickRAG 需要 langchain-text-splitters。请执行: pip install fanlang[rag]"
            )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
        )
        return splitter.split_text(text)

    def _chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """内部 LLM 调用。

        Args:
            messages: 消息列表
            model: 模型名

        Returns:
            模型回复文本
        """
        if self._chat_func:
            return self._chat_func(messages, model or self.chat_model)

        import requests

        payload = {
            "model": model or self.chat_model,
            "messages": messages,
            "stream": False,
        }
        resp = requests.post(
            f"{self.ollama_host}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    # ============================================================
    # 公共 API
    # ============================================================
    def add_documents(
        self,
        dir_path: str,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
    ) -> Tuple[int, int]:
        """自动扫描目录并索引所有文档。

        Args:
            dir_path: 文档目录路径
            on_progress: 进度回调 (current, total, filename)

        Returns:
            (新索引数量, 总文件数量)
        """
        self._ensure_init()

        files = self._scan_directory(dir_path)
        total = len(files)
        new_count = 0

        for i, fp in enumerate(files):
            rel_path = os.path.basename(fp)

            if on_progress:
                on_progress(i + 1, total, rel_path)

            # 检查是否已索引
            file_hash = self._get_file_hash(fp)
            if rel_path in self._index_record and self._index_record[rel_path] == file_hash:
                continue

            # 提取文本
            text = extract_text(fp)
            if not text:
                continue

            # 分块
            chunks = self._split_text(text)

            # 生成唯一 ID
            doc_id_base = hashlib.md5(rel_path.encode()).hexdigest()[:12]
            ids = [f"{doc_id_base}_{j}" for j in range(len(chunks))]
            metadatas = [
                {"source": rel_path, "chunk": j, "file": os.path.basename(fp)}
                for j in range(len(chunks))
            ]

            # 批量入库（每次 100 条）
            batch_size = 100
            for start in range(0, len(chunks), batch_size):
                end = min(start + batch_size, len(chunks))
                self._collection.upsert(
                    ids=ids[start:end],
                    documents=chunks[start:end],
                    metadatas=metadatas[start:end],
                )

            # 记录已索引
            self._index_record[rel_path] = file_hash
            new_count += 1

        self._save_index_record()
        return new_count, total

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """向量检索。

        Args:
            query: 查询文本
            top_k: 返回数量，默认使用初始化时的 top_k

        Returns:
            [{"text": str, "source": str, "score": float}, ...]
        """
        self._ensure_init()

        k = top_k or self.top_k

        if self._collection.count() == 0:
            return []

        query_emb = self._embed([query])[0]
        results = self._collection.query(
            query_embeddings=[query_emb],
            n_results=min(k, self._collection.count()),
        )

        chunks: List[Dict[str, Any]] = []
        for i in range(len(results["documents"][0])):
            chunks.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source", ""),
                "score": results["distances"][0][i] if results["distances"] else 0.0,
            })
        return chunks

    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """检索 + 回答。

        Args:
            question: 问题
            top_k: 检索数量
            system_prompt: 自定义系统提示词

        Returns:
            (回答文本, 检索到的文本块列表)
        """
        self._ensure_init()

        # 1. 检索
        chunks = self.search(question, top_k)
        if not chunks:
            return (
                "\u4f60\u7684\u77e5\u8bc6\u5e93\u4e2d\u6ca1\u6709\u627e\u5230\u76f8\u5173\u8d44\u6599\uff0c\u8bf7\u5148\u6dfb\u52a0\u6587\u6863\u3002",
                [],
            )

        # 2. 构建上下文
        context = ""
        for i, c in enumerate(chunks):
            context += f"[\u6765\u6e90{i+1}: {c['source']}]\n{c['text']}\n\n"

        sp = system_prompt or (
            "\u4f60\u662f\u4e13\u4e1a\u7684\u5b66\u4e60\u52a9\u624b\u3002\u7528\u4e2d\u6587\u56de\u7b54\uff0c\u57fa\u4e8e\u63d0\u4f9b\u7684\u8d44\u6599\uff0c\u7b80\u660e\u627c\u8981\u3002"
            "\u5982\u679c\u8d44\u6599\u4e0d\u8db3\u4ee5\u56de\u7b54\uff0c\u8bf7\u5982\u5b9e\u8bf4\u3002\u5f15\u7528\u8d44\u6599\u4e2d\u7684\u5185\u5bb9\u3002"
        )

        messages = [
            {"role": "system", "content": sp},
            {"role": "user", "content": f"\u4ee5\u4e0b\u662f\u53c2\u8003\u8d44\u6599\uff1a\n{context}\n\n\u8bf7\u56de\u7b54\uff1a{question}"},
        ]

        # 3. 生成回答
        answer = self._chat(messages)
        return answer, chunks

    def query_stream(
        self,
        question: str,
        top_k: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> Generator[Any, None, None]:
        """流式检索 + 回答。

        Yields:
            逐步输出答案片段，最后一个 yield 包含完整答案和检索结果
        """
        try:
            import requests
        except ImportError:
            raise ImportError("流式查询需要 requests 库。请执行: pip install requests")

        self._ensure_init()

        # 检索
        chunks = self.search(question, top_k)
        if not chunks:
            yield {
                "type": "error",
                "content": (
                    "\u4f60\u7684\u77e5\u8bc6\u5e93\u4e2d\u6ca1\u6709\u627e\u5230\u76f8\u5173\u8d44\u6599\uff0c"
                    "\u8bf7\u5148\u6dfb\u52a0\u6587\u6863\u3002"
                ),
                "chunks": [],
            }
            return

        # 构建上下文
        context = ""
        for i, c in enumerate(chunks):
            context += f"[\u6765\u6e90{i+1}: {c['source']}]\n{c['text']}\n\n"

        sp = system_prompt or (
            "\u4f60\u662f\u4e13\u4e1a\u7684\u5b66\u4e60\u52a9\u624b\u3002\u7528\u4e2d\u6587\u56de\u7b54\uff0c\u57fa\u4e8e\u63d0\u4f9b\u7684\u8d44\u6599\uff0c\u7b80\u660e\u627c\u8981\u3002"
            "\u5982\u679c\u8d44\u6599\u4e0d\u8db3\u4ee5\u56de\u7b54\uff0c\u8bf7\u5982\u5b9e\u8bf4\u3002\u5f15\u7528\u8d44\u6599\u4e2d\u7684\u5185\u5bb9\u3002"
        )

        payload = {
            "model": self.chat_model,
            "messages": [
                {"role": "system", "content": sp},
                {"role": "user", "content": f"\u4ee5\u4e0b\u662f\u53c2\u8003\u8d44\u6599\uff1a\n{context}\n\n\u8bf7\u56de\u7b54\uff1a{question}"},
            ],
            "stream": True,
        }

        resp = requests.post(
            f"{self.ollama_host}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        )
        resp.raise_for_status()

        full_answer = ""
        for line in resp.iter_lines(decode_unicode=True):
            if line:
                import json
                data = json.loads(line)
                if "message" in data and "content" in data["message"]:
                    content = data["message"]["content"]
                    full_answer += content
                    yield {"type": "chunk", "content": content, "chunks": None}
                if data.get("done"):
                    break

        yield {"type": "done", "content": full_answer, "chunks": chunks}

    def get_stats(self) -> Dict[str, Any]:
        """获取向量库统计信息。

        Returns:
            {"doc_chunks": int, "indexed_files": int}
        """
        self._ensure_init()
        return {
            "doc_chunks": self._collection.count(),
            "indexed_files": len(self._index_record),
        }

    def clear(self):
        """清空向量库和索引记录。"""
        self._ensure_init()
        self._collection.delete(ids=self._collection.get()["ids"])
        self._index_record.clear()
        self._save_index_record()
