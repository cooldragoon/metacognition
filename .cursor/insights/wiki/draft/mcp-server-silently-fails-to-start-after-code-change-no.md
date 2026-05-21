# MCP server silently fails to start after code change — no error message from Claude Code, no startup log generated

> Sources: User observation, 2026-05-21
> Created: 2026-05-21
> Severity: high
> Status: draft
> Hit Count: 0
> ID: 223d02ae31fb

## Overview
MCP server silently fails to start after code change — no error message from Claude Code, no startup log generated. Root cause: A malformed `try:` block without matching `except` or `finally` caused a Python SyntaxError in server.py. The process was never spawned, so Claude Code could only report "Failed to connect" with no diagnostic detail. The startup.log file was never created because the Python interpreter rejected the file before executing any statements.. Resolution: After editing MCP server code, run `python -c "import py_compile; py_compile.compile('server.py', doraise=True); print('Syntax OK')"` to catch syntax errors before restarting Claude Code

## Symptom
MCP server silently fails to start after code change — no error message from Claude Code, no startup log generated

## Root Cause
A malformed `try:` block without matching `except` or `finally` caused a Python SyntaxError in server.py. The process was never spawned, so Claude Code could only report "Failed to connect" with no diagnostic detail. The startup.log file was never created because the Python interpreter rejected the file before executing any statements.

## Resolution
After editing MCP server code, run `python -c "import py_compile; py_compile.compile('server.py', doraise=True); print('Syntax OK')"` to catch syntax errors before restarting Claude Code

## Notes

## See Also
