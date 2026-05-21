# Spike 验证报告: "记住了" 知识闭环

> 日期: 2026-05-21 | 状态: Phase 2 已完成

## 1. 验证目标

验证 MetaCognition 最核心的假设——知识能否跨 Claude Code 会话持久化——是否成立。

## 2. 验证结论

**假设成立。** 跨会话知识闭环已跑通：会话 A 记录 insight → 关闭 → 会话 B 通过 MCP tool 检索命中。

## 3. 验证项

| # | 验证项 | 结果 | 证据 |
|---|--------|------|------|
| 1 | 用户说"记住了" → draft insight 写入 Wiki | ✅ 通过 | 4 条 insight 存在于 `draft/` 目录 |
| 2 | log.md 联动追加 | ✅ 通过 | `## [2026-05-20] ingest \| ...` 条目存在 |
| 3 | index.md 联动更新 | ✅ 通过 | draft 表格包含所有 insight 行 |
| 4 | 关键词去重 | ✅ 通过 | 同类问题返回 `status: duplicate` |
| 5 | 跨会话检索 | ✅ 通过 | 重启后 `expert_brain__retrieve` 返回 4 条结果 |
| 6 | Hit count 自动递增 | ✅ 通过 | 每次 retrieve 命中后 hit_count +1 |
| 7 | MCP 配置自动启动 | ✅ 通过 | `.mcp.json` + `enableAllProjectMcpServers` |

## 4. 设计假设纠正

以下假设在 spike 中被修正：

| 假设 | 文档中的设计 | 实际情况 | 影响 |
|------|-------------|---------|------|
| MCP 配置位置 | 写在 `settings.local.json` 的 `mcpServers` 键 | **不支持**。MCP Server 必须在 `.mcp.json` 中定义 | 高 — 修正了部署方式 |
| MCP SDK API | `@server.tool()` 装饰器 | MCP 1.27.1 使用 `@server.list_tools()` + `@server.call_tool()` | 中 — API 不同，逻辑相同 |
| Karpathy Wiki 格式 | 使用 `[[wikilinks]]` 和 YAML frontmatter | 无 wikilink，无 YAML frontmatter。元数据用 `> ` 块引用，链接用标准 markdown | 中 — wiki_bridge.py 的格式输出需适配 |
| 路径解析 | `os.getcwd()` 在 import 时求值 | 应基于 `__file__` 推导，避免 CWD 变化导致路径错误 | 低 — 已修正，当前 CWD 未变时不触发 |

## 5. 生产环境 insights（已记录）

Spike 过程中记录的 4 条真实洞察：

1. **HIGH** — conda 在 VS Code 终端失败 → 改 Terminal Profile 为 Git Bash
2. **HIGH** — MCP Server 配了 settings.local.json 不生效 → 用 `.mcp.json`
3. **MEDIUM** — MCP Server 改配置后 tool 不出现（早期认知）→ 重启 Claude Code
4. **LOW** — Windows 路径反斜杠在 bash 转义 → `sed` 转换

## 6. 已知限制

- **Jaccard 关键词搜索** 对语义相近但用词不同的查询得分低（如 "conda" 查询对 "MCP server" 得 0 分）。Phase 2 升级到向量检索可解决。
- **参数名不一致 bug** (query vs query_text) 已修复，但需重启 MCP Server 进程才生效——MCP Server 是长连接，代码更新后不会自动重载。
- **零分结果未过滤** — `retrieve` 返回 top_k 时包含 score=0.0 的结果。
- **Hit count 仅在 query 命中时递增**，不做衰减或归档。

## 7. Phase 2 验证 (2026-05-21)

| 验证项 | 结果 |
|--------|:----:|
| Session Start 自动检索 | ✅ |
| model2vec 向量搜索 + 关键词 fallback | ✅ |
| Ensemble 搜索 (向量+关键词合并) | ✅ |
| Query variants (每种 insight 嵌入多问法) | ✅ |
| Promote (hit >= 5 → live) | ✅ 2 条已晋升 |
| Decay (90d 减半, 180d 归档) | ✅ |
| 46 场景测试 (0.2s, 0 失败) | ✅ |
| 搜索质量: Recall@5=100%, MRR=0.778 | ✅ |
| 种子数据: 9 条 insight (7 draft + 2 live) | ✅ |
| 一键 setup.sh (pip + model + .npy) | ✅ |

## 8. 下一步

- 外脑会诊 (Phase 3) — 暂缓，WebSearch 替代
- CodeGraph 物理层 — 暂缓
- 团队共享 — 暂缓
- 持续积累 insight 喂养知识库
