---
name: metacognition
description: Cross-session knowledge persistence — auto-retrieves known pitfalls at session start, records lessons when user says "remembered"
---

# MetaCognition Skill

## Session Start (AUTO)

At the start of every session, you MUST execute this before responding to the user:

1. Call `mcp__expert-brain__expert_brain__retrieve` with a query that summarizes the current project
   context. Use the project name, OS, and technologies in use (Python, bash, VS Code, Claude Code, etc.).

2. If results are returned AND the top result has severity "high" or "critical":
   > "⚠️ Known pitfalls from previous sessions:"
   > List each result with its symptom and resolution.

3. If results exist but are all medium/low severity:
   > "💡 Lessons from past sessions:"
   > List briefly.

4. If no results, proceed SILENTLY. Do NOT tell the user "no insights found."

## Recording Insights (TRIGGER)

When the user signals a lesson learned — saying "remembered", "记住了", "记下来",
"remember this", "learned a lesson", "don't fall for this again", or similar:

1. Synthesize a concise insight:
   - **symptom**: What went wrong (1 sentence)
   - **root_cause**: Technical explanation (1-2 sentences)
   - **resolution**: Verified fix or workaround (1 sentence)
   - **severity**: "low" | "medium" | "high" | "critical"

2. Call `mcp__expert-brain__expert_brain__draft_insight` with these fields.
   Include the optional `variants` field — 2-4 ways someone might describe the SAME problem
   in different phrasing. The variants help future search match regardless of exact wording.

3. Report the result:
   - new → "Recorded. Hit count: 1"
   - duplicate → "Already recorded (ID: {insight_id})."

## Promotion (TRIGGER)

When the user says "promote this rule", "固化这条规则", or when an insight
has hit_count >= 5 in the retrieve results:

1. Call `mcp__expert-brain__expert_brain__promote` with the insight_id.

2. Report the result:
   - promoted + has_remote=true →
     "Promoted to Live Constraint. Consider committing and pushing to share with your team."
   - promoted + has_remote=false →
     "Promoted to Live Constraint."
   - threshold_not_met →
     "Insufficient hit count (need >= 5)."

## Variants Guidelines

When generating query variants, describe the SAME problem from different angles:

- **Different verbs**: "fails" "not found" "not recognized" "silently fails" "throws error"
- **Different subjects**: reframe what broke — the tool, the command, the config, the environment
- **Different action context**: "trying to run" "after restart" "fresh install" "in editor"
- **Keep them short**: each variant is a single sentence or phrase

The variants are embedded alongside the symptom for semantic search. A user
describing the pitfall with any of these phrasings should match the insight.

## Constraints

- NEVER write insight content directly to files — ALWAYS use the MCP tool.
- NEVER append rules to CLAUDE.md — all insights go through the MCP tool.
- The user can say "ignore"/"忽略" to skip recording.
