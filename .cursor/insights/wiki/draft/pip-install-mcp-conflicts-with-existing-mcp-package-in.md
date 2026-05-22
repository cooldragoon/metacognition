# pip install mcp conflicts with existing mcp package in conda environment

> Sources: User observation, 2026-05-21
> Created: 2026-05-21
> Severity: low
> Status: draft
> Hit Count: 17
> ID: e10648fc3a66

## Overview
pip install mcp conflicts with existing mcp package in conda environment. Root cause: conda base env has a different mcp package; pip installs alongside causing import conflicts. Resolution: Always use a dedicated virtualenv or conda env for MCP server projects

## Symptom
pip install mcp conflicts with existing mcp package in conda environment

## Root Cause
conda base env has a different mcp package; pip installs alongside causing import conflicts

## Resolution
Always use a dedicated virtualenv or conda env for MCP server projects
## Query Variants
- mcp import error after pip install
- package namespace conflict with mcp
- wrong mcp module imported
- conda and pip package collision
## Notes

## See Also
