# -*- coding: utf-8 -*-
"""
FanLang 狼群模型配置
====================
四个模型角色 + 模型路由器，根据任务类型自动选择合适的模型。
"""

from typing import Any, Callable, Dict, Literal, Optional


# ============================================================
# 狼群模型配置
# ============================================================
# 斥候 - 文本向量化（常驻，极小）
EMBED_MODEL: str = "shaw/dmeta-embedding-zh"

# 猎手 - 主力问答（常驻）
MAIN_MODEL: str = "qwen2.5:1.5b"

# 智囊 - 深度推理（按需加载）
REASON_MODEL: str = "deepseek-r1:1.5b"

# 哨兵 - 图文理解（按需加载）
VISION_MODEL: str = "minicpm-v4.6:1b"

# 狼群成员清单
WOLF_PACK: Dict[str, Dict[str, Any]] = {
    "斥候": {"model": EMBED_MODEL, "desc": "文本向量化", "size": "408MB", "auto": True},
    "猎手": {"model": MAIN_MODEL, "desc": "主力问答·通义千问", "size": "986MB", "auto": True},
    "智囊": {"model": REASON_MODEL, "desc": "深度推理·DeepSeek", "size": "1.1GB", "auto": False},
    "哨兵": {"model": VISION_MODEL, "desc": "图文理解·MiniCPM", "size": "1.6GB", "auto": False},
}

# 任务类型 → 推荐角色
TASK_ROUTING: Dict[str, str] = {
    "简单问答": "猎手",
    "写作": "猎手",
    "翻译": "猎手",
    "总结": "猎手",
    "代码": "猎手",
    "深度推理": "智囊",
    "数学推理": "智囊",
    "逻辑推理": "智囊",
    "图像理解": "哨兵",
    "图文分析": "哨兵",
    "向量化": "斥候",
}


# ============================================================
# 模型路由器
# ============================================================
class WolfPackRouter:
    """根据任务类型自动选择狼群模型角色。"""

    def __init__(
        self,
        chat_func: Optional[Callable] = None,
        wolf_pack: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Args:
            chat_func: 自定义聊天函数。签名: chat_func(model_name, messages) -> str
                      如果为 None，将默认使用 Ollama (http://localhost:11434/api/chat)
            wolf_pack: 自定义狼群配置。如果为 None，使用默认 WOLF_PACK
        """
        self._chat_func = chat_func
        self._wolf_pack = wolf_pack or dict(WOLF_PACK)

    @property
    def wolf_pack(self) -> Dict[str, Dict[str, Any]]:
        """获取当前狼群配置。"""
        return dict(self._wolf_pack)

    def get_role(self, role_name: str) -> Optional[Dict[str, Any]]:
        """根据角色名获取配置。"""
        return self._wolf_pack.get(role_name)

    def get_model(self, role_name: str) -> str:
        """根据角色名获取模型名。"""
        role = self._wolf_pack.get(role_name)
        if role:
            return role["model"]
        return MAIN_MODEL

    def route(
        self,
        task_type: str,
        user_input: str = "",
    ) -> str:
        """
        根据任务类型路由到合适的模型角色。

        Args:
            task_type: 任务类型（如"深度推理"、"写作"、"翻译"）
            user_input: 用户输入，用于辅助判断

        Returns:
            角色名（如"猎手"、"智囊"、"哨兵"、"斥候"）
        """
        # 精确匹配
        role = TASK_ROUTING.get(task_type)
        if role:
            return role

        # 模糊匹配：检查任务类型关键词
        reasoning_keywords = ["推理", "逻辑", "数学", "证明", "分析"]
        vision_keywords = ["图像", "图片", "视觉", "看图", "照片", "截图"]
        embed_keywords = ["向量", "相似度", "嵌入", "embed"]

        for kw in reasoning_keywords:
            if kw in task_type or kw in user_input:
                return "智囊"
        for kw in vision_keywords:
            if kw in task_type or kw in user_input:
                return "哨兵"
        for kw in embed_keywords:
            if kw in task_type or kw in user_input:
                return "斥候"

        # 默认使用猎手
        return "猎手"

    def route_model(
        self,
        task_type: str,
        user_input: str = "",
    ) -> str:
        """
        根据任务类型路由到合适的模型名。

        Args:
            task_type: 任务类型
            user_input: 用户输入

        Returns:
            模型名（如"qwen2.5:1.5b"）
        """
        role = self.route(task_type, user_input)
        return self.get_model(role)

    def chat(
        self,
        messages: list,
        model_name: Optional[str] = None,
        role_name: Optional[str] = None,
    ) -> str:
        """
        使用指定模型或角色进行对话。

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model_name: 直接指定模型名（优先级高于 role_name）
            role_name: 角色名（如"猎手"、"智囊"）

        Returns:
            模型回复文本
        """
        if model_name is None:
            model_name = self.get_model(role_name or "猎手")

        if self._chat_func:
            return self._chat_func(model_name, messages)

        # 默认使用 Ollama
        try:
            import json
            import urllib.request
            import urllib.error

            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False,
            }
            req = urllib.request.Request(
                "http://localhost:11434/api/chat",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())["message"]["content"]
        except urllib.error.URLError:
            raise ConnectionError(
                "Ollama 未运行！请先安装并启动 Ollama：\n  https://ollama.com"
            )
