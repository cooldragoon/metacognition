# Changelog

## 2026-05-21 — Phase 2: Knowledge Engine

### Added
- model2vec vector search (potion-base-8M, 256-dim, numpy-only) replacing sentence-transformers
- Ensemble search: vector + keyword merged with dedup
- Query variants: each insight embedded with 2-4 alternate phrasings
- Search evaluation script (`eval_search.py`) with Recall@5 / MRR metrics
- 46-scenario test suite (`test_scenarios.py`, 0.2s, 0 failures)
- Setup script (`setup.sh`): pip install + model download + .npy regeneration + index/log rebuild
- `has_remote` detection in promote() for team sharing hint
- `.gitignore`: exclude .npy embeddings, model files, generated index/log
- Seed data: 9 insights (7 draft + 2 live) covering MCP dev, Python env, Claude Code hooks

### Changed
- KNOWN ISSUE: project `.mcp.json` not loaded at runtime (Claude Code #15215) — workaround: `claude mcp add --scope user`
- MCP registration simplified: single `claude mcp add --scope user` command
- Search engine: ensemble (vector+catch + keyword fallback) replaces single-path keyword
- Index/log files rebuilt by setup.sh, no longer git-tracked
- SKILL.md moved to `.claude/skills/metacognition/` for auto-discovery

### Removed
- sentence-transformers (PyTorch, 2GB) → model2vec (numpy-only, 8MB model)
- Large product PDFs and v1.0 doc from repo

## 2026-05-20 — Phase 1: "Remembered" Closed Loop

### Added
- Expert Brain MCP Server (Python, stdio transport, 2 initial tools)
- `expert_brain__draft_insight`: record insights with keyword dedup
- `expert_brain__retrieve`: Jaccard keyword search
- wiki_bridge adapter layer (~300 lines)
- MetaCognition SKILL.md: Session Start auto-retrieve + "remembered" trigger
- Wiki directory scaffold (`.cursor/insights/wiki/`)
- Document format: markdown with blockquote metadata (karpathy-llm-wiki convention)
- Project CLAUDE.md with architecture overview and development conventions

### Fixed
- Parameter name mismatch in retrieve tool (query vs query_text)
- Markdown/table injection sanitization in wiki_bridge
- `os.getcwd()` → `__file__` path derivation

## 2026-05-21 — Phase 2 Extensions

### Added
- `expert_brain__promote`: draft → live constraint (hit_count >= 5)
- `expert_brain__decay`: 90-day hit_count halving, 180-day archiving
- 4th tool registered, permissions allow list updated
- Spike verification report

### Fixed
- SyntaxError from unclosed `try` block silently killed MCP server at startup
- MCP config must use user-level `claude mcp add --scope user`, not project `.mcp.json`
