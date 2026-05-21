# MCP server tools not appearing in Claude Code after configuring settings.local.json

> Sources: User observation, 2026-05-20
> Created: 2026-05-20
> Severity: high
> Status: promoted
> Hit Count: 9
> ID: 15078b21adc7

## Overview
MCP server tools not appearing in Claude Code after configuring settings.local.json. Root cause: Claude Code does not support the `mcpServers` key in settings.local.json. MCP servers must be defined in a `.mcp.json` file at the project root, with `enableAllProjectMcpServers: true` in settings to auto-approve.. Resolution: Create `.mcp.json` in the project root with the `mcpServers` config, and add `enableAllProjectMcpServers: true` to `.claude/settings.local.json`

## Symptom
MCP server tools not appearing in Claude Code after configuring settings.local.json

## Root Cause
Claude Code does not support the `mcpServers` key in settings.local.json. MCP servers must be defined in a `.mcp.json` file at the project root, with `enableAllProjectMcpServers: true` in settings to auto-approve.

## Resolution
Create `.mcp.json` in the project root with the `mcpServers` config, and add `enableAllProjectMcpServers: true` to `.claude/settings.local.json`

## Query Variants
- MCP server configuration .mcp.json not being loaded
- project level MCP json ignored at runtime
- claude mcp add --scope user is the correct way
- MCP server registered but tools not found in session

## Notes

## See Also

> Promoted to: live
