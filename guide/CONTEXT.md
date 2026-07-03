# 凡语 FanLang — AI 会话入口

> **你是谁、在哪、现在什么状态。每次会话从这里开始。**

---

## 【总】项目全貌

| 项 | 值 |
|:--|:--|
| 项目名 | 凡语 FanLang |
| 定位 | AI 交互层——用中文符号+组织形态为开源 AI 项目赋能 |
| 许可 | MIT |
| 仓库 | https://gitcode.com/desshu/FanLang |
| 本地路径 | C:\Work\FanLang |
| 入口文件 | publish.bat (发布) / README.md (门面) |
| 当前版本 | 0.1.0 |

### 三层产品

| 包 | 用途 | 状态 |
|:--|:--|:--|
| `fanlang` | 核心 (符号体系+OODA+RAG+术语+研讨厅) | ✅ 已实现 |
| `fanlang-streamlit` | Streamlit 插件 (render_symbol_bar) | ✅ 已实现 |
| `fanlang-langchain` | LangChain 集成 (OODAAgent+Retriever) | ✅ 已实现 |

### 质量保障

| 项 | 值 |
|:--|:--|
| 测试用例 | 413 个 (pytest) |
| 示例应用 | 5 个 (examples/) |
| CI | GitHub Actions (.github/workflows/ci.yml) |
| CHANGELOG | ✅ CHANGELOG.md |

### 原始项目遗迹

| 目录 | 来源 |
|:--|:--|
| `legacy/zhongwen/` | 精简版——25符号+Streamlit脚手架 |
| `legacy/ebook-rag/` | 完整版——RAG电子书问答+狼群模型 |

---

## 【查】当前状态

- **PyPI 发布**: ❌ 未发布（token 已配置在 .fanlang.json，待首次发布）
- **GitCode 推送**: ✅ 已推送（4次提交）
- **核心包导入测试**: ✅ 全部通过
- **研讨厅引擎**: ✅ 已实现（seminar.py, 514行, 7角色, 3组织形态）
- **论文文档**: ✅ paper-01 + paper-02
- **上下文文档体系**: 🚧 正在建设（本文件所在目录 guide/）

---

## 【改】最近变更

```
2026-07-03 · 测试体系 + 示例应用 + CHANGELOG + CI
            - 413 个测试用例 (fanlang/streamlit/langchain)
            - 5 个示例应用 (examples/)
            - CHANGELOG.md 版本历史
            - GitHub Actions CI (.github/workflows/ci.yml)
            - repaired: seminar.py sym.name → sym.name_cn bug
            - repaired: ooda.py act() 使用 _chat 统一出口
2026-07  · d8e9a12  feat: 盗火者研讨厅 (seminar.py + 论文01+02)
2026-07  · 828da8e  chore: 加密钥保护 (.fanlang.json → .gitignore)
2026-07  · 4153cba  feat: publish.py 自动化中间层
2026-07  · e437d52  v2: monorepo 重构 (3个pip包 + legacy归档)
2026-07  · (原始)    GitCode 初始提交 (精简版)
```

---

## 【想】设计哲学

1. **凡语不给用户用——给开源项目用。** 它不是独立产品，是赋能层。
2. **符号×组织形态 = 质量保证。** 单次LLM靠概率，组织结构靠约束。
3. **中间层消灭知识鸿沟。** publish.py 封装所有 DevOps 操作。
4. **文档即持久化上下文。** guide/ 目录就是我跨会话的记忆体。

---

## 【定】下一步

| 优先级 | 事项 | 阻塞 |
|:--|:--|:--|
| P0 | 首次 PyPI 发布（运行 publish --all） | - |
| P1 | GitHub 镜像仓库 | GitHub 账号 |
| P2 | 博客发布（掘金/知乎） | - |
| P3 | Open-WebUI 集成 | - |

---

## 【阅】文档导航

| 我需要知道什么 | 读哪个文件 |
|:--|:--|
| 项目是什么，什么状态 | `guide/CONTEXT.md` ← 本文件 |
| 常见任务怎么做 | `guide/SCENARIOS.md` |
| 为什么这么设计 | `guide/DECISIONS.md` |
| 有什么可复用的模式 | `guide/PATTERNS.md` |
| 接下来做什么 | `guide/ROADMAP.md` |
| 文档怎么维护 | `guide/GOVERN.md` |
| 学术级论证 | `docs/PAPER-01*.md` `docs/PAPER-02*.md` |
| 产品门面 | `README.md` |
| 给贡献者看的 | `CONTRIBUTING.md` |
| 技术博客 | `BLOG-01*.md` |

---

## 【兼】技术上下文速查

| 项目 | 说明 |
|:--|:--|
| 模型默认 | qwen2.5:1.5b (Ollama) |
| 向量模型 | shaw/dmeta-embedding-zh |
| UI 框架 | Streamlit 1.28+ |
| 向量库 | ChromaDB |
| Agent 框架 | 自研 (非 LangChain/CrewAI 依赖) |
| Python | 3.10+ |
| 开发环境 | Windows, PowerShell 5 |

---

> **AI 读取规则：每次新会话，先读本文件，再根据任务类型索引到对应文档。**
