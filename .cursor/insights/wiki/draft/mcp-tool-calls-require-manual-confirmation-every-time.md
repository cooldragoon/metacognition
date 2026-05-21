# MCP tool calls require manual confirmation every time — permission prompts interrupt workflow

> Sources: User observation, 2026-05-21
> Created: 2026-05-21
> Severity: low
> Status: draft
> Hit Count: 7
> ID: 1b5c8106dc4b

## Overview
MCP tool calls require manual confirmation every time — permission prompts interrupt workflow. Root cause: Each MCP tool must be explicitly added to the `permissions.allow` list in `.claude/settings.local.json`. New tools added to the server are not automatically whitelisted.. Resolution: Add all MCP tool names to the permissions.allow array: `mcp__expert-brain__expert_brain__draft_insight`, `mcp__expert-brain__expert_brain__retrieve`, `mcp__expert-brain__expert_brain__promote`, `mcp__expert-brain__expert_brain__decay`

## Symptom
MCP tool calls require manual confirmation every time — permission prompts interrupt workflow

## Root Cause
Each MCP tool must be explicitly added to the `permissions.allow` list in `.claude/settings.local.json`. New tools added to the server are not automatically whitelisted.

## Resolution
Add all MCP tool names to the permissions.allow array: `mcp__expert-brain__expert_brain__draft_insight`, `mcp__expert-brain__expert_brain__retrieve`, `mcp__expert-brain__expert_brain__promote`, `mcp__expert-brain__expert_brain__decay`

## Query Variants
- MCP tools keep asking for permission every call
- how to whitelist MCP tools permanently
- permission prompts interrupting development workflow
- auto-approve MCP tool calls without confirmation

## Notes

## See Also
