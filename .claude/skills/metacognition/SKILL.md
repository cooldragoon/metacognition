---
name: metacognition
description: Cross-session knowledge persistence — auto-retrieves known pitfalls at session start, records lessons when user says "remembered"
---

# MetaCognition Skill

## Session Start (AUTO)

At the start of every session, you MUST execute this before responding to the user:

1. Call `mcp__expert-brain__expert_brain__retrieve` with a query that summarizes the current project
   context. Use the project name ("metacognition"), operating system ("Windows"), and technologies in use
   (Python, bash, VS Code, Claude Code).

2. If results are returned AND the top result has severity "high" or "critical":
   > "⚠️ 发现已知陷阱:"
   > List each result with its symptom and resolution.

3. If results exist but are all medium/low severity:
   > "💡 过往经验:"
   > List briefly.

4. If no results, proceed SILENTLY. Do NOT tell the user "no insights found."

## Recording Insights (TRIGGER)

When the user says "记住了", "记住这个坑", "以后别踩这个", "记下来", or similar:

1. Synthesize a concise insight:
   - **symptom**: What went wrong (1 sentence)
   - **root_cause**: Technical explanation (1-2 sentences)
   - **resolution**: Verified fix or workaround (1 sentence)
   - **severity**: "low" | "medium" | "high" | "critical"

2. Call `mcp__expert-brain__expert_brain__draft_insight` with these fields.

3. Report the result:
   - new → "已记录。Hit count: 1"
   - duplicate → "这条经验已经被记录过了。"

## Constraints

- NEVER write insight content directly to files — ALWAYS use the MCP tool.
- NEVER append rules to CLAUDE.md — all insights go through the MCP tool.
- The user can say "忽略" to skip recording.
