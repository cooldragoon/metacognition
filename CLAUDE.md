# CLAUDE.md

MetaCognition — 为 Claude Code 构建的可验证跨模型认知架构。单机优先。

## 项目概述

本项目的核心创新是让 AI 辅助编程从"单次会话的聪明"进化为"跨会话的睿智"：遇到诡异 bug 解决后说"记住了"，系统自动记录 draft insight 到 Wiki，下次遇到同类问题时自动检索并提示。当前为 spike 验证阶段，仅实现"记住了"知识闭环。

## 项目结构

```
metacognition/
├── expert-brain-server/         ← MCP Server (Python, stdio transport)
│   ├── server.py                ← MCP 入口, 注册 2 个 tool
│   ├── tools/
│   │   ├── draft_insight.py     ← expert_brain__draft_insight
│   │   └── retrieve.py          ← expert_brain__retrieve
│   ├── wiki_bridge.py           ← 文件系统适配层 (karpathy-llm-wiki 约定)
│   └── requirements.txt         ← mcp>=1.0.0
├── metacognition-skill/
│   └── SKILL.md                 ← 行为契约 (session start → retrieve, "记住了" → draft)
├── .cursor/insights/wiki/       ← 知识存储 (Markdown 文件, karpathy-llm-wiki 格式)
│   ├── draft/                   ← 草稿态洞察
│   ├── live/                    ← 发布态约束 (Phase 2)
│   ├── patterns/                ← 成功模式
│   ├── archive/                 ← 归档
│   ├── index.md                 ← 内容目录
│   └── log.md                   ← 时间线日志
├── .claude/
│   └── settings.local.json      ← 注册 expert-brain MCP Server
└── docs/superpowers/
    ├── specs/                   ← 设计文档
    └── plans/                   ← 实施计划
```

## MCP Server

Expert Brain MCP Server 提供 2 个 tool：

- **expert_brain__draft_insight**: 记录草稿洞察。输入 symptom/root_cause/resolution/severity，自动去重后写入 Wiki。
- **expert_brain__retrieve**: 检索知识。输入 query，返回 top_k 条匹配洞察。

启动：Claude Code 通过 settings.local.json 自动启动，无需手动干预。Server 使用 stdio transport。

Wiki 文件格式约定见 `.cursor/insights/wiki/draft/test-insight.md`。

## 开发约定

- 当前为单机版，所有数据存储在本地 `.cursor/insights/wiki/` 目录
- Phase 1 仅做关键词去重 (Jaccard similarity)，不做向量检索
- MCP Server 代码保持在 300 行以内，wiki_bridge 是核心模块
- 不直接修改 CLAUDE.md 来记录洞察——全部通过 MCP tool
- Python 3.10+, `mcp>=1.0.0`

## 引用

全局行为准则见 `D:\cc\CLAUDE.md`。Superpowers 工作流技能已可用。
