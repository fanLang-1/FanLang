
import json
import urllib.request
import urllib.error
from src.symbols import SINGLE_CHARS, CORE_7

OLLAMA_HOST = "http://localhost:11434"
MODEL = "qwen2.5:1.5b"

def _chat(messages):
    payload = {"model": MODEL, "messages": messages, "stream": False}
    try:
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())["message"]["content"]
    except urllib.error.URLError:
        return '{"error": "ollama_not_running"}'

# ============================================================
# Layer 4: Orient
# ============================================================
CLARITY_RULES = {
    "写": ["写什么类型", "什么主题", "多长", "什么风格"],
    "改": ["改什么", "改成什么样"],
    "翻": ["翻什么", "从哪到哪"],
    "总": ["总什么", "多短的摘要"],
    "问": ["问什么"],
    "画": ["画什么", "什么风格"],
    "想": ["想什么方面", "要几个点子"],
    "解": ["解什么概念", "用哪个领域打比方"],
    "教": ["教什么", "从什么水平开始"],
    "比": ["比什么和什么", "从哪些维度比"],
    "查": ["查什么", "在哪查"],
    "理": ["理什么", "理成什么样子"],
}

def orient(symbol_char, user_input):
    info = SINGLE_CHARS.get(symbol_char)
    if not info:
        return {"need_clarify": False, "summary": user_input}
    
    rules = CLARITY_RULES.get(symbol_char, [])
    
    # 短输入直接追问
    if len(user_input.strip()) < 8 and rules:
        return {"need_clarify": True, "question": rules[0] + "?"}
    
    rules_text = "\n".join("- " + r for r in rules)
    prompt = (
        "当前模式: " + info["e"] + "[" + symbol_char + "]" + info["n"] + "\n"
        "用户输入: " + user_input + "\n\n"
        "需要明确的信息:\n" + rules_text + "\n\n"
        "判断用户是否说清楚了? 如果否, 最该先问哪一个问题?(只问一个)\n"
        "输出JSON: {\"clear\": true/false, \"next_question\": \"问题\", \"summary\": \"总结\"}"
    )
    
    resp = _chat([
        {"role": "system", "content": "你是AI需求分析师,输出JSON。"},
        {"role": "user", "content": prompt},
    ])
    
    try:
        result = json.loads(resp)
        if "error" in result:
            return {"need_clarify": False, "summary": user_input}
        if result.get("clear"):
            return {"need_clarify": False, "summary": result.get("summary", user_input)}
        else:
            return {"need_clarify": True, "question": result.get("next_question", "能说具体点吗?")}
    except:
        return {"need_clarify": False, "summary": user_input}

# ============================================================
# Layer 3: Decide
# ============================================================
def decide(symbol_char, user_input, requirements):
    symbol_to_agent = {
        "写":"writing_agent", "改":"rewriting_agent", "翻":"translation_agent",
        "总":"summary_agent", "问":"qa_agent", "画":"drawing_agent",
        "想":"brainstorm_agent", "解":"explain_agent", "教":"teach_agent",
        "比":"compare_agent", "查":"search_agent", "理":"organize_agent",
        "编":"coding_agent", "转":"convert_agent", "算":"calculate_agent",
        "记":"memory_agent", "定":"schedule_agent", "说":"voice_agent",
        "试":"experiment_agent", "评":"evaluate_agent",
        "阅":"read_agent", "空":"create_agent", "止":"stop_agent",
        "兼":"combine_agent", "或":"choose_agent",
    }
    info = SINGLE_CHARS.get(symbol_char, {})
    return {
        "agent": symbol_to_agent.get(symbol_char, "general_agent"),
        "symbol_char": symbol_char,
        "symbol_name": info.get("n", ""),
        "requirements": requirements,
        "user_input": user_input,
    }

# ============================================================
# Layer 2: Act
# ============================================================
def act(plan):
    from src.engine import ask
    return ask(plan["symbol_char"], plan["user_input"])

# ============================================================
# Layer 1: Observe
# ============================================================
def observe(symbol_char, user_input, result):
    prompt = (
        "用户要求: " + user_input + "\n"
        "AI回答: " + result[:300] + "\n\n"
        "判断回答是否满足了用户要求? 如果否, 具体要改什么?\n"
        '输出JSON: {"satisfied": true/false, "feedback": "改进建议"}'
    )
    resp = _chat([
        {"role": "system", "content": "你是质量检查员,输出JSON。"},
        {"role": "user", "content": prompt},
    ])
    try:
        result = json.loads(resp)
        satisfied = result.get("satisfied", True)
        return {"satisfied": satisfied, "message": result.get("feedback", "") if not satisfied else "OK"}
    except:
        return {"satisfied": True, "message": ""}

# ============================================================
# 完整 OODA
# ============================================================
def ooda_cycle(symbol_char, user_input):
    orient_result = orient(symbol_char, user_input)
    if orient_result["need_clarify"]:
        return {"status": "clarify", "question": orient_result["question"]}, False
    
    summary = orient_result.get("summary", user_input)
    plan = decide(symbol_char, user_input, summary)
    result = act(plan)
    obs = observe(symbol_char, user_input, result)
    
    return {"status": "done", "result": result, "feedback": obs["message"]}, obs["satisfied"]

# ============================================================
# 符号检测
# ============================================================
def detect_symbol(user_input):
    """关键词匹配 + LLM 兜底"""
    kw_map = [
        ("写", ["写","文章","作文","文案","小说","稿子","报告","创作"]),
        ("改", ["改","润色","修改","编辑","修订","校对"]),
        ("翻", ["翻","翻译","译","英文","中文"]),
        ("总", ["总","总结","摘要","提炼","概括","归纳"]),
        ("画", ["画","图片","图像","插图","绘画","绘图"]),
        ("问", ["问","问题","什么","为什么","怎么","吗","如何","啥"]),
        ("想", ["想","点子","创意","灵感","建议","方案"]),
        ("解", ["解","解释","什么意思","含义","比喻","通俗"]),
        ("教", ["教","学","学习","教程","入门"]),
        ("比", ["比","对比","区别","差异","哪个好","不同"]),
        ("查", ["查","搜索","查找","检索"]),
        ("理", ["理","整理","分类","归档","梳理"]),
        ("编", ["编","代码","程序","编程","bug","开发"]),
        ("转", ["转","转换","转化为","格式","转成"]),
        ("算", ["算","计算","数据","统计"]),
        ("记", ["记","记住","保存","记录","收藏"]),
        ("定", ["定","定时","提醒","安排","计划","日程","每天"]),
        ("说", ["说","读","朗读","语音","发音"]),
        ("评", ["评","评价","评分","打分","评测","怎么样"]),
    ]
    for sym, keywords in kw_map:
        for kw in keywords:
            if kw in user_input:
                return sym
    
    sym_list = " ".join([v["e"]+"["+k+"]"+v["n"] for k,v in SINGLE_CHARS.items()])
    prompt = "用户说: " + user_input + "\n选一个最匹配的符号: " + sym_list + "\n只输出符号字符本身。"
    resp = _chat([
        {"role": "system", "content": "只输出一个汉字。"},
        {"role": "user", "content": prompt},
    ])
    resp = resp.strip()
    for c in SINGLE_CHARS:
        if c in resp:
            return c
    return "问"
