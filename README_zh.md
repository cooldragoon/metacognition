# MetaCognition

可验证的跨模型认知架构 — 让 Claude Code 从"单次会话的聪明"进化为"跨会话的睿智"。

遇到诡异 bug 解决后说"记住了"，系统自动记录 insight，下次遇到同类问题自动检索并提示。单机优先，Markdown 存储，零外部依赖。

## 架构

```
用户说"记住了" → MetaCognition Skill → draft_insight (MCP tool)
                                            ├── 去重 (向量 > 0.92 | 关键词 > 0.6)
                                            ├── 写入 draft/*.md + query variants
                                            └── _embed() → .npy

会话启动 → Skill 自动调 retrieve → ensemble 搜索
                                    ├── model2vec 向量 (256-dim, 32ms)
                                    └── Jaccard 关键词 fallback (12ms)
                                    └── 命中? → 列出已知陷阱

hit_count >= 5 → promote (draft → live)
90d 未命中 → decay (hit_count 减半) → 180d → archive
```

## 快速开始

```bash
# 1. Clone
git clone <repo-url>
cd metacognition

# 2. 一键 setup — 自动安装所有依赖
bash expert-brain-server/setup.sh
# 具体包括：
#   pip install model2vec mcp numpy          ← Python 依赖
#   huggingface-cli download potion-base-8M   ← 嵌入模型 (60MB, 缓存后离线可用)
#   从种子数据生成 .npy 嵌入向量
#   重建 index.md 和 log.md

# 3. 验证
python expert-brain-server/test_scenarios.py    # 46 场景测试
python expert-brain-server/eval_search.py       # 搜索质量评估

# 4. 注册 MCP Server（用户级，推荐）
claude mcp add --scope user expert-brain -- python expert-brain-server/server.py

# 5. 重启 Claude Code
# Session Start 自动检索种子数据中的已知陷阱
```

**国内网络**：setup.sh 自动尝试 hf-mirror.com 镜像。也可手动设置：

```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download minishlab/potion-base-8M --local-dir expert-brain-server/models/potion-base-8M
```

## 使用

| 操作 | 触发方式 | 说明 |
|------|---------|------|
| **检索陷阱** | Session Start 自动 | 每次打开 Claude Code 自动展示 |
| **记录陷阱** | 说"记住了" | LLM 自动合成 insight + query variants |
| **晋升约束** | 自动 (hit >= 5) | draft → live，回写到 live/ 目录 |
| **衰减归档** | `expert_brain__decay` | 90d 减半，180d 归档 |

## 种子数据

新用户 clone 后自带 9 条示例 insight，覆盖：

| 领域 | 数量 | 示例 |
|------|:----:|------|
| MCP Server 开发 | 6 | 配置格式、SyntaxError、权限白名单、schema 不匹配 |
| Python 环境 | 2 | conda 终端问题、pip 版本冲突 |
| Claude Code | 1 | Windows bash hook 陷阱 |

## MCP Tools

| Tool | 输入 | 输出 |
|------|------|------|
| `expert_brain__draft_insight` | symptom, root_cause, resolution, severity, variants? | insight_id, status, hit_count |
| `expert_brain__retrieve` | query, top_k? | results[] |
| `expert_brain__promote` | insight_id | promotion status |
| `expert_brain__decay` | — | decayed/archived counts |

## 测试

```bash
python expert-brain-server/test_scenarios.py    # 46 场景, 0.2s
python expert-brain-server/test_scenarios.py --json  # 机器可读
python expert-brain-server/eval_search.py       # 搜索质量 (Recall/MRR)
```

当前搜索质量：

| 引擎 | Recall@5 | MRR | 延迟 |
|------|:-------:|:---:|:----:|
| 关键词 (Jaccard) | 100% | 0.833 | 12ms |
| Ensemble (向量+关键词) | 100% | 0.778 | 32ms |

## 项目结构

```
metacognition/
├── CLAUDE.md                          ← 项目指南
├── expert-brain-server/               ← MCP Server
│   ├── server.py                      ← 4 tools, stdio transport
│   ├── wiki_bridge.py                 ← 核心引擎 (markdown I/O + 搜索)
│   ├── tools/{draft_insight,retrieve}.py
│   ├── setup.sh                       ← 一键安装
│   ├── eval_search.py                 ← 搜索评估
│   └── test_scenarios.py              ← 场景测试
├── .claude/skills/metacognition/      ← MetaCognition Skill
│   └── SKILL.md                       ← 行为契约
├── .cursor/insights/wiki/             ← 知识存储 (种子数据)
│   ├── draft/ (7) + live/ (2)
│   ├── index.md + log.md
└── docs/superpowers/                  ← 设计文档
    ├── specs/  (3)
    └── plans/  (2)
```

## 设计哲学

- **单机优先**：所有数据本地 Markdown 文件，不依赖外部服务
- **渐进增强**：向量搜索不可用 → 关键词 fallback → 用户体验不退
- **知识生命周期**：draft → live → archive，自动衰减防膨胀
- **Query variants**：每条 insight 嵌入 2-4 种不同问法，提升语义检索召回

## License

MIT
