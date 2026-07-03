# -*- coding: utf-8 -*-
"""
FanLang 狼群模型路由测试
=========================
测试 WolfPackRouter 初始化、get_role、get_model、route、route_model。
"""
import pytest
from unittest.mock import patch, Mock
from fanlang.wolfpack import (
    WolfPackRouter, WOLF_PACK, TASK_ROUTING,
    EMBED_MODEL, MAIN_MODEL, REASON_MODEL, VISION_MODEL,
)


# ============================================================
# WOLF_PACK 配置验证
# ============================================================

class TestWolfPackConfig:
    """验证 WOLF_PACK 静态配置。"""

    def test_four_roles(self):
        """狼群必须有 4 个角色。"""
        assert len(WOLF_PACK) == 4

    def test_expected_roles(self):
        """验证 4 个角色名称。"""
        expected = {"斥候", "猎手", "智囊", "哨兵"}
        assert set(WOLF_PACK.keys()) == expected

    def test_scout_config(self):
        """斥候配置验证。"""
        scout = WOLF_PACK["斥候"]
        assert scout["model"] == EMBED_MODEL
        assert "shaw/dmeta-embedding-zh" in scout["model"]
        assert scout["auto"] is True

    def test_hunter_config(self):
        """猎手配置验证。"""
        hunter = WOLF_PACK["猎手"]
        assert hunter["model"] == MAIN_MODEL
        assert "qwen2.5" in hunter["model"]
        assert hunter["auto"] is True

    def test_thinker_config(self):
        """智囊配置验证。"""
        thinker = WOLF_PACK["智囊"]
        assert thinker["model"] == REASON_MODEL
        assert "deepseek-r1" in thinker["model"]
        assert thinker["auto"] is False

    def test_sentinel_config(self):
        """哨兵配置验证。"""
        sentinel = WOLF_PACK["哨兵"]
        assert sentinel["model"] == VISION_MODEL
        assert "minicpm" in sentinel["model"]
        assert sentinel["auto"] is False

    def test_all_have_required_keys(self):
        """每个角色必须有 model, desc, size, auto 字段。"""
        for name, config in WOLF_PACK.items():
            assert "model" in config, f"{name} 缺少 model"
            assert "desc" in config, f"{name} 缺少 desc"
            assert "size" in config, f"{name} 缺少 size"
            assert "auto" in config, f"{name} 缺少 auto"


class TestTaskRouting:
    """验证 TASK_ROUTING 配置。"""

    def test_task_routing_has_entries(self):
        assert len(TASK_ROUTING) >= 10

    def test_simple_qa_routes_to_hunter(self):
        assert TASK_ROUTING["简单问答"] == "猎手"

    def test_writing_routes_to_hunter(self):
        assert TASK_ROUTING["写作"] == "猎手"

    def test_deep_reasoning_routes_to_thinker(self):
        assert TASK_ROUTING["深度推理"] == "智囊"

    def test_image_understanding_routes_to_sentinel(self):
        assert TASK_ROUTING["图像理解"] == "哨兵"

    def test_vectorization_routes_to_scout(self):
        assert TASK_ROUTING["向量化"] == "斥候"

    def test_all_task_types(self):
        expected = {
            "简单问答", "写作", "翻译", "总结", "代码",
            "深度推理", "数学推理", "逻辑推理",
            "图像理解", "图文分析", "向量化",
        }
        assert set(TASK_ROUTING.keys()) == expected


# ============================================================
# WolfPackRouter 初始化
# ============================================================

class TestWolfPackRouterInit:
    """测试 WolfPackRouter 初始化。"""

    def test_default_initialization(self):
        router = WolfPackRouter()
        assert router._chat_func is None
        assert router._wolf_pack == WOLF_PACK

    def test_with_custom_chat_func(self):
        def dummy(model, msgs):
            return "ok"
        router = WolfPackRouter(chat_func=dummy)
        assert router._chat_func is dummy

    def test_with_custom_wolf_pack(self):
        custom_pack = {"自定义角色": {"model": "test", "desc": "test", "size": "1MB", "auto": True}}
        router = WolfPackRouter(wolf_pack=custom_pack)
        assert "自定义角色" in router._wolf_pack
        assert "斥候" not in router._wolf_pack

    def test_wolf_pack_property_returns_copy(self):
        """wolf_pack 属性应返回副本，修改不影响内部。"""
        router = WolfPackRouter()
        wp = router.wolf_pack
        wp["new"] = {}
        assert "new" not in router._wolf_pack


# ============================================================
# get_role()
# ============================================================

