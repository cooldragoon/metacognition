# Spike: "记住了" 知识闭环验证

> 版本: 1.0 | 日期: 2026-05-20 | 状态: 待评审

## 1. 目标

验证 MetaCognition 最核心的差异化价值——知识跨会话持久化——在 1-2 周内跑通闭合：

**会话 1**: 遇到 bug → 解决 → 用户说"记住了" → 系统自动记录 draft insight → 写入 Wiki  
**会话 2**: 打开新会话 → Librarian 预检 → 检索命中 → 提示用户已知陷阱

## 2. 范围

### 做
- 安装 karpathy-llm-wiki 社区 skill 作为 Wiki 存储引擎
- 自建 Expert Brain MCP Server（Python），实现 2 个 tool
- 编写 MetaCognition Skill（声明式 prompt 契约）
- 与 Superpowers Session Start 嵌入点集成
- 端到端跨会话验证

### 不做
- CodeGraph 物理层集成
- Live 晋升机制
- 多模型路由 / 外脑会诊
- Docker 沙盒验证
- 熔断与配额管理
- 知识衰减与归档
- 团队共享

## 3. 技术选型

| 决策 | 选择 | 理由 |
|------|------|------|
| Wiki 引擎 | karpathy-llm-wiki (Astro-Han) | Agent Skills 兼容，标准 raw/wiki/ 目录结构 |
| MCP Server 语言 | Python | MCP Python SDK 成熟，与 wiki 对接最直接 |
| 试验项目 | metacognition 自身 | 边建系统边用系统，场景真实 |
| 存储 | Markdown 文件 (.cursor/insights/wiki/) | karpathy-llm-wiki 约定，无需引入数据库 |
| 检索 | karpathy-llm-wiki 自带的 query 能力 | Phase 1 不引入向量检索 |

## 4. 项目骨架

```
metacognition/
├── expert-brain-server/
│   ├── server.py                 # MCP 入口, stdio transport
│   ├── tools/
│   │   ├── draft_insight.py      # 记录草稿洞察
│   │   └── retrieve.py           # 检索知识
│   ├── wiki_bridge.py            # karpathy-llm-wiki 适配层
│   └── requirements.txt
│
├── metacognition-skill/
│   └── SKILL.md                  # 行为契约
│
├── .cursor/insights/wiki/        # karpathy-llm-wiki 存储 (skill 安装后创建)
│   ├── draft/
│   ├── live/
│   ├── patterns/
│   ├── archive/
│   ├── index.md
│   └── log.md
│
└── .claude/
    └── settings.local.json       # 注册 expert-brain MCP Server
```

## 5. MCP Tool 接口

### 5.1 expert_brain/draft_insight

```
输入:
  symptom: string        # 问题现象（1 句）
  root_cause: string     # 根因（1-2 句）
  resolution: string     # 解决方案（1 句）
  severity: "low" | "medium" | "high" | "critical"   # 默认 "medium"

处理:
  1. 生成语义指纹: sha256(symptom[:100] + root_cause[:100])
  2. 关键词去重（Phase 2 升级为向量去重）
  3. 调用 wiki_bridge.ingest() → 写入 draft/*.md
  4. 追加 log.md + 更新 index.md

输出:
  insight_id: string
  status: "new" | "updated" | "duplicate"
  hit_count: int
```

### 5.2 expert_brain/retrieve

```
输入:
  query: string
  top_k: int            # 默认 5

处理:
  1. 调用 wiki_bridge.query()
  2. 按 relevance 排序

输出:
  results: [{ insight_id, symptom, resolution, hit_count, severity, wiki_path }]
```

## 6. wiki_bridge 适配层

不修改 karpathy-llm-wiki 源码。通过其 CLI 和文件约定对接：

- **写入路径**: 遵循 karpathy-llm-wiki 的 Markdown 节点格式（symptom/root_cause/resolution 映射到节点内容）
- **读取路径**: 调用 karpathy-llm-wiki 的 query 能力
- **目录约定**: `.cursor/insights/wiki/draft/`、`log.md`、`index.md`

如果社区 skill 接口不满足需求，wiki_bridge 隔离变更范围。

## 7. Superpowers 融合

### 7.1 Spike 范围内的嵌入点

| 嵌入点 | 触发时机 | MetaCognition 动作 |
|--------|---------|-------------------|
| Session Start (using-superpowers) | 会话启动 | `retrieve` 加载已知 draft insights，提示用户 |
| 执行中 | 用户说"记住了" | `draft_insight` 写入 Wiki |

### 7.2 后续迭代嵌入点（不在 spike 范围）

| 嵌入点 | 触发时机 | 计划动作 |
|--------|---------|---------|
| brainstorming 提方案前 | 探索选项时 | 检索类似设计决策、已知反模式 |
| writing-plans 拆任务前 | 分步规划时 | 检索受影响模块的历史脆弱性 |
| TDD Red 阶段 | 测试构造失败 | 检索测试模式 |
| systematic-debugging | 开始调试前 | 检索类似错误的历史根因 |
| verification-before-completion | 声称完成前 | 全量决策门检查 |
| finishing-a-development-branch | 合并前 | 完整 CI 检查清单 |

### 7.3 优先级规则

```
用户显式指令 > Superpowers 规程 > MetaCognition 约束 > 系统默认
```

MetaCognition 约束不能凌驾于用户显式指令。用户始终可以说"忽略那个约束，强制执行"。

### 7.4 Subagent 上下文隔离

未来多代理模式下，注入子代理的知识必须是干净的自包含 payload，不带当前会话历史。Spike 阶段不涉及子代理。

## 8. 实施步骤

| # | 步骤 | 产出 | 验证 |
|---|------|------|------|
| 1 | 安装 karpathy-llm-wiki skill | Wiki 目录就绪 | 手动 ingest 一条测试页面，确认 `.md` 节点生成 |
| 2 | 搭建 MCP Server 骨架 | `server.py` 启动 | `expert_brain` 出现在 Claude Code tool 列表中 |
| 3 | 实现 `wiki_bridge.py` | 适配层工作 | 独立脚本测试 ingest → 文件出现 |
| 4 | 实现 `draft_insight` tool | 写入闭环 | 手动触发，检查 draft/*.md、log.md、index.md |
| 5 | 实现 `retrieve` tool | 查询闭环 | 用已知 insight 的关键词查询，确认命中 |
| 6 | 写 `SKILL.md` | 行为契约 | Session start 自动调用 retrieve |
| 7 | 端到端验证 | 跨会话闭环 | 会话 1 记录 → 关闭 → 会话 2 检索命中 |

Step 4 和 5 互不依赖，可并行开发。

## 9. 成功标准

- [ ] 用户说"记住了"后，draft insight 出现在 `.cursor/insights/wiki/draft/` 中
- [ ] log.md 记录该 ingest 事件
- [ ] index.md 包含新 insight 的索引条目
- [ ] 关闭会话后，新会话启动时 `retrieve` 能查到旧 insight
- [ ] 同问题重复记录时，系统返回 "duplicate" 而非创建新节点
