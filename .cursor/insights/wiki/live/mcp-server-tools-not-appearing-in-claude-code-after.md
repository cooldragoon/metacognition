# MCP server tools not appearing in Claude Code after configuring settings.local.json

> Sources: User observation, 2026-05-20
> Created: 2026-05-20
> Severity: high
> Status: live
> Hit Count: 5
> ID: 15078b21adc7

## Overview
MCP server tools not appearing in Claude Code after configuring settings.local.json. Root cause: Claude Code does not support the `mcpServers` key in settings.local.json. MCP servers must be defined in a `.mcp.json` file at the project root, with `enableAllProjectMcpServers: true` in settings to auto-approve.. Resolution: Create `.mcp.json` in the project root with the `mcpServers` config, and add `enableAllProjectMcpServers: true` to `.claude/settings.local.json`

## Symptom
MCP server tools not appearing in Claude Code after configuring settings.local.json

## Root Cause
Claude Code does not support the `mcpServers` key in settings.local.json. MCP servers must be defined in a `.mcp.json` file at the project root, with `enableAllProjectMcpServers: true` in settings to auto-approve.

## Resolution
Use `claude mcp add --scope user` to register the server at user level (in `~/.claude.json`). Project `.mcp.json` is not reliably loaded at runtime (known Claude Code issue #15215). Verify with `claude mcp list` after registration. Also add `enableAllProjectMcpServers: true` to settings as a belt-and-suspenders measure.

## Notes

## See Also
