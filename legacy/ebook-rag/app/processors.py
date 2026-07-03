"""
📄 文件处理器 - 从各种格式提取文本
"""

import os
import re
import zipfile
import tempfile
from bs4 import BeautifulSoup
import pypdf

def extract_text_from_txt(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def extract_text_from_md(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def extract_text_from_html(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f.read(), "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n")

def extract_text_from_pdf(filepath):
    """从 PDF 提取文本"""
    text = ""
    try:
        reader = pypdf.PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"  ⚠️ PDF读取失败: {e}")
    return text

def extract_text_from_epub(filepath):
    """从 EPUB 提取文本"""
    text = ""
    try:
        with zipfile.ZipFile(filepath, "r") as z:
            # 找到所有 html/xhtml 文件
            html_files = [f for f in z.namelist() if f.endswith((".html", ".xhtml", ".htm"))]
            html_files.sort()
            for fname in html_files:
                try:
                    content = z.read(fname)
                    soup = BeautifulSoup(content, "lxml")
                    for tag in soup(["script", "style", "nav"]):
                        tag.decompose()
                    text += soup.get_text(separator="\n") + "\n"
                except:
                    pass
    except Exception as e:
        print(f"  ⚠️ EPUB读取失败: {e}")
    return text

def extract_text_from_docx(filepath):
    """从 DOCX 提取文本"""
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:
        return "⚠️ python-docx 未安装，请执行: pip install python-docx"
    except Exception as e:
        return f"⚠️ DOCX读取失败: {e}"

def extract_text(filepath):
    """自动识别格式并提取文本"""
    ext = os.path.splitext(filepath)[1].lower()
    handlers = {
        ".txt": extract_text_from_txt,
        ".md": extract_text_from_md,
        ".html": extract_text_from_html,
        ".htm": extract_text_from_html,
        ".pdf": extract_text_from_pdf,
        ".epub": extract_text_from_epub,
        ".docx": extract_text_from_docx,
    }
    handler = handlers.get(ext)
    if not handler:
        return None
    print(f"  📖 正在提取: {os.path.basename(filepath)}")
    text = handler(filepath)
    # 清理
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {3,}', '  ', text)
    text = text.strip()
    return text if len(text) > 50 else None  # 过滤太短的内容
