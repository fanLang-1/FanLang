# QuickRAG

一行代码启动本地文档检索。

## 安装

```bash
pip install pyfanlang[rag]
```

## 快速使用

```python
from fanlang import QuickRAG

rag = QuickRAG(persist_dir="./chroma_db")

# 索引文档
rag.add_documents("./my_docs")

# 检索
results = rag.search("什么是机器学习？", top_k=3)
for r in results:
    print(f"[{r['score']:.4f}] {r['text'][:100]}")

# 问答（需 LLM）
answer, chunks = rag.query("什么是机器学习？", top_k=2)
print(f"回答：{answer}")
```

## 支持的文档格式

| 格式 | 支持 | 
|:--|:--|
| `.txt` | ✅ |
| `.md` | ✅ |
| `.html` | ✅ |
| `.pdf` | ✅ |
| `.docx` | ✅ |
| `.epub` | ✅ |

## 索引回调

```python
def on_progress(current, total, filename):
    print(f"[{current}/{total}] {filename}")

new, total = rag.add_documents("./docs", on_progress=on_progress)
print(f"新增 {new}/{total} 个文件")
```

## 统计

```python
stats = rag.get_stats()
# {"doc_chunks": 128, "indexed_files": 15}
```