class TestGetRole:
    """测试 get_role()。"""

    def test_get_existing_role(self):
        router = WolfPackRouter()
        role = router.get_role("猎手")
        assert role is not None
        assert role["model"] == MAIN_MODEL

    def test_get_scout(self):
        router = WolfPackRouter()
        role = router.get_role("斥候")
        assert role is not None
        assert role["model"] == EMBED_MODEL

    def test_get_thinker(self):
        router = WolfPackRouter()
        role = router.get_role("智囊")
        assert role is not None

    def test_get_non_existing_role(self):
        router = WolfPackRouter()
        assert router.get_role("不存在") is None

    def test_get_empty_string(self):
        router = WolfPackRouter()
        assert router.get_role("") is None


# ============================================================
# get_model()
# ============================================================

class TestGetModel:
    """测试 get_model()。"""

    def test_get_hunter_model(self):
        router = WolfPackRouter()
        assert router.get_model("猎手") == MAIN_MODEL

    def test_get_scout_model(self):
        router = WolfPackRouter()
        assert router.get_model("斥候") == EMBED_MODEL

    def test_get_thinker_model(self):
        router = WolfPackRouter()
        assert router.get_model("智囊") == REASON_MODEL

    def test_get_sentinel_model(self):
        router = WolfPackRouter()
        assert router.get_model("哨兵") == VISION_MODEL

    def test_get_non_existing_role_returns_main(self):
        """不存在的角色返回 MAIN_MODEL 作为默认。"""
        router = WolfPackRouter()
        assert router.get_model("不存在") == MAIN_MODEL


# ============================================================
# route() 精确匹配
# ============================================================

class TestRouteExact:
    """测试 route() 精确匹配。"""

    def setup_method(self):
        self.router = WolfPackRouter()

    def test_simple_qa(self):
        assert self.router.route("简单问答") == "猎手"

    def test_writing(self):
        assert self.router.route("写作") == "猎手"

    def test_translation(self):
        assert self.router.route("翻译") == "猎手"

    def test_summary(self):
        assert self.router.route("总结") == "猎手"

    def test_code(self):
        assert self.router.route("代码") == "猎手"

    def test_deep_reasoning(self):
        assert self.router.route("深度推理") == "智囊"

    def test_math_reasoning(self):
        assert self.router.route("数学推理") == "智囊"

    def test_logic_reasoning(self):
        assert self.router.route("逻辑推理") == "智囊"

    def test_image_understanding(self):
        assert self.router.route("图像理解") == "哨兵"

    def test_image_text_analysis(self):
        assert self.router.route("图文分析") == "哨兵"

    def test_vectorization(self):
        assert self.router.route("向量化") == "斥候"


# ============================================================
# route() 模糊匹配
# ============================================================

class TestRouteFuzzy:
    """测试 route() 模糊匹配和关键词匹配。"""

    def setup_method(self):
        self.router = WolfPackRouter()

    def test_reasoning_keyword_in_task_type(self):
        """任务类型包含'推理'关键词应匹配智囊。"""
        assert self.router.route("复杂推理任务") == "智囊"

    def test_logic_keyword(self):
        assert self.router.route("逻辑问题") == "智囊"

    def test_math_keyword(self):
        assert self.router.route("数学问题") == "智囊"

    def test_proof_keyword(self):
        assert self.router.route("证明题") == "智囊"

    def test_analysis_keyword(self):
        assert self.router.route("数据分析") == "智囊"

    def test_image_keyword_in_task_type(self):
        assert self.router.route("图像生成") == "哨兵"

    def test_picture_keyword(self):
        assert self.router.route("图片处理") == "哨兵"

    def test_vision_keyword(self):
        assert self.router.route("视觉识别") == "哨兵"

    def test_embed_keyword(self):
        assert self.router.route("embedding") == "斥候"

    def test_similarity_keyword(self):
        assert self.router.route("相似度计算") == "斥候"

    def test_vector_keyword(self):
        assert self.router.route("向量数据库") == "斥候"

    def test_user_input_reasoning(self):
        """user_input 包含推理关键词也应匹配智囊。"""
        assert self.router.route("普通任务", "需要逻辑推理的任务") == "智囊"

    def test_user_input_vision(self):
        """user_input 包含视觉关键词应匹配哨兵。"""
        assert self.router.route("普通任务", "看看这张图片") == "哨兵"

    def test_user_input_embed(self):
        assert self.router.route("普通任务", "计算embedding") == "斥候"


# ============================================================
# route() 默认
# ============================================================

