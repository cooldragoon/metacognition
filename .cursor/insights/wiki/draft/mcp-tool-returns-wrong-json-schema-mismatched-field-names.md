# MCP tool returns wrong JSON schema — mismatched field names

> Sources: User observation, 2026-05-21
> Created: 2026-05-21
> Severity: medium
> Status: draft
> Hit Count: 0
> ID: 1aa0400c06f7

## Overview
MCP tool returns wrong JSON schema — mismatched field names. Root cause: Tool def in list_tools() uses camelCase but handler reads snake_case from arguments dict. Resolution: Align field names between list_tools() inputSchema and call_tool() argument keys

## Symptom
MCP tool returns wrong JSON schema — mismatched field names

## Root Cause
Tool def in list_tools() uses camelCase but handler reads snake_case from arguments dict

## Resolution
Align field names between list_tools() inputSchema and call_tool() argument keys
## Query Variants
- MCP tool parameter name mismatch
- tool argument not being passed correctly
- snake_case vs camelCase in MCP schema
- list_tools schema does not match call_tool handler
## Notes

## See Also
