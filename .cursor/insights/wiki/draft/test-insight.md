# Windows Path Handling in Cross-Platform Bash Scripts

> Sources: User observation, 2026-05-20
> Created: 2026-05-20

## Overview

When running bash commands on Windows (Git Bash, MSYS2, or Claude's bash tool), paths returned by Windows tools use backslashes and drive letters (e.g., `D:\cc\project\file.txt`). Forwarding these paths directly to bash commands causes failures because bash interprets backslashes as escape sequences. The reliable pattern is to always convert paths to forward-slash form before use.

## The Pattern

**Always normalize Windows paths before using them in bash:**

```bash
# WRONG — backslashes break bash:
cp "$(some-windows-tool)" /target/

# RIGHT — normalize first:
normalized=$(some-windows-tool | sed 's/\\/\//g')
cp "$normalized" /target/
```

**Key failure modes observed:**

1. **Escape interpretation**: Bash reads `\c` as an escape sequence, silently producing wrong paths
2. **Drive letter colon**: `D:` followed by `\` can be misparsed by some tools
3. **UNC paths**: `\\server\share` requires special handling (double-slash prefix)

**When this matters most:**

- Passing paths from Windows-native tools (cygpath, where.exe) to bash builtins
- Working with file paths returned by MCP tools on Windows
- Cross-session state where paths are stored and reused later

## Notes

This is a meta-level insight about the development environment itself. The pattern is recurring: every time a new tool or workflow touches Windows paths, the same normalization step is needed. The cost of forgetting is silent failures that are hard to debug.

## See Also

- [Bash Quoting Rules](../patterns/bash-quoting-rules.md) (planned)
- [Cross-Platform Path Conventions](../patterns/cross-platform-paths.md) (planned)
