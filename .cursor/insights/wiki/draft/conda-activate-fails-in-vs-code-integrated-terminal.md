# conda activate fails in VS Code integrated terminal

> Sources: User observation, 2026-05-20
> Created: 2026-05-20
> Severity: high
> Status: draft
> Hit Count: 1
> ID: 55eb6bff0e8c

## Overview
conda activate fails in VS Code integrated terminal. Root cause: VS Code default terminal profile is PowerShell, which does not source conda hooks. Resolution: Set terminal.integrated.defaultProfile.windows to Git Bash in VS Code settings.json

## Symptom
conda activate fails in VS Code integrated terminal

## Root Cause
VS Code default terminal profile is PowerShell, which does not source conda hooks

## Resolution
Set terminal.integrated.defaultProfile.windows to Git Bash in VS Code settings.json

## Notes

## See Also
