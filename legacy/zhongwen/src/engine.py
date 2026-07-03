"""
🔌 推理引擎 — 连接 Ollama 本地模型
只需一行命令安装 Ollama，其他自动。
"""

import json
import subprocess
import urllib.request
import urllib.error

OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:1.5b"

def _post(path, data):
    """调用 Ollama API"""
    url = f"{OLLAMA_HOST}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError:
        raise ConnectionError("Ollama 未运行！请先安装并启动 Ollama：\n  https://ollama.com")

def chat(messages, model=None, stream=False):
    """对话"""
    model = model or DEFAULT_MODEL
    payload = {"model": model, "messages": messages, "stream": stream}
    return _post("/api/chat", payload)["message"]["content"]

def ask(symbol_char, user_input=""):
    """按符号模式生成回答"""
    from src.symbols import SINGLE_CHARS
    info = SINGLE_CHARS.get(symbol_char)
    if not info:
        return chat([{"role": "user", "content": user_input}])
    
    prompts = {
        "写":"你是写作助手。用中文口语化风格写作。用户说写什么，你就怎么写。",
        "改":"你是改写助手。用户给一段文字，你按他要求改写。保持原意。",
        "翻":"你是翻译助手。翻译要自然，不要机器味。默认中英互译。",
        "总":"你是总结助手。提炼核心要点，用 bullet point 列出。",
        "问":"你是问答助手。用大白话解释，别拽术语。不知道就说不知道。",
        "画":"你是绘画描述师。把用户描述转成英文绘图提示词，方便复制到 Midjourney 使用。",
        "想":"你是创意助手。点子要新颖、具体、落地。至少给 5 个。",
        "解":"你是通俗解释专家。用最简单比喻和日常语言解释。",
        "教":"你是耐心老师。从零开始一步步教。要具体可操作。",
        "比":"你是分析助手。从多个维度对比，列异同，给结论。",
        "查":"你是检索助手。基于已有知识回答问题，注明信息来自哪里。",
        "理":"你是整理助手。归类、排序、结构化。输出要清晰。",
        "编":"你是编程助手。说清楚每段代码干什么。",
        "转":"你是格式转换助手。按用户要求转换格式。",
        "算":"你是计算助手。给出计算过程和结果。",
        "记":"你是记忆助手。记住重要信息，下次对话可用。",
        "定":"你是定时助手。帮用户规划时间安排。",
        "说":"你是语音助手。把文字转成适合朗读的口语。",
        "试":"你是实验助手。帮用户尝试不同的方案。",
        "评":"你是评价助手。客观公正，优缺点都说。",
        "阅":"你是观察助手。只描述你看到的，不做分析和评价。",
        "空":"你是创造助手。从零开始，没有任何限制。",
        "止":"你是输出助手。给出最终结论，不再继续。",
        "兼":"你是整合助手。把多个信息合并在一起分析。",
        "或":"你是选择助手。帮用户对比不同选项，推荐最佳。",
    }
    sp = prompts.get(symbol_char, "你是有用的助手。用中文回答。")
    content = f"{sp}\n\n用户说：{user_input}" if user_input else sp
    return chat([
        {"role": "system", "content": sp},
        {"role": "user", "content": user_input or "请介绍自己能做什么"},
    ])

def check_ollama():
    """检查 Ollama 是否运行"""
    try:
        _post("/api/tags", {})
        return True
    except:
        return False

def pull_model(model=None):
    """拉取模型"""
    model = model or DEFAULT_MODEL
    print(f"正在拉取模型 {model}...")
    subprocess.run(["ollama", "pull", model])
    print("完成！")
