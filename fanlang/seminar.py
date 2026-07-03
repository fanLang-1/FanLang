# -*- coding: utf-8 -*-
"""
盗火者研讨厅 — 多智能体组织化协作引擎.

从个体智能到组织智能的跃迁：
  单次 LLM 调用 → 概率输出
  N 个角色 × K 轮对抗/评议 → 结构保证质量

核心理念：
  人类文明里最可靠的求真机制不是"一个聪明人"，
  而是"律师对辩"、"同行评议"、"编辑部流程"。
  把这些组织形式映射到 AI 智能体，输出质量不再依赖运气。

三种组织形态：
  - Pipeline（流水线）：串行接力，适合确定性任务
  - Panel（评议制）：多视角并行 + 汇总，适合创意任务
  - Adversarial（对撞式）：对立角色对抗 + 裁判裁决，适合论证任务

用法：
  from fanlang.seminar import SeminarHall, Role, PipelineOrg, PanelOrg, AdversarialOrg

  hall = SeminarHall()
  hall.add(Role("王编辑", "改", expertise="文字精炼"))
  hall.add(Role("李校对", "查", expertise="事实核查"))
  result = PipelineOrg(hall).execute("写一篇AI科普文章")
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .symbols import get_symbol


# ── 虚拟人 ────────────────────────────────────────────
@dataclass
class Role:
    """研讨厅中的一个虚拟角色.

    不同于简单的 prompt 模板——Role 有名称、有专长、有性格参数、
    有记忆（过往产出），具备连续性和可成长性。
    """

    name: str                      # 角色名（如 "王编辑"）
    symbol_char: str               # 绑定一个凡语符号，定义核心能力
    expertise: str = ""            # 专长描述
    personality: str = "专业、严谨" # 性格参数
    temperature: float = 0.7       # 创造性程度
    memory: List[Dict[str, str]] = field(default_factory=list)  # 持久化记忆

    def __post_init__(self):
        sym = get_symbol(self.symbol_char)
        if sym:
            self._symbol = sym
        else:
            raise ValueError(f"未知符号: {self.symbol_char}")

    @property
    def system_prompt(self) -> str:
        """生成角色的系统提示词."""
        sym = self._symbol
        lines = [
            f"你是 {self.name}，{self.expertise}。",
            f"你的核心能力是【{sym.char}】{sym.name}：{sym.description}。",
            f"性格：{self.personality}。",
            "",
            "任务规则：",
            f"1. 专注于你的角色职责——你是{self.expertise}，做你该做的事。",
            "2. 不要越界做别人的工作。",
            "3. 输出时标注你的角色名：【{role}】。",
            "4. 如果信息不足，明确说出你需要什么。",
        ]
        return "\n".join(lines).format(role=self.name)

    def remember(self, content: str, meta: str = ""):
        """存入记忆."""
        self.memory.append({
            "content": content,
            "meta": meta,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

    def recall(self, n: int = 5) -> str:
        """提取最近 n 条记忆."""
        recent = self.memory[-n:]
        if not recent:
            return ""
        return "\n".join(
            f"[{m['timestamp']}] {m['meta']}: {m['content'][:200]}"
            for m in recent
        )


# ── 研 讨 厅 ───────────────────────────────────────────
@dataclass
class RoundResult:
    """一轮讨论的结果."""
    role_name: str
    content: str
    round_num: int
    metadata: Dict[str, str] = field(default_factory=dict)


class SeminarHall:
    """研讨厅：管理多个角色，协调多轮讨论.

    研讨厅本身不定义组织形态——组织形态（流水线/评议/对撞）
    是外部传入的执行策略。研讨厅只负责：
      - 管理角色池
      - 提供统一的 chat 接口
      - 记录讨论日志
    """

    def __init__(self, chat_fn: Optional[Callable] = None):
        """
        Args:
            chat_fn: LLM 调用函数，签名 (system_prompt, user_message) -> str
                     不传则使用默认 Ollama 调用.
        """
        self.roles: Dict[str, Role] = {}
        self.log: List[RoundResult] = []
        self.chat_fn = chat_fn or self._default_chat

    def add(self, role: Role):
        """添加一个角色到研讨厅."""
        self.roles[role.name] = role

    def remove(self, name: str):
        """移除一个角色."""
        self.roles.pop(name, None)

    def get_role(self, name: str) -> Optional[Role]:
        return self.roles.get(name)

    def discuss(
        self,
        role: Role,
        message: str,
        round_num: int = 0,
    ) -> RoundResult:
        """让一个角色发言.

        Args:
            role: 发言角色
            message: 给角色的输入（可能是用户问题或上一环的输出）
            round_num: 当前轮次

        Returns:
            RoundResult
        """
        system = role.system_prompt
        if role.memory:
            system += f"\n\n你的过往记忆:\n{role.recall(5)}"

        response = self.chat_fn(system, message)

        result = RoundResult(
            role_name=role.name,
            content=response,
            round_num=round_num,
            metadata={"symbol": role.symbol_char},
        )
        self.log.append(result)
        role.remember(response, f"第{round_num}轮讨论")
        return result

    def _default_chat(self, system: str, user: str) -> str:
        """默认 Ollama 调用."""
        import requests

        try:
            resp = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "qwen2.5:1.5b",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "stream": False,
                    "options": {"temperature": 0.7},
                },
                timeout=120,
            )
            return resp.json()["message"]["content"]
        except Exception as e:
            return f"[研讨厅错误: {e}]"

    def summary(self) -> str:
        """输出讨论日志摘要."""
        lines = [f"研讨厅讨论记录 — {len(self.log)} 轮\n"]
        for r in self.log:
            lines.append(
                f"[第{r.round_num}轮] 【{r.metadata.get('symbol', '?')}】"
                f"{r.role_name}: {r.content[:150]}..."
            )
        return "\n".join(lines)


# ── 组织形态 A：流水线 Pipeline ─────────────────────────
class PipelineOrg:
    """流水线组织：角色串行接力.

    【写手】→ 【编辑】→ 【校对】→ 【主编】
    每个角色只看到上一环的输出，专注自己的职责。
    适合：写作、翻译、代码 review 等有明确工序的任务。
    """

    def __init__(self, hall: SeminarHall, roles: List[str]):
        """
        Args:
            hall: 研讨厅实例
            roles: 角色名列表（按执行顺序）
        """
        self.hall = hall
        self.role_names = roles

    def execute(self, task: str) -> Dict[str, Any]:
        """执行流水线.

        Args:
            task: 用户任务

        Returns:
            {result: 最终输出, log: 各阶段输出, rounds: 总轮次}
        """
        current = task
        stage_outputs = {}

        for i, name in enumerate(self.role_names):
            role = self.hall.get_role(name)
            if not role:
                stage_outputs[name] = f"[错误: 角色 {name} 不存在]"
                continue

            # 给当前角色传什么？
            if i == 0:
                prompt = f"任务：{current}"
            else:
                prompt = (
                    f"上一阶段的输出：\n---\n{current}\n---\n"
                    f"你是{role.expertise}，请基于以上内容完成你的工作。"
                )

            result = self.hall.discuss(role, prompt, round_num=i)
            current = result.content
            stage_outputs[name] = current

        return {
            "result": current,
            "stages": stage_outputs,
            "rounds": len(self.role_names),
        }


# ── 组织形态 B：评议制 Panel ────────────────────────────
class PanelOrg:
    """评议制组织：多视角并行产出 + 主编汇总.

    同一任务给多个角色，各自独立完成，最后由主编对比融合。
    适合：创意写作、策略分析、方案设计——需要多样性的任务。
    """

    def __init__(
        self,
        hall: SeminarHall,
        panel_roles: List[str],
        chief_role: str,
    ):
        """
        Args:
            hall: 研讨厅实例
            panel_roles: 评议组成员角色名列表
            chief_role: 主编角色名
        """
        self.hall = hall
        self.panel_names = panel_roles
        self.chief_name = chief_role

    def execute(self, task: str) -> Dict[str, Any]:
        """执行评议制.

        Returns:
            {result, versions, synthesis, rounds}
        """
        versions = {}

        # Phase 1: 并行产出
        for i, name in enumerate(self.panel_names):
            role = self.hall.get_role(name)
            if not role:
                versions[name] = f"[错误: {name} 不存在]"
                continue

            personalized_task = (
                f"任务：{task}\n"
                f"你作为{role.expertise}，请从你的专业视角完成此任务。"
            )
            result = self.hall.discuss(role, personalized_task, round_num=i)
            versions[name] = result.content

        # Phase 2: 主编汇总
        chief = self.hall.get_role(self.chief_name)
        if not chief:
            return {
                "result": "",
                "versions": versions,
                "synthesis": f"[错误: 主编 {self.chief_name} 不存在]",
                "rounds": len(self.panel_names),
            }

        synthesis_prompt = (
            "以下是多个专家对同一任务的独立产出。请你作为主编：\n"
            "1. 对比各版本的优缺点\n"
            "2. 提取每个版本最精彩的部分\n"
            "3. 融合成一个最优版本\n"
            "4. 说明你做关键决策的理由\n\n"
        )
        for name, content in versions.items():
            synthesis_prompt += f"【{name}的版本】:\n{content}\n\n"

        final = self.hall.discuss(
            chief, synthesis_prompt, round_num=len(self.panel_names)
        )

        return {
            "result": final.content,
            "versions": versions,
            "synthesis": final.content,
            "rounds": len(self.panel_names) + 1,
        }


# ── 组织形态 C：对撞式 Adversarial ─────────────────────
class AdversarialOrg:
    """对撞式组织：正反对抗 + 裁判裁决.

    【正方】立论 → 【反方】驳斥 → 【正方】修正 → 【裁判】裁决
    模拟律师辩论、学术 peer review、红蓝军对抗。
    适合：策略决策、逻辑论证、风险评估——需要严密性的任务。
    """

    def __init__(
        self,
        hall: SeminarHall,
        pro_role: str,
        con_role: str,
        judge_role: str,
        max_rounds: int = 3,
    ):
        """
        Args:
            hall: 研讨厅实例
            pro_role: 正方角色名
            con_role: 反方角色名
            judge_role: 裁判角色名
            max_rounds: 最多对撞轮数
        """
        self.hall = hall
        self.pro_name = pro_role
        self.con_name = con_role
        self.judge_name = judge_role
        self.max_rounds = max_rounds

    def execute(self, task: str) -> Dict[str, Any]:
        """执行对撞式辩论."""
        pro = self.hall.get_role(self.pro_name)
        con = self.hall.get_role(self.con_name)
        judge = self.hall.get_role(self.judge_name)

        if not all([pro, con, judge]):
            missing = [
                n for n, r in [
                    (self.pro_name, pro),
                    (self.con_name, con),
                    (self.judge_name, judge),
                ] if not r
            ]
            return {"result": "", "error": f"角色不存在: {missing}"}

        transcripts = []
        pro_position = None

        for rnd in range(self.max_rounds):
            if rnd == 0:
                # 正方立论
                prompt = f"命题：{task}\n请给出你最强有力的论证。"
                pro_result = self.hall.discuss(pro, prompt, round_num=rnd * 2)
                pro_position = pro_result.content
                transcripts.append({
                    "round": rnd,
                    "role": self.pro_name,
                    "action": "立论",
                    "content": pro_position,
                })
            else:
                # 正方回应反方质疑
                prompt = (
                    f"原始命题：{task}\n\n"
                    f"你的上一轮立場:\n{pro_position}\n\n"
                    f"反方提出的质疑:\n{current_attack}\n\n"
                    "请回应反方的质疑，修正你的论证。"
                )
                pro_result = self.hall.discuss(pro, prompt, round_num=rnd * 2)
                pro_position = pro_result.content
                transcripts.append({
                    "round": rnd,
                    "role": self.pro_name,
                    "action": "回应",
                    "content": pro_position,
                })

            # 反方驳斥
            attack_prompt = (
                f"命题：{task}\n\n"
                f"正方论证:\n{pro_position}\n\n"
                "请你作为专业的批评者，找出论证中的逻辑漏洞、"
                "事实错误、或遗漏的关键角度。要尖锐但不恶意。"
            )
            con_result = self.hall.discuss(con, attack_prompt, round_num=rnd * 2 + 1)
            current_attack = con_result.content
            transcripts.append({
                "round": rnd,
                "role": self.con_name,
                "action": "驳斥",
                "content": current_attack,
            })

        # 裁判裁决
        all_transcripts = "\n\n".join(
            f"[{t['role']} - {t['action']}]: {t['content']}"
            for t in transcripts
        )
        verdict_prompt = (
            f"命题：{task}\n\n"
            f"辩论记录:\n{all_transcripts}\n\n"
            "请你作为裁判：\n"
            "1. 总结双方核心论点\n"
            "2. 评估哪方论证更有力\n"
            "3. 给出最终裁决和建议\n"
            "4. 指出辩论中未被充分讨论的盲区"
        )
        verdict = self.hall.discuss(
            judge, verdict_prompt, round_num=self.max_rounds * 2
        )

        return {
            "result": verdict.content,
            "transcripts": transcripts,
            "verdict": verdict.content,
            "rounds": self.max_rounds * 2 + 1,
        }


# ── 快捷工厂 ────────────────────────────────────────────
def quick_seminar(chat_fn: Optional[Callable] = None) -> SeminarHall:
    """快速创建一个预配置好的研讨厅.

    包含 7 个常用角色：
      - 王写手 (写作)
      - 李编辑 (编辑润色)
      - 张校对 (事实核查)
      - 刘顾问 (分析建议)
      - 陈裁判 (裁决评审)
      - 赵创意 (创意脑暴)
      - 孙批判 (质疑批评)
    """
    hall = SeminarHall(chat_fn=chat_fn)
    hall.add(Role("王写手", "写", "写作输出", "文笔流畅，逻辑清晰"))
    hall.add(Role("李编辑", "改", "文字润色", "挑剔但不刻薄"))
    hall.add(Role("张校对", "查", "事实核查", "严谨，逐条验证"))
    hall.add(Role("刘顾问", "理", "分析整理", "结构化思维"))
    hall.add(Role("陈裁判", "评", "决策评审", "公正，不偏不倚"))
    hall.add(Role("赵创意", "想", "创意构思", "脑洞大，不拘一格"))
    hall.add(Role("孙批判", "解", "逻辑分析", "尖锐，直指要害"))
    return hall


def quick_pipeline(hall: Optional[SeminarHall] = None) -> PipelineOrg:
    """快捷流水线：写手 → 编辑 → 校对."""
    if hall is None:
        hall = quick_seminar()
    need = ["王写手", "李编辑", "张校对"]
    for name in need:
        if name not in hall.roles:
            raise ValueError(f"研讨厅缺少角色: {name}")
    return PipelineOrg(hall, need)


def quick_panel(hall: Optional[SeminarHall] = None) -> PanelOrg:
    """快捷评议制：王写手+赵创意+刘顾问 → 陈裁判."""
    if hall is None:
        hall = quick_seminar()
    return PanelOrg(
        hall,
        panel_roles=["王写手", "赵创意", "刘顾问"],
        chief_role="陈裁判",
    )


def quick_adversarial(hall: Optional[SeminarHall] = None) -> AdversarialOrg:
    """快捷对撞式：王写手 vs 孙批判 → 陈裁判."""
    if hall is None:
        hall = quick_seminar()
    return AdversarialOrg(
        hall,
        pro_role="王写手",
        con_role="孙批判",
        judge_role="陈裁判",
        max_rounds=2,
    )
