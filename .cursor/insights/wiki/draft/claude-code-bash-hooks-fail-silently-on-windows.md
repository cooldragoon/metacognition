# Claude Code bash hooks fail silently on Windows

> Sources: User observation, 2026-05-21
> Created: 2026-05-21
> Severity: medium
> Status: draft
> Hit Count: 4
> ID: ab6b6fa5b4f2

## Overview
Claude Code bash hooks fail silently on Windows. Root cause: Windows uses PowerShell as default shell; bash hooks need #!/usr/bin/env bash header and execute permission. Resolution: Add shell=^bash^ to hook config and ensure script has LF line endings

## Symptom
Claude Code bash hooks fail silently on Windows

## Root Cause
Windows uses PowerShell as default shell; bash hooks need #!/usr/bin/env bash header and execute permission

## Resolution
Add shell=^bash^ to hook config and ensure script has LF line endings
## Query Variants
- hook script not executing on Windows
- bash hook permission denied
- line ending CRLF breaks shell script
- shebang missing in hook command
## Notes

## See Also
