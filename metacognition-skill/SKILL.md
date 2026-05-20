---
name: metacognition
description: Cross-session knowledge persistence for Claude Code — records lessons learned and retrieves them in future sessions
---

# MetaCognition Skill

## Session Start

At the start of every session, call `expert_brain__retrieve` with a query summarizing
the current task context (project name, technologies in use, operating system).
If results are returned, present the top insights to the user:

> "I found these insights from previous sessions that may be relevant:"
> [list each insight with its symptom and resolution]

If no results, proceed silently.

## Recording Insights

When the user explicitly signals a lesson learned — saying "记住了", "记住这个坑",
"以后别踩这个", "记下来", or similar — do the following:

1. Synthesize a concise insight:
   - **symptom**: What went wrong (1 sentence)
   - **root_cause**: Technical explanation (1-2 sentences)
   - **resolution**: Verified fix or workaround (1 sentence)
   - **severity**: "low" | "medium" | "high" | "critical"

2. Call `expert_brain__draft_insight` with these fields.

3. Report the result:
   - If "new": "已记录。Hit count: 1"
   - If "duplicate": "这条经验已经被记录过了 (ID: {insight_id})。"

## Constraints

- NEVER write insight content directly to files.
- NEVER append rules to CLAUDE.md — all insights go through the MCP tool.
- The user can always say "忽略" to skip recording, or "删除那条" to request removal.
