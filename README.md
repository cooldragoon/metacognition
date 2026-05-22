# MetaCognition

> **Your AI coding assistant gets smarter with every session.**
>
> The same trap, never twice. The same bug, never debugged again. The same lesson, never relearned.
> Say "remembered" — and it truly remembers. Next time you open Claude Code, known pitfalls are already waiting for you to sidestep them.

A verifiable cross-model cognitive architecture for Claude Code. Record lessons learned, retrieve them across sessions, and build a knowledge base that compounds. Single-machine first, markdown-native, zero external dependencies.

## Architecture

```
User says "remembered" → MetaCognition Skill → draft_insight (MCP tool)
                                                 ├── dedup (vector > 0.92 | keyword > 0.6)
                                                 ├── write draft/*.md + query variants
                                                 └── _embed() → .npy

Session start → Skill auto-calls retrieve → ensemble search
                                              ├── model2vec vector (256-dim, 32ms)
                                              └── Jaccard keyword fallback (12ms)
                                              └── match? → surface known pitfalls

hit_count >= 5 → promote (draft → live)
90d stale → decay (hit_count halved) → 180d → archive
```

## Why MetaCognition

| Problem | Without MetaCognition | With MetaCognition |
|---------|----------------------|-------------------|
| **Session amnesia** | Debug the same environment trap from scratch every time | "remembered" → auto-retrieved next session |
| **Blind retries** | Claude tries 4-5 different fixes, each damaging the code tree more | Known root cause injected at the 2nd failure |
| **Rule bloat** | Dump everything into CLAUDE.md → context pollution → hallucinations | On-demand retrieval, only show relevant constraints |
| **Team knowledge silos** | Alice's Docker volume trap is Bob's 2-hour debug session | Live Constraint promotion → PR merge → team-wide guard |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/<user>/metacognition.git
cd metacognition

# 2. One-click setup (pip + model download + embedding generation)
bash expert-brain-server/setup.sh

# 3. Register MCP server
claude mcp add --scope user expert-brain -- python expert-brain-server/server.py

# 4. Restart Claude Code
# Session Start auto-retrieves seed insights — no configuration needed
```

**Users in China**: setup.sh auto-tries the hf-mirror.com mirror. You can also set it manually:

```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download minishlab/potion-base-8M --local-dir expert-brain-server/models/potion-base-8M
```

## How It Works With Superpowers and gstack

| System | Role | One-liner |
|--------|------|-----------|
| **Superpowers** | Process discipline | How you work — brainstorming → TDD → review → ship |
| **gstack** | Engineering quality | What you build — browser QA, expert review, design audit |
| **MetaCognition** | Knowledge persistence | What you learned — trap memory, cross-session retrieval, auto-reminders |

Superpowers keeps you from skipping steps. gstack keeps you from building the wrong thing. MetaCognition keeps you from falling into the same trap twice. They run independently — no hard dependencies.

## MCP Tools

| Tool | Input | Output |
|------|-------|--------|
| `expert_brain__draft_insight` | symptom, root_cause, resolution, severity, variants? | insight_id, status, hit_count |
| `expert_brain__retrieve` | query, top_k? | ranked results |
| `expert_brain__promote` | insight_id | promotion status (+ has_remote flag) |
| `expert_brain__decay` | — | decayed/archived counts |

## Search Quality

| Engine | Recall@5 | MRR | Latency |
|--------|:-------:|:---:|:-------:|
| Keyword (Jaccard) | 100% | 0.833 | 12ms |
| Ensemble (vector + keyword) | 100% | 0.778 | 32ms |

## Seed Insights (9 bundled)

| Domain | Count | Examples |
|--------|:----:|----------|
| MCP Server Dev | 6 | Config format, SyntaxError, permissions whitelist, schema mismatch |
| Python Env | 2 | conda terminal issue, pip version conflict |
| Claude Code | 1 | Windows bash hook traps |

## Testing

```bash
python expert-brain-server/test_scenarios.py    # 46 scenarios, 0.2s
python expert-brain-server/eval_search.py       # Search quality (Recall/MRR)
```

## Design Philosophy

- **Single-machine first**: all data in local markdown files, zero external services
- **Graceful degradation**: vector search unavailable → keyword fallback → user unaffected
- **Knowledge lifecycle**: draft → live → archive, auto-decay to prevent bloat
- **Query variants**: each insight embedded with 2-4 alternate phrasings for broad semantic recall

## License

MIT

---

[中文文档](README_zh.md)
