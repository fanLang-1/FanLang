# 变更日志

## 0.1.1 (2026-07-03)

- **所有包**: PyPI 全量发布（`pyfanlang` / `pyfanlang-streamlit` / `pyfanlang-langchain`）
- **核心包**: 改用 src-layout 确保 wheel 正确包含源代码
- **修复**: `seminar.py` 字段名 bug + `ooda.py` 调用链修复
- **新增**: README 文档修复（三个包都有独立 README）


### 核心包 `fanlang`

- **符号体系**: 25 个单字符号（4 梯队 × 5 分类）+ 36 个双词符号（6 类）+ 12 个语法符号
- **OODA 循环引擎**: Orient → Decide → Act → Observe 四阶段交互循环，支持流式输出
- **QuickRAG**: 一行代码启动本地 RAG，支持 .txt / .md / .html / .pdf / .epub / .docx
- **术语映射**: 24 条英中 AI 术语双向查询
- **狼群模型路由器**: 4 角色（猎手/智囊/哨兵/斥候）自动任务路由
- **盗火者研讨厅**: 3 种组织形态（Pipeline/Panel/Adversarial）+ 7 个预制角色 + 快捷工厂

### Streamlit 插件 `fanlang-streamlit`

- `render_symbol_bar()` — 一行代码渲染能力符号按钮栏
- `render_symbol_picker()` — 按梯队分组的展开式符号选择器
- `render_terminology_tooltip()` — 术语悬停提示卡片
- 自定义 CSS 样式注入（蓝色主题）

### LangChain 集成 `fanlang-langchain`

- `OODAAgent` — 基于 OODA 循环的智能代理，支持工具调用与自评估
- `FanLangRetriever` — 封装 QuickRAG 的 LangChain 检索器

### 文档与工具

- 六份 guide 文档（CONTEXT / SCENARIOS / DECISIONS / PATTERNS / ROADMAP / GOVERN）
- 两篇论文（PAPER-01 组织形态学 / PAPER-02 研讨厅架构）
- 技术博客（BLOG-01: 为什么 AI 工具需要能力菜单）
- `publish.py` 发布自动化中间层
- 5 个示例应用
- 413 个测试用例
