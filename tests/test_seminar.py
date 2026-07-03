# -*- coding: utf-8 -*-
"""
FanLang 研讨厅（多智能体协作）测试
===================================
测试 Role、SeminarHall、PipelineOrg、PanelOrg、AdversarialOrg 及快捷工厂。
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
from fanlang.seminar import (
    Role, SeminarHall, RoundResult,
    PipelineOrg, PanelOrg, AdversarialOrg,
    quick_seminar, quick_pipeline, quick_panel, quick_adversarial,
)


# ============================================================
# Role dataclass
# ============================================================

class TestRoleDataclass:
    """验证 Role 数据类的字段和行为。"""

    def test_role_minimal_init(self):
        """最小化初始化方式（不指定 expertise）。"""
        role = Role("测试角色", "写")
        assert role.name == "测试角色"
        assert role.symbol_char == "写"
        assert role.expertise == ""
        assert role.personality == "专业、严谨"
        assert role.temperature == 0.7
        assert role.memory == []

    def test_role_full_init(self):
        """完全初始化。"""
        role = Role("王写手", "写", expertise="写作输出", personality="文笔流畅", temperature=0.5)
        assert role.name == "王写手"
        assert role.expertise == "写作输出"
        assert role.personality == "文笔流畅"
        assert role.temperature == 0.5

    def test_unknown_symbol_raises_error(self):
        """未知符号抛出 ValueError。"""
        with pytest.raises(ValueError, match="未知符号"):
            Role("测试", "X")

    def test_system_prompt_generation(self):
        """验证 system_prompt 生成。"""
        role = Role("王写手", "写", expertise="写作输出")
        prompt = role.system_prompt
        assert "王写手" in prompt
        assert "写作输出" in prompt
        assert "写" in prompt or "✍️" in prompt or "写作" in prompt
        assert "任务规则" in prompt
        assert "不要越界" in prompt

    def test_system_prompt_includes_rolename(self):
        """system_prompt 中的 {role} 被替换为角色名。"""
        role = Role("测试编辑", "改", expertise="润色")
        prompt = role.system_prompt
        assert "【测试编辑】" in prompt

    def test_remember_and_recall(self):
        """记忆存储和提取功能。"""
        role = Role("测试", "问")
        assert len(role.memory) == 0

        role.remember("第一次对话", meta="开场")
        assert len(role.memory) == 1
        assert role.memory[0]["content"] == "第一次对话"
        assert "timestamp" in role.memory[0]

        role.remember("第二次对话", meta="深入")
        assert len(role.memory) == 2

    def test_recall_empty(self):
        """无记忆时 recall 返回空字符串。"""
        role = Role("测试", "问")
        assert role.recall() == ""

    def test_recall_limit(self):
        """recall 只返回最近的 n 条。"""
        role = Role("测试", "问")
        for i in range(10):
            role.remember(f"第{i}条记忆", meta=f"轮{i}")
        recalled = role.recall(n=3)
        # 应包含第7,8,9条
        assert "第7条" in recalled
        assert "第0条" not in recalled

    def test_role_memory_isolation(self):
        """不同角色的 memory 互不干扰。"""
        r1 = Role("A", "写")
        r2 = Role("B", "问")
        r1.remember("A的记忆")
        assert len(r1.memory) == 1
        assert len(r2.memory) == 0


# ============================================================
# SeminarHall
# ============================================================

class TestSeminarHall:
    """测试 SeminarHall 研讨厅。"""

    def test_init_empty(self):
        hall = SeminarHall()
        assert hall.roles == {}
        assert hall.log == []
        assert callable(hall.chat_fn)

    def test_add_role(self):
        hall = SeminarHall()
        role = Role("王写手", "写")
        hall.add(role)
        assert "王写手" in hall.roles
        assert hall.roles["王写手"] is role

    def test_add_multiple_roles(self):
        hall = SeminarHall()
        hall.add(Role("A", "写"))
        hall.add(Role("B", "改"))
        hall.add(Role("C", "查"))
        assert len(hall.roles) == 3

    def test_remove_existing(self):
        hall = SeminarHall()
        hall.add(Role("王写手", "写"))
        hall.remove("王写手")
        assert "王写手" not in hall.roles

    def test_remove_non_existing(self):
        """移除不存在的角色不会报错。"""
        hall = SeminarHall()
        hall.remove("不存在")  # 不应抛出异常

    def test_get_role_existing(self):
        hall = SeminarHall()
        role = Role("测试", "问")
        hall.add(role)
        assert hall.get_role("测试") is role

    def test_get_role_non_existing(self):
        hall = SeminarHall()
        assert hall.get_role("不存在") is None

    def test_discuss_with_chat_fn(self):
        """使用 chat_fn 进行讨论。"""
        def mock_chat(system, user):
            return "模拟回复"
        hall = SeminarHall(chat_fn=mock_chat)
        role = Role("王写手", "写")
        hall.add(role)
        result = hall.discuss(role, "写一篇文章")
        assert isinstance(result, RoundResult)
        assert result.role_name == "王写手"
        assert result.content == "模拟回复"
        assert result.round_num == 0
        assert result.metadata == {"symbol": "写"}

    def test_discuss_appends_log(self):
        """讨论结果附加到日志。"""
        hall = SeminarHall(chat_fn=lambda s, u: "回复")
        role = Role("测试", "问")
        hall.add(role)
        hall.discuss(role, "问题", round_num=1)
        assert len(hall.log) == 1
        assert hall.log[0].content == "回复"

    def test_discuss_auto_memory(self):
        """讨论后自动存入角色记忆。"""
        hall = SeminarHall(chat_fn=lambda s, u: "记住我")
        role = Role("测试", "问")
        hall.discuss(role, "问题", round_num=1)
        assert len(role.memory) == 1
        assert role.memory[0]["content"] == "记住我"

    def test_discuss_includes_memory_in_prompt(self):
        """有记忆时在 system prompt 中包含记忆。"""
        def mock_chat(system, user):
            assert "过往记忆" in system
            return "ok"
        hall = SeminarHall(chat_fn=mock_chat)
        role = Role("测试", "问")
        role.remember("旧记忆")
        hall.discuss(role, "问题")

    def test_default_chat_error_returns_error_message(self):
        """默认 chat 出错时返回错误信息。"""
        hall = SeminarHall()
        role = Role("测试", "问")
        # Mock requests.post 使其抛出异常，验证错误处理路径
        # 注意：requests 在 seminar._default_chat 函数内部导入，需 patch 全局路径
        with patch("requests.post") as mock_post:
            mock_post.side_effect = Exception("模拟网络错误")
            result = hall.discuss(role, "问题")
            assert "研讨厅错误" in result.content

    def test_summary_output(self):
        """summary 方法输出日志摘要。"""
        hall = SeminarHall(chat_fn=lambda s, u: "回复内容" * 20)
        role = Role("王写手", "写")
        hall.add(role)
        hall.discuss(role, "任务", round_num=0)
        summary = hall.summary()
        assert "研讨厅讨论记录" in summary
        assert "王写手" in summary
        assert "写" in summary or "✍️" in summary


# ============================================================
# PipelineOrg
# ============================================================

class TestPipelineOrg:
    """测试流水线组织。"""

    def test_pipeline_execute(self):
        """流水线串行执行。"""
        chat_log = []

        def chat_fn(system, user):
            chat_log.append(user)
            return f"处理: {user[:20]}"

        hall = SeminarHall(chat_fn=chat_fn)
        hall.add(Role("A", "写", expertise="写作"))
        hall.add(Role("B", "改", expertise="编辑"))
        hall.add(Role("C", "查", expertise="校对"))

        pipeline = PipelineOrg(hall, ["A", "B", "C"])
        result = pipeline.execute("写一篇文章")

        assert "result" in result
        assert "stages" in result
        assert "rounds" in result
        assert result["rounds"] == 3
        assert "A" in result["stages"]
        assert "B" in result["stages"]
        assert "C" in result["stages"]

    def test_pipeline_missing_role(self):
        """角色不存在时返回错误信息。"""
        hall = SeminarHall(chat_fn=lambda s, u: "ok")
        hall.add(Role("A", "写"))
        pipeline = PipelineOrg(hall, ["A", "不存在"])
        result = pipeline.execute("任务")
        assert "错误" in result["stages"]["不存在"]

    def test_pipeline_single_role(self):
        """只有一个角色的流水线。"""
        hall = SeminarHall(chat_fn=lambda s, u: "最终输出")
        hall.add(Role("A", "写"))
        pipeline = PipelineOrg(hall, ["A"])
        result = pipeline.execute("任务")
        assert result["result"] == "最终输出"
        assert result["rounds"] == 1


# ============================================================
# PanelOrg
# ============================================================

class TestPanelOrg:
    """测试评议制组织。"""

    def test_panel_execute(self):
        """评议制并行产出 + 主编汇总。"""
        outputs = {}

        def chat_fn(system, user):
            if "主编" in system:
                return "汇总结果"
            return "独立产出"

        hall = SeminarHall(chat_fn=chat_fn)
        hall.add(Role("专家A", "写", expertise="写作"))
        hall.add(Role("专家B", "想", expertise="创意"))
        hall.add(Role("主编C", "评", expertise="评审"))

        panel = PanelOrg(hall, panel_roles=["专家A", "专家B"], chief_role="主编C")
        result = panel.execute("设计一个方案")

        assert "result" in result
        assert "versions" in result
        assert "synthesis" in result
        assert "rounds" in result
        assert "专家A" in result["versions"]
        assert "专家B" in result["versions"]

    def test_panel_missing_chief(self):
        """主编不存在时返回错误信息。"""
        hall = SeminarHall(chat_fn=lambda s, u: "产出")
        hall.add(Role("专家A", "写"))
        panel = PanelOrg(hall, panel_roles=["专家A"], chief_role="不存在的主编")
        result = panel.execute("任务")
        assert "错误" in result["synthesis"]
        assert "专家A" in result["versions"]

    def test_panel_missing_panelist(self):
        """评议组成员不存在时返回错误信息。"""
        hall = SeminarHall(chat_fn=lambda s, u: "产出")
        hall.add(Role("主编", "评"))
        panel = PanelOrg(hall, panel_roles=["不存在"], chief_role="主编")
        result = panel.execute("任务")
        assert "错误" in result["versions"]["不存在"]


# ============================================================
# AdversarialOrg
# ============================================================

class TestAdversarialOrg:
    """测试对撞式组织。"""

    def test_adversarial_execute(self):
        """正反方对抗 + 裁判裁决。"""
        transcripts = []

        def chat_fn(system, user):
            transcripts.append(user[:30])
            if "裁判" in system:
                return "最终裁决"
            if "质疑" in user or "漏洞" in user:
                return "反方驳斥内容"
            return "正方立论内容"

        hall = SeminarHall(chat_fn=chat_fn)
        hall.add(Role("正方", "写", expertise="论证"))
        hall.add(Role("反方", "解", expertise="批判"))
        hall.add(Role("裁判", "评", expertise="裁决"))

        adv = AdversarialOrg(hall, pro_role="正方", con_role="反方", judge_role="裁判", max_rounds=2)
        result = adv.execute("AI是否安全")

        assert "result" in result
        assert "transcripts" in result
        assert "verdict" in result
        assert "rounds" in result
        assert len(result["transcripts"]) >= 4  # 2轮 × (正方+反方)

    def test_adversarial_missing_role(self):
        """缺少角色时返回错误。"""
        hall = SeminarHall(chat_fn=lambda s, u: "ok")
        hall.add(Role("正方", "写"))
        # 缺少反方和裁判
        adv = AdversarialOrg(hall, pro_role="正方", con_role="反方", judge_role="裁判", max_rounds=1)
        result = adv.execute("命题")
        assert "error" in result
        assert "反方" in result["error"] or "裁判" in result["error"]

    def test_adversarial_default_max_rounds(self):
        """默认 max_rounds=3。"""
        hall = SeminarHall(chat_fn=lambda s, u: "回复")
        hall.add(Role("正方", "写"))
        hall.add(Role("反方", "解"))
        hall.add(Role("裁判", "评"))
        adv = AdversarialOrg(hall, pro_role="正方", con_role="反方", judge_role="裁判")
        assert adv.max_rounds == 3


# ============================================================
# 快捷工厂
# ============================================================

class TestQuickFactories:
    """测试快捷工厂函数。"""

    def test_quick_seminar_has_7_roles(self):
        hall = quick_seminar()
        assert len(hall.roles) == 7
        expected = {"王写手", "李编辑", "张校对", "刘顾问", "陈裁判", "赵创意", "孙批判"}
        assert set(hall.roles.keys()) == expected

    def test_quick_seminar_with_chat_fn(self):
        def custom(s, u):
            return "ok"
        hall = quick_seminar(chat_fn=custom)
        assert hall.chat_fn is custom

    def test_quick_seminar_roles_have_valid_symbols(self):
        hall = quick_seminar()
        for role in hall.roles.values():
            assert hasattr(role, "_symbol")  # __post_init__ 应成功
            assert role.system_prompt

    def test_quick_pipeline_creates_org(self):
        pipeline = quick_pipeline()
        assert isinstance(pipeline, PipelineOrg)
        assert pipeline.role_names == ["王写手", "李编辑", "张校对"]

    def test_quick_pipeline_with_existing_hall(self):
        hall = quick_seminar()
        pipeline = quick_pipeline(hall)
        assert pipeline.hall is hall

    def test_quick_pipeline_missing_role_raises(self):
        hall = SeminarHall(chat_fn=lambda s, u: "ok")
        hall.add(Role("王写手", "写"))
        # 缺少李编辑和张校对
        with pytest.raises(ValueError, match="缺少角色"):
            quick_pipeline(hall)

    def test_quick_panel_creates_org(self):
        panel = quick_panel()
        assert isinstance(panel, PanelOrg)
        assert panel.panel_names == ["王写手", "赵创意", "刘顾问"]
        assert panel.chief_name == "陈裁判"

    def test_quick_panel_with_hall(self):
        hall = quick_seminar()
        panel = quick_panel(hall)
        assert panel.hall is hall

    def test_quick_adversarial_creates_org(self):
        adv = quick_adversarial()
        assert isinstance(adv, AdversarialOrg)
        assert adv.pro_name == "王写手"
        assert adv.con_name == "孙批判"
        assert adv.judge_name == "陈裁判"
        assert adv.max_rounds == 2

    def test_quick_adversarial_with_hall(self):
        hall = quick_seminar()
        adv = quick_adversarial(hall)
        assert adv.hall is hall


# ============================================================
# RoundResult
# ============================================================

class TestRoundResult:
    """验证 RoundResult 数据类。"""

    def test_round_result_fields(self):
        result = RoundResult(
            role_name="测试",
            content="内容",
            round_num=1,
            metadata={"key": "value"},
        )
        assert result.role_name == "测试"
        assert result.content == "内容"
        assert result.round_num == 1
        assert result.metadata == {"key": "value"}

    def test_default_metadata(self):
        result = RoundResult(role_name="测试", content="内容", round_num=0)
        assert result.metadata == {}


# ============================================================
# 集成测试
# ============================================================

class TestIntegration:
    """多组件集成测试。"""

    def test_quick_seminar_discuss(self):
        hall = quick_seminar(chat_fn=lambda s, u: "集成回复")
        role = hall.get_role("王写手")
        result = hall.discuss(role, "集成测试任务")
        assert result.content == "集成回复"
        assert result.role_name == "王写手"

    def test_pipeline_with_quick_seminar(self):
        hall = quick_seminar(chat_fn=lambda s, u: "流水线输出")
        pipeline = quick_pipeline(hall)
        result = pipeline.execute("集成流水线任务")
        assert result["rounds"] == 3
        assert result["result"] != ""

    def test_panel_with_quick_seminar(self):
        hall = quick_seminar(chat_fn=lambda s, u: "评议产出")
        panel = quick_panel(hall)
        result = panel.execute("集成评议任务")
        assert len(result["versions"]) == 3
        assert result["rounds"] == 4

    def test_adversarial_with_quick_seminar(self):
        def chat_fn(system, user):
            if "裁判" in system:
                return "法官说: 正方胜"
            if "质疑" in user or "漏洞" in user:
                return "反方: 漏洞很多"
            return "正方: 论证有力"

        hall = quick_seminar(chat_fn=chat_fn)
        adv = quick_adversarial(hall)
        result = adv.execute("集成对抗任务")
        assert "verdict" in result
        assert len(result["transcripts"]) >= 4
