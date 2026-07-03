# 凡语 · 路线图

> 接下来做什么、优先级、依赖关系。每次会话结束后更新。

---

## 【定】三阶段规划

### 阶段 1: 打磨 (2026 Q3 — 现在)

```
✅ 核心包实现 (fanlang 0.1.0)
✅ Streamlit 集成 (fanlang-streamlit 0.1.0)
✅ LangChain 集成 (fanlang-langchain 0.1.0)
✅ 研讨厅引擎 (seminar.py)
✅ 论文文档 (paper-01, paper-02)
✅ 自动化中间层 (publish.py)
✅ 上下文文档体系 (guide/)
✅ 测试体系 (413 个测试用例, pytest)
✅ 示例应用 (5 个 demo: 符号/OODA/终端/研讨厅/RAG)
✅ CHANGELOG.md
✅ GitHub Actions CI (.github/workflows/ci.yml)
⬜ 首次 PyPI 发布
⬜ GitHub 镜像仓库
```

### 阶段 2: 推广 (2026 Q3-4)

```
⬜ 技术博客发布（掘金/知乎/Medium）
⬜ Open-WebUI 贡献 PR
⬜ LlamaIndex contrib 包
⬜ GitHub star 突破 100
⬜ Product Hunt 英文版提交
⬜ 第一个外部贡献者
```

### 阶段 3: 生态 (2027)

```
⬜ Dify 插件
⬜ LangChain 官方 contrib
⬜ 企业咨询案例 × 1
⬜ 研讨厅论文投稿（学术会议）
⬜ 社区 meetup/workshop
```

---

## 【查】待办清单

| # | 事项 | 优先级 | 依赖 | 预计工时 |
|:--|:--|:--|:--|:--|
| 1 | 完成 guide/ 文档体系 | P0 | - | ✅ 已完成 |
| 2 | 首次 PyPI 发布 (3个包) | P0 | guide完成 | 10min |
| 3 | GitHub 镜像仓库 | P2 | GitHub账号 | 30min |
| 4 | 博客: "为什么AI工具需要能力菜单" | P1 | - | ✅ 已发布 (掘金/知乎) |
| 5 | 博客: "OODA vs LangChain Chain" | P2 | - | 3h |
| 6 | 写 examples/ 下5个demo | P2 | - | ✅ 已完成 |
| 7 | 搭建 GitHub Pages 文档站 | P2 | #3 | 2h |
| 8 | Open-WebUI 集成 PR | P3 | #3 | 8h |
| 9 | 企业版定价方案 | P3 | - | 3h |

---

## 【想】未决问题

| 问题 | 状态 | 备注 |
|:--|:--|:--|
| 是否需要 .whl 托管在 GitHub Releases? | 待定 | 目前只有 PyPI 渠道 |
| fanlang 是否需要 Docker 镜像? | 待定 | 用户仍需装 Ollama |
| 是否要写英文版 README? | 待定 | 海外推广需要 |
| 研讨厅论文投哪里? | 待定 | ACL / EMNLP / arXiv only |
| 是否需要企业版 License (非 MIT)? | 否 | MIT 足够，企业咨询服务另行收费 |