class TestRouteDefault:
    """测试 route() 默认返回猎手。"""

    def setup_method(self):
        self.router = WolfPackRouter()

    def test_unknown_task_default_hunter(self):
        """未知任务类型默认返回猎手。"""
        assert self.router.route("未知任务类型") == "猎手"

    def test_empty_string_default_hunter(self):
        assert self.router.route("") == "猎手"

    def test_no_keyword_match_default_hunter(self):
        assert self.router.route("日常聊天") == "猎手"


# ============================================================
# route_model()
# ============================================================

class TestRouteModel:
    """测试 route_model() 返回模型名。"""

    def setup_method(self):
        self.router = WolfPackRouter()

    def test_qa_route_to_main_model(self):
        assert self.router.route_model("简单问答") == MAIN_MODEL

    def test_reasoning_route_to_reason_model(self):
        assert self.router.route_model("深度推理") == REASON_MODEL

    def test_vision_route_to_vision_model(self):
        assert self.router.route_model("图像理解") == VISION_MODEL

    def test_vector_route_to_embed_model(self):
        assert self.router.route_model("向量化") == EMBED_MODEL

    def test_default_route_to_main_model(self):
        assert self.router.route_model("未知类型") == MAIN_MODEL


# ============================================================
# chat() 方法
# ============================================================

class TestChatMethod:
    """测试 chat() 方法。"""

    def test_chat_with_custom_func(self):
        """使用自定义 chat_func。"""
        def dummy(model, msgs):
            return f"使用模型 {model} 回复"
        router = WolfPackRouter(chat_func=dummy)
        result = router.chat([{"role": "user", "content": "hello"}], model_name="test-model")
        assert "test-model" in result

    def test_chat_with_role_name(self):
        """通过角色名选择模型。"""
        def dummy(model, msgs):
            return f"模型: {model}"
        router = WolfPackRouter(chat_func=dummy)
        result = router.chat([{"role": "user", "content": "hello"}], role_name="智囊")
        assert REASON_MODEL in result

    def test_chat_default_role(self):
        """不指定 model_name 和 role_name 时默认使用猎手。"""
        def dummy(model, msgs):
            return f"模型: {model}"
        router = WolfPackRouter(chat_func=dummy)
        result = router.chat([{"role": "user", "content": "hello"}])
        assert MAIN_MODEL in result

    def test_chat_model_name_overrides_role(self):
        """model_name 优先级高于 role_name。"""
        def dummy(model, msgs):
            return f"模型: {model}"
        router = WolfPackRouter(chat_func=dummy)
        result = router.chat(
            [{"role": "user", "content": "hello"}],
            model_name="override-model",
            role_name="智囊",
        )
        assert "override-model" in result


# ============================================================
# Edge Cases
# ============================================================

class TestWolfPackEdgeCases:
    """狼群模块边界情况测试。"""

    def test_route_with_only_user_input_no_task_type(self):
        """没有 task_type 但有 user_input 时。"""
        router = WolfPackRouter()
        # 空字符串作为 task_type
        result = router.route("", "需要看看这张图片")
        assert result == "哨兵"

    def test_route_both_empty(self):
        """task_type 和 user_input 都为空。"""
        router = WolfPackRouter()
        assert router.route("", "") == "猎手"

    def test_custom_wolf_pack_get_role(self):
        """自定义狼群配置的 get_role。"""
        custom = {"测试角色": {"model": "test-model", "desc": "test", "size": "1MB", "auto": False}}
        router = WolfPackRouter(wolf_pack=custom)
        assert router.get_role("测试角色")["model"] == "test-model"
        assert router.get_role("猎手") is None

    def test_custom_wolf_pack_get_model_default(self):
        """自定义狼群中不存在的角色返回 MAIN_MODEL。"""
        custom = {}
        router = WolfPackRouter(wolf_pack=custom)
        assert router.get_model("不存在") == MAIN_MODEL

    def test_exact_match_precedes_fuzzy(self):
        """精确匹配优先于模糊匹配。"""
        router = WolfPackRouter()
        # "向量化" 精确匹配斥候，即使 "化" 不在模糊关键词中
        assert router.route("向量化") == "斥候"

    def test_wolf_pack_shallow_copy_outer_dict(self):
        """外部修改外层 dict 不影响内部（浅拷贝的外层是独立的）。"""
        router = WolfPackRouter()
        wp = router.wolf_pack
        wp["新角色"] = {"model": "new"}
        assert "新角色" not in router._wolf_pack

    def test_chat_no_custom_func_raises_connection(self):
        """没有自定义函数且 Ollama 未运行时抛出 ConnectionError。"""
        router = WolfPackRouter()
        with patch("urllib.request.urlopen") as mock_urlopen:
            import urllib.error
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
            with pytest.raises(ConnectionError, match="Ollama"):
                router.chat([{"role": "user", "content": "hi"}])
