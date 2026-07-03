# -*- coding: utf-8 -*-
"""
凡语示例 5: QuickRAG 文档检索
===============================
使用 QuickRAG 进行本地文档的检索增强生成。
需要安装 chromadb + 可选依赖。

用法：
    python examples/05_rag_demo.py <目录路径>
    # 不传参时使用 examples/knowledge/ 作为默认目录
"""

import os
import sys

from fanlang import QuickRAG


def create_knowledge_base():
    """创建示例知识库。"""
    kb_dir = os.path.join(os.path.dirname(__file__), "knowledge")
    os.makedirs(kb_dir, exist_ok=True)

    # 创建示例文档
    sample_files = {
        "ai-intro.txt": """
人工智能（Artificial Intelligence，简称 AI）是计算机科学的一个分支，
致力于创建能够模拟人类智能的系统。主要包括机器学习、深度学习、自然语言处理等领域。

机器学习是 AI 的核心分支之一，它使计算机能够从数据中学习而不需要显式编程。
常见的机器学习方法包括监督学习、无监督学习和强化学习。

深度学习是机器学习的一个子集，使用多层神经网络来处理复杂模式。
它在图像识别、语音识别和自然语言处理等领域取得了突破性进展。
""",
        "python-basics.txt": """
Python 是一种高级、解释型编程语言，以其简洁的语法和强大的生态系统而闻名。
它广泛应用于数据分析、人工智能、Web 开发等领域。

Python 的特点包括：
1. 简洁易读的语法
2. 丰富的标准库
3. 强大的第三方包生态（NumPy、Pandas、Scikit-learn 等）
4. 跨平台支持
5. 动态类型系统

Python 3.10+ 引入了模式匹配等新特性，进一步增强了语言表达能力。
""",
        "rag-intro.txt": """
RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合检索和生成的 AI 技术。
它通过在生成回答之前先从知识库中检索相关信息，来提高回答的准确性和可靠性。

RAG 的工作流程：
1. 用户提出问题
2. 系统将问题转为向量，在知识库中检索最相关的文档片段
3. 将检索到的文档作为上下文，与问题一起发送给 LLM
4. LLM 基于上下文生成回答

RAG 的优势：
- 减少 AI 幻觉
- 基于事实和已有知识回答
- 可追溯信息来源
- 无需重新训练模型即可引入新知识
""",
    }

    for filename, content in sample_files.items():
        filepath = os.path.join(kb_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())

    print(f"  已创建示例知识库：{kb_dir}")
    return kb_dir


def demo_rag_search(rag: QuickRAG):
    """演示检索功能。"""
    print("\n--- 检索测试 ---")
    queries = [
        "什么是机器学习？",
        "Python 有哪些特点？",
        "RAG 是怎么工作的？",
        "深度学习有什么用？",
    ]

    for q in queries:
        print(f"\n  查询: {q}")
        try:
            chunks = rag.search(q, top_k=2)
            if chunks:
                print(f"  找到 {len(chunks)} 个相关片段：")
                for i, c in enumerate(chunks):
                    preview = c["text"][:80].replace("\n", " ")
                    score = c.get("score", 0)
                    print(f"    [{i+1}] (得分: {score:.4f}) {preview}...")
            else:
                print("  未找到相关结果")
        except Exception as e:
            print(f"  检索异常: {e}")


def demo_rag_query(rag: QuickRAG):
    """演示问答功能（需 LLM）。"""
    print("\n--- 问答测试（需 Ollama 运行）---")
    question = "Python 在 AI 领域有哪些应用？"

    try:
        print(f"\n  问题: {question}")
        answer, chunks = rag.query(question, top_k=2)
        print(f"  回答: {answer[:200]}...")
        print(f"  参考来源: {[c['source'] for c in chunks]}")
    except Exception as e:
        print(f"  问答异常: {e}（可能需要安装依赖或启动 Ollama）")


def main():
    print("=" * 60)
    print("【查】凡语 QuickRAG 文档检索演示")
    print("=" * 60)

    # 确定文档目录
    if len(sys.argv) > 1:
        doc_dir = sys.argv[1]
        if not os.path.isdir(doc_dir):
            print(f"错误：目录不存在 {doc_dir}")
            sys.exit(1)
    else:
        # 创建示例知识库
        doc_dir = create_knowledge_base()

    print(f"\n知识库目录: {doc_dir}")

    # 初始化 QuickRAG
    try:
        rag = QuickRAG(persist_dir="./chroma_demo_db")
    except ImportError as e:
        print(f"\n缺少依赖: {e}")
        print("请安装: pip install fanlang[rag]")
        sys.exit(1)

    # 索引文档
    def on_progress(current, total, filename):
        print(f"  索引: [{current}/{total}] {filename}")

    print("\n--- 索引文档 ---")
    try:
        new_count, total = rag.add_documents(doc_dir, on_progress=on_progress)
        print(f"\n  索引完成: 新增 {new_count}/{total} 个文件")
    except Exception as e:
        print(f"  索引异常: {e}")
        sys.exit(1)

    # 查看统计
    stats = rag.get_stats()
    print(f"  向量库: {stats['doc_chunks']} 个片段, {stats['indexed_files']} 个文件")

    # 演示检索
    demo_rag_search(rag)

    # 演示问答
    # demo_rag_query(rag)  # 需要 LLM，默认注释

    print("\n" + "=" * 60)
    print("演示完成。清理临时数据...")
    print("=" * 60)

    # 清理
    import shutil
    if os.path.exists("./chroma_demo_db"):
        shutil.rmtree("./chroma_demo_db")
    print("  已清理 chroma_demo_db/")

    # 如果创建了示例知识库，清理
    kb_dir = os.path.join(os.path.dirname(__file__), "knowledge")
    if os.path.exists(kb_dir):
        shutil.rmtree(kb_dir)
        print(f"  已清理 {kb_dir}")


if __name__ == "__main__":
    main()
