# MCP server tools not appearing in Claude Code after config change

> Sources: User observation, 2026-05-20
> Created: 2026-05-20
> Severity: medium
> Status: draft
> Hit Count: 27
> ID: 43df8fe15e36

## Overview
MCP server tools not appearing in Claude Code after config change. Root cause: Claude Code must be restarted to pick up mcpServers changes in settings.local.json. Resolution: After editing settings.local.json, close and reopen Claude Code for the MCP server to register

## Symptom
MCP server tools not appearing in Claude Code after config change

## Root Cause
Claude Code must be restarted to pick up mcpServers changes in settings.local.json

## Resolution
After editing settings.local.json, close and reopen Claude Code for the MCP server to register

## Query Variants
- MCP tools missing after restarting Claude Code
- configured MCP server but tools not showing up
- mcpServers in settings but no tools available
- after mcp add the tools did not appear

## Notes

## See Also
