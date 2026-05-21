# CLAUDE.md

MetaCognition — 为 Claude Code 构建的可验证跨模型认知架构。单机优先。

## 项目概述

让 AI 辅助编程从"单次会话的聪明"进化为"跨会话的睿智"：遇到诡异 bug 解决后说"记住了"，系统自动记录 draft insight 到 Wiki，下次遇到同类问题时自动检索并提示。当前 Phase 2 完成，具备完整的知识生命周期管理。

## 项目结构

```
metacognition/
├── README.md                          ← 新用户入口
├── CLAUDE.md                          ← 项目指南（本文件）
├── .gitignore                         ← 排除 .npy / models/ / .claude/
│
├── expert-brain-server/               ← MCP Server (Python, stdio transport)
│   ├── server.py                      ← MCP 入口, 注册 4 个 tool
│   ├── wiki_bridge.py                 ← 核心引擎 (markdown I/O + ensemble 搜索)
│   ├── tools/
│   │   ├── draft_insight.py           ← expert_brain__draft_insight
│   │   └── retrieve.py                ← expert_brain__retrieve
│   ├── setup.sh                       ← 一键安装 (pip + model + embedding 生成)
│   ├── requirements.txt               ← mcp + model2vec + numpy
│   ├── test_scenarios.py              ← 46 场景测试
│   ├── eval_search.py                 ← 搜索质量评估
│   └── models/                        ← 向量模型 (setup.sh 下载, gitignore 排除)
│
├── .claude/skills/metacognition/      ← MetaCognition Skill
│   └── SKILL.md                       ← 行为契约 (session start + "记住了")
│
├── .cursor/insights/wiki/             ← 知识存储 (种子数据 9 条)
│   ├── draft/ (7)                     ← 草稿态洞察
│   ├── live/  (2)                     ← 发布态约束 (hit_count >= 5 晋升)
│   ├── archive/                       ← 归档 (180d 未命中)
│   ├── index.md                       ← setup.sh 重建 (gitignored)
│   └── log.md                         ← setup.sh 重建 (gitignored)
│
└── docs/superpowers/                  ← 设计文档
    ├── specs/  (3)                    ← 设计 spec + 验证报告
    └── plans/  (2)                    ← 实施计划
```

## MCP Server

Expert Brain MCP Server 提供 4 个 tool：

| Tool | 功能 | 关键输入 |
|------|------|---------|
| `expert_brain__draft_insight` | 记录洞察 + 自动去重 + variant 嵌入 | symptom, root_cause, resolution, severity, variants? |
| `expert_brain__retrieve` | Ensemble 搜索 (向量 + 关键词) | query, top_k? |
| `expert_brain__promote` | 晋升 draft → live (hit >= 5) | insight_id |
| `expert_brain__decay` | 衰减 (90d 减半) + 归档 (180d) | — |

启动方式：`claude mcp add --scope user expert-brain -- python expert-brain-server/server.py`

> ⚠️ **已踩坑**: 
> - 不要在 `settings.local.json` 里写 `mcpServers`——Claude Code 不支持。用 `claude mcp add --scope user`。项目 `.mcp.json` 有已知 bug (Issue #15215)。
> - 改完 server.py 后跑 `python -c "import py_compile; py_compile.compile('server.py', doraise=True)"` 检查语法——SyntaxError 会导致 MCP 静默失败。
> - 新 tool 需要加到 `permissions.allow` 白名单。

## 搜索引擎

```
用户查询
    │
    ├── model2vec 向量搜索 (potion-base-8M, 256-dim, 32ms)
    │   ├── 嵌入来源: symptom + variants
    │   └── 不可用? → 关键词 Jaccard fallback (12ms)
    │
    └── Ensemble 合并:
        向量主导排序 + 关键词补充召回
        → Recall@5=100%, MRR=0.778
```

## 种子数据

9 条 insight 覆盖 MCP 开发 / Python 环境 / Claude Code hook 场景。新用户 clone 后跑 `bash setup.sh` 即可体验完整闭环。

## 开发约定

- 单机优先，所有数据本地 `.cursor/insights/wiki/` markdown 文件
- `.npy` 嵌入文件可重生成（不在 git 中），`setup.sh` 自动生成
- MCP Server 代码保持在 500 行以内，wiki_bridge 是核心模块
- 不直接修改 CLAUDE.md 来记录洞察——全部通过 MCP tool
- Python 3.10+, `mcp>=1.0.0`, `model2vec>=0.7.0`, numpy
- 向量模型不可用 → 关键词 fallback → 服务不退

## 环境搭建

```bash
# 一键 setup（首次需要网络下载 60MB 模型，之后离线可用）
bash expert-brain-server/setup.sh

# 国内网络先设置镜像：
export HF_ENDPOINT=https://hf-mirror.com

# 注册 MCP Server
claude mcp add --scope user expert-brain -- python expert-brain-server/server.py
```

## 测试

```bash
python expert-brain-server/test_scenarios.py    # 46 场景, 0.2s
python expert-brain-server/eval_search.py       # 搜索质量 (Recall/MRR)
python expert-brain-server/eval_search.py --json  # 机器可读
```

## 团队共享方案 (设计定稿，单机阶段不启用)

```
.cursor/insights/wiki/
├── draft/*.md    ← git 跟踪 (种子数据 + 团队决定共享的 insight)
├── live/*.md     ← git 跟踪 (晋升后的约束, 通过 PR 合并共享)
├── draft/*.npy   ← gitignore (setup.sh 生成)
├── live/*.npy    ← gitignore (setup.sh 生成)
├── index.md      ← gitignore (setup.sh 重建)
└── log.md        ← gitignore (setup.sh 重建)
```

个人 insight 保持在本地 `draft/`，不 commit。晋升到 `live/` 后, `git add live/xxx.md` → PR review → merge → 全员同步。非 append-only 文件（`.md` insight）不会产生合并冲突。

## 引用

全局行为准则见 `D:\cc\CLAUDE.md`。Superpowers 工作流技能已可用。
