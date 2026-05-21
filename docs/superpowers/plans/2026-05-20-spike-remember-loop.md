# Spike: "记住了" 知识闭环 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify the "remember" closed loop — user says "remembered", system records a draft insight to the Karpathy-style wiki, and a fresh session retrieves it.

**Architecture:** MetaCognition Skill (prompt-only behavior contract) calls Expert Brain MCP Server (Python, stdio transport) which reads/writes Wiki files directly using karpathy-llm-wiki directory conventions. No database — plain Markdown files under `.cursor/insights/wiki/`.

**Tech Stack:** Python 3.11+, `mcp` SDK, karpathy-llm-wiki skill (for format conventions), file-system Markdown storage

---

### Task 1: Install and inspect karpathy-llm-wiki skill

**Files:**
- Create: `.cursor/insights/wiki/` (via skill install)

- [ ] **Step 1: Clone karpathy-llm-wiki to the skills directory**

```bash
git clone https://github.com/Astro-Han/karpathy-llm-wiki.git /tmp/karpathy-llm-wiki
```

- [ ] **Step 2: Inspect the skill's file format conventions**

Read the SKILL.md and any example wiki files to understand:
- How `.md` node files are structured (frontmatter? headings?)
- How `index.md` and `log.md` are formatted
- How wikilinks `[[...]]` connect pages

```bash
ls /tmp/karpathy-llm-wiki/
cat /tmp/karpathy-llm-wiki/SKILL.md
```

- [ ] **Step 3: Create the wiki directory scaffold**

```bash
mkdir -p .cursor/insights/wiki/draft
mkdir -p .cursor/insights/wiki/live
mkdir -p .cursor/insights/wiki/patterns
mkdir -p .cursor/insights/wiki/archive
touch .cursor/insights/wiki/index.md
touch .cursor/insights/wiki/log.md
```

- [ ] **Step 4: Hand-write a sample draft insight node**

Create `.cursor/insights/wiki/draft/test-insight.md` with content following the karpathy-llm-wiki convention discovered in Step 2. This file serves as reference for wiki_bridge.py.

```bash
echo "Verified: wiki directory scaffold exists with all subdirectories and index/log files"
```

Expected: `ls .cursor/insights/wiki/` shows `draft/ live/ patterns/ archive/ index.md log.md`

- [ ] **Step 5: Commit**

```bash
git add .cursor/insights/wiki/
git commit -m "feat: create wiki directory scaffold per karpathy-llm-wiki convention"
```

---

### Task 2: Scaffold Expert Brain MCP Server skeleton

**Files:**
- Create: `expert-brain-server/requirements.txt`
- Create: `expert-brain-server/server.py`
- Create: `expert-brain-server/tools/__init__.py`
- Create: `expert-brain-server/tools/draft_insight.py`
- Create: `expert-brain-server/tools/retrieve.py`
- Create: `expert-brain-server/wiki_bridge.py`
- Modify: `.claude/settings.local.json`

- [ ] **Step 1: Write requirements.txt**

```txt
mcp>=1.0.0
```

- [ ] **Step 2: Write server.py with stdio transport**

```python
"""Expert Brain MCP Server — minimal spike with 2 tools."""

import sys
import os
import asyncio

# Ensure server can import its own tools regardless of CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mcp.server.stdio
from mcp.server import Server
from mcp.types import Tool, TextContent

from tools.draft_insight import draft_insight
from tools.retrieve import retrieve

server = Server("expert-brain")


@server.tool()
async def expert_brain__draft_insight(
    symptom: str,
    root_cause: str,
    resolution: str,
    severity: str = "medium",
) -> dict:
    """Record a draft insight from a resolved bug or lesson learned.

    Args:
        symptom: What went wrong (1 sentence)
        root_cause: Technical explanation (1-2 sentences)
        resolution: Verified fix or workaround (1 sentence)
        severity: low, medium, high, or critical
    """
    return draft_insight(symptom, root_cause, resolution, severity)


@server.tool()
async def expert_brain__retrieve(query: str, top_k: int = 5) -> dict:
    """Search the wiki for insights matching the query.

    Args:
        query: Search terms
        top_k: Max results to return
    """
    return retrieve(query, top_k)


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

- [ ] **Step 3: Write placeholder tool modules**

`tools/__init__.py`:
```python
"""Expert Brain MCP tools."""
```

`tools/draft_insight.py`:
```python
"""Record a draft insight."""


def draft_insight(symptom: str, root_cause: str, resolution: str, severity: str = "medium") -> dict:
    """Placeholder — implemented in Task 4."""
    return {
        "insight_id": "not-implemented",
        "status": "error",
        "hit_count": 0,
    }
```

`tools/retrieve.py`:
```python
"""Retrieve insights from the wiki."""


def retrieve(query: str, top_k: int = 5) -> dict:
    """Placeholder — implemented in Task 5."""
    return {"results": []}
```

- [ ] **Step 4: Write placeholder wiki_bridge.py**

```python
"""Adapter layer for karpathy-llm-wiki file conventions.

Follows the karpathy-llm-wiki pattern:
- wiki/draft/*.md — draft insight nodes
- wiki/live/*.md  — promoted constraints
- wiki/index.md   — content directory
- wiki/log.md     — append-only timeline

All paths are relative to the project root.
"""

import os

WIKI_ROOT = os.path.join(os.getcwd(), ".cursor", "insights", "wiki")
DRAFT_DIR = os.path.join(WIKI_ROOT, "draft")
LIVE_DIR = os.path.join(WIKI_ROOT, "live")
INDEX_PATH = os.path.join(WIKI_ROOT, "index.md")
LOG_PATH = os.path.join(WIKI_ROOT, "log.md")


def ingest(symptom: str, root_cause: str, resolution: str, severity: str, insight_id: str) -> str:
    """Create a new draft insight .md node. Returns the file path."""
    raise NotImplementedError("Task 3")


def query(search: str, top_k: int = 5) -> list[dict]:
    """Search draft insights by keyword. Returns list of result dicts."""
    raise NotImplementedError("Task 3")


def check_duplicate(symptom: str, root_cause: str) -> str | None:
    """Check if a similar insight already exists. Returns insight_id or None."""
    raise NotImplementedError("Task 3")
```

- [ ] **Step 5: Register MCP server in settings.local.json**

Read the existing `.claude/settings.local.json`:

```bash
cat .claude/settings.local.json
```

Then write the updated config:

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "Bash(git clone *)",
      "Bash(pip install *)",
      "Bash(python *)"
    ]
  },
  "mcpServers": {
    "expert-brain": {
      "command": "python",
      "args": ["expert-brain-server/server.py"]
    }
  }
}
```

- [ ] **Step 6: Verify server imports correctly**

```bash
cd D:/cc/metacognition && python -c "
import sys
sys.path.insert(0, 'expert-brain-server')
from server import server
from tools.draft_insight import draft_insight
from tools.retrieve import retrieve
print('Server name:', server.name)
print('draft_insight imported OK')
print('retrieve imported OK')
print('All imports pass — tools will appear in Claude Code after restart')
"
```

Note: The MCP server uses stdio transport, so tools appear as MCP tools only when registered in Claude Code. The import check validates the server module loads cleanly. Verify actual tool listing by restarting Claude Code and checking available tools.

Expected: `Server name: expert-brain`, both imports OK.

- [ ] **Step 7: Commit**

```bash
git add expert-brain-server/ .claude/settings.local.json
git commit -m "feat: scaffold expert-brain MCP server with placeholder tools"
```

---

### Task 3: Implement wiki_bridge.py adapter

**Files:**
- Modify: `expert-brain-server/wiki_bridge.py` (replace placeholder)

- [ ] **Step 1: Write a slug helper for generating filenames**

In `wiki_bridge.py`, add above the existing functions:

```python
import re
import hashlib
from datetime import datetime, timezone


def _slug(text: str, max_len: int = 60) -> str:
    """Convert a symptom string to a filename-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[-\s]+", "_", slug)
    return slug[:max_len].strip("_")


def _generate_id(symptom: str, root_cause: str) -> str:
    """Generate a stable insight_id from semantic fingerprint."""
    return hashlib.sha256(
        (symptom[:100] + root_cause[:100]).encode()
    ).hexdigest()[:12]
```

- [ ] **Step 2: Implement ingest()**

Replace the `ingest` stub with:

```python
def ingest(symptom: str, root_cause: str, resolution: str, severity: str, insight_id: str) -> str:
    """Create a new draft insight .md node. Returns the file path."""
    os.makedirs(DRAFT_DIR, exist_ok=True)

    filename = f"{_slug(symptom)}.md"
    filepath = os.path.join(DRAFT_DIR, filename)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    content = f"""# {symptom}

## Symptom
{symptom}

## Root Cause
{root_cause}

## Resolution
{resolution}

## Metadata
- id: {insight_id}
- created: {now}
- severity: {severity}
- status: draft
- hit_count: 1
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    _append_log(f"Ingested [{symptom}](draft/{filename}) (id: {insight_id})")
    _update_index(filename, symptom)

    return filepath
```

- [ ] **Step 3: Implement _append_log()**

```python
def _append_log(entry: str) -> None:
    """Append a timestamped entry to log.md."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    os.makedirs(WIKI_ROOT, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"- {now}: {entry}\n")
```

- [ ] **Step 4: Implement _update_index()**

```python
def _update_index(filename: str, title: str) -> None:
    """Add an entry to index.md if not already present."""
    entry = f"- [{title}](draft/{filename})"

    os.makedirs(WIKI_ROOT, exist_ok=True)
    if not os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            f.write("# Wiki Index\n\n## Draft Insights\n\n")
        with open(INDEX_PATH, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        return

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        existing = f.read()

    if entry not in existing:
        # Append under ## Draft Insights heading, or create it
        if "## Draft Insights" in existing:
            lines = existing.split("\n")
            insert_idx = None
            for i, line in enumerate(lines):
                if line.strip() == "## Draft Insights":
                    insert_idx = i + 1
                    break
            if insert_idx is not None:
                lines.insert(insert_idx + 1, entry)
                with open(INDEX_PATH, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
        else:
            with open(INDEX_PATH, "a", encoding="utf-8") as f:
                f.write(f"\n## Draft Insights\n\n{entry}\n")
```

- [ ] **Step 5: Implement check_duplicate()**

Replace the `check_duplicate` stub with:

```python
def check_duplicate(symptom: str, root_cause: str) -> str | None:
    """Check if a similar insight already exists by keyword matching.
    
    Phase 1: simple keyword overlap. Phase 2 upgrades to vector similarity.
    """
    if not os.path.isdir(DRAFT_DIR):
        return None

    words = set(symptom.lower().split() + root_cause.lower().split())
    # Filter stop-words-ish short tokens
    keywords = {w for w in words if len(w) > 3}

    best_match = None
    best_score = 0.0

    for fname in os.listdir(DRAFT_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(DRAFT_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read().lower()
        file_words = set(content.split())
        file_keywords = {w for w in file_words if len(w) > 3}
        if not keywords:
            continue
        overlap = len(keywords & file_keywords) / len(keywords)
        if overlap > best_score:
            best_score = overlap
            best_match = fname

    if best_score > 0.6 and best_match:
        # Extract insight_id from the file
        fpath = os.path.join(DRAFT_DIR, best_match)
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("- id:"):
                    return line.split(":")[1].strip()
    return None
```

- [ ] **Step 6: Implement query()**

Replace the `query` stub with:

```python
def query(search: str, top_k: int = 5) -> list[dict]:
    """Search draft insights by keyword overlap. Returns ranked results."""
    if not os.path.isdir(DRAFT_DIR):
        return []

    query_words = set(search.lower().split())
    query_keywords = {w for w in query_words if len(w) > 2}

    results = []
    for fname in os.listdir(DRAFT_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(DRAFT_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        content_lower = content.lower()
        file_words = set(content_lower.split())
        file_keywords = {w for w in file_words if len(w) > 2}
        if not query_keywords:
            continue
        score = len(query_keywords & file_keywords) / len(query_keywords)

        if score > 0:
            meta = _parse_metadata(content)
            meta["score"] = round(score, 2)
            meta["wiki_path"] = f"draft/{fname}"
            results.append(meta)

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]


def _parse_metadata(content: str) -> dict:
    """Extract metadata fields from a wiki node."""
    meta = {}
    for line in content.split("\n"):
        if line.startswith("- id:"):
            meta["insight_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("- severity:"):
            meta["severity"] = line.split(":", 1)[1].strip()
        elif line.startswith("- hit_count:"):
            meta["hit_count"] = int(line.split(":", 1)[1].strip())
    # Extract symptom from the first heading
    for line in content.split("\n"):
        if line.startswith("# "):
            meta["symptom"] = line[2:].strip()
            break
    # Extract resolution
    in_resolution = False
    for line in content.split("\n"):
        if line.startswith("## Resolution"):
            in_resolution = True
            continue
        if in_resolution and line.startswith("##"):
            break
        if in_resolution and line.strip() and not line.startswith("##"):
            meta["resolution"] = line.strip()
            break
    return meta
```

- [ ] **Step 7: Test wiki_bridge.py independently**

Write a quick test script to verify:

```bash
cd D:/cc/metacognition && python -c "
import sys
sys.path.insert(0, 'expert-brain-server')
from wiki_bridge import ingest, query, check_duplicate, _generate_id

# Test ingest
id1 = _generate_id('conda fails in VS Code terminal', 'default profile is PowerShell')
path = ingest('conda fails in VS Code terminal', 'default profile is PowerShell',
              'switch default profile to Git Bash', 'high', id1)
print('Ingested to:', path)

# Test duplicate detection
dup = check_duplicate('conda not found in VS Code terminal', 'PowerShell profile issue')
print('Duplicate check:', dup)

# Test query
results = query('conda terminal PowerShell')
print('Query results:', len(results))
for r in results:
    print(f'  [{r[\"score\"]}] {r.get(\"symptom\", \"?\")}')
"
```

Expected: Ingest creates a `.md` file, duplicate check returns the ID, query returns 1 result with score > 0.

- [ ] **Step 8: Commit**

```bash
git add expert-brain-server/wiki_bridge.py
git commit -m "feat: implement wiki_bridge with ingest, query, and duplicate detection"
```

---

### Task 4: Implement draft_insight MCP tool

**Files:**
- Modify: `expert-brain-server/tools/draft_insight.py` (replace placeholder)

- [ ] **Step 1: Write the full implementation**

```python
"""Record a draft insight from a resolved bug or lesson learned."""

from wiki_bridge import ingest, check_duplicate, _generate_id


def draft_insight(
    symptom: str,
    root_cause: str,
    resolution: str,
    severity: str = "medium",
) -> dict:
    """Record a draft insight. Deduplicates before writing."""
    insight_id = _generate_id(symptom, root_cause)

    existing_id = check_duplicate(symptom, root_cause)
    if existing_id:
        return {
            "insight_id": existing_id,
            "status": "duplicate",
            "hit_count": -1,  # caller should re-read to get actual count
        }

    filepath = ingest(symptom, root_cause, resolution, severity, insight_id)

    return {
        "insight_id": insight_id,
        "status": "new",
        "hit_count": 1,
    }
```

- [ ] **Step 2: Verify the tool can be imported**

```bash
cd D:/cc/metacognition && python -c "
import sys
sys.path.insert(0, 'expert-brain-server')
from tools.draft_insight import draft_insight

result = draft_insight(
    'pytest fails in bash on Windows',
    'PATH does not include Python Scripts directory in Git Bash',
    'add Scripts path to .bashrc',
    'medium'
)
print('Result:', result)
assert result['status'] == 'new'
print('PASS')
"
```

Expected: `Result: {'insight_id': '...', 'status': 'new', 'hit_count': 1}` + `PASS`

- [ ] **Step 3: Verify duplicate detection works end-to-end**

```bash
cd D:/cc/metacognition && python -c "
import sys
sys.path.insert(0, 'expert-brain-server')
from tools.draft_insight import draft_insight

# Same issue, slightly different wording
result = draft_insight(
    'pytest not working in bash terminal on Windows',
    'Python Scripts directory missing from Git Bash PATH',
    'add Scripts path to .bashrc',
    'medium'
)
print('Result:', result)
assert result['status'] == 'duplicate'
print('PASS')
"
```

Expected: `Result: {'insight_id': '...', 'status': 'duplicate', ...}` + `PASS`

- [ ] **Step 4: Commit**

```bash
git add expert-brain-server/tools/draft_insight.py
git commit -m "feat: implement draft_insight MCP tool with dedup"
```

---

### Task 5: Implement retrieve MCP tool

**Files:**
- Modify: `expert-brain-server/tools/retrieve.py` (replace placeholder)

- [ ] **Step 1: Write the full implementation**

```python
"""Retrieve insights from the wiki."""

from wiki_bridge import query


def retrieve(query_text: str, top_k: int = 5) -> dict:
    """Search the wiki for insights matching the query."""
    results = query(query_text, top_k)
    return {"results": results}
```

- [ ] **Step 2: Verify retrieve finds the insight from Task 4**

```bash
cd D:/cc/metacognition && python -c "
import sys
sys.path.insert(0, 'expert-brain-server')
from tools.retrieve import retrieve

result = retrieve('pytest bash Windows PATH')
print('Results:', len(result['results']))
for r in result['results']:
    print(f'  [{r[\"score\"]}] {r.get(\"symptom\", \"?\")} — {r.get(\"resolution\", \"?\")}')
assert len(result['results']) >= 1
print('PASS')
"
```

Expected: at least 1 result with `pytest` in the symptom, score > 0, PASS.

- [ ] **Step 3: Commit**

```bash
git add expert-brain-server/tools/retrieve.py
git commit -m "feat: implement retrieve MCP tool"
```

---

### Task 6: Write MetaCognition SKILL.md

**Files:**
- Create: `metacognition-skill/SKILL.md`

- [ ] **Step 1: Write the behavior contract**

```markdown
---
name: metacognition
description: Cross-session knowledge persistence for Claude Code — records lessons learned and retrieves them in future sessions
---

# MetaCognition Skill

## Session Start

At the start of every session, call `expert_brain__retrieve` with a query summarizing
the current task context (project name, technologies in use, operating system).
If results are returned, present the top insights to the user:

> "I found these insights from previous sessions that may be relevant:"
> [list each insight with its symptom and resolution]

If no results, proceed silently.

## Recording Insights

When the user explicitly signals a lesson learned — saying "记住了", "记住这个坑",
"以后别踩这个", "记下来", or similar — do the following:

1. Synthesize a concise insight:
   - **symptom**: What went wrong (1 sentence)
   - **root_cause**: Technical explanation (1-2 sentences)
   - **resolution**: Verified fix or workaround (1 sentence)
   - **severity**: "low" | "medium" | "high" | "critical"

2. Call `expert_brain__draft_insight` with these fields.

3. Report the result:
   - If "new": "已记录。Hit count: 1"
   - If "duplicate": "这条经验已经被记录过了 (ID: {insight_id})。"

## Constraints

- NEVER write insight content directly to files.
- NEVER append rules to CLAUDE.md — all insights go through the MCP tool.
- The user can always say "忽略" to skip recording, or "删除那条" to request removal.
```

- [ ] **Step 2: Verify Claude Code can load the skill**

Check that the skill file follows the expected format (frontmatter + markdown body):

```bash
head -6 metacognition-skill/SKILL.md
```

Expected: `---` on line 1, `name: metacognition` on line 2, valid YAML frontmatter.

- [ ] **Step 3: Commit**

```bash
git add metacognition-skill/
git commit -m "feat: add MetaCognition skill behavior contract"
```

---

### Task 7: End-to-end cross-session verification

**Files:** None (verification only)

- [ ] **Step 1: Clean up any test insights from previous tasks**

```bash
rm -f .cursor/insights/wiki/draft/pytest*.md
# Rebuild index and log from scratch for clean verification
> .cursor/insights/wiki/log.md
cat > .cursor/insights/wiki/index.md << 'EOF'
# Wiki Index

## Draft Insights

EOF
```

- [ ] **Step 2: Simulate Session 1 — record an insight**

```bash
cd D:/cc/metacognition && python -c "
import sys
sys.path.insert(0, 'expert-brain-server')
from tools.draft_insight import draft_insight

result = draft_insight(
    'conda activate fails in VS Code integrated terminal',
    'VS Code default terminal profile is PowerShell, which does not source conda hooks',
    'Set terminal.integrated.defaultProfile.windows to Git Bash in VS Code settings.json',
    'high'
)
print('Session 1 — recorded:', result)
assert result['status'] == 'new'
"
```

- [ ] **Step 3: Verify the file artifacts exist**

```bash
echo "=== draft/ ==="
ls -la .cursor/insights/wiki/draft/
echo "=== index.md ==="
cat .cursor/insights/wiki/index.md
echo "=== log.md ==="
cat .cursor/insights/wiki/log.md
```

Expected:
- `draft/` contains a `.md` file with "conda" in the filename
- `index.md` lists the new entry under "## Draft Insights"
- `log.md` has a timestamped line with "Ingested"

- [ ] **Step 4: Simulate Session 2 — retrieve the insight**

```bash
cd D:/cc/metacognition && python -c "
import sys
sys.path.insert(0, 'expert-brain-server')
from tools.retrieve import retrieve

result = retrieve('conda terminal PowerShell activate Windows environment')
print('Session 2 — retrieved:', len(result['results']), 'results')
for r in result['results']:
    print(f'  [{r[\"score\"]}] {r.get(\"symptom\", \"?\")}')
    print(f'    resolution: {r.get(\"resolution\", \"?\")}')
assert len(result['results']) >= 1
assert result['results'][0]['score'] > 0
print('CROSS-SESSION LOOP VERIFIED')
"
```

Expected: `CROSS-SESSION LOOP VERIFIED` with at least 1 result (score > 0).

- [ ] **Step 5: Test duplicate detection end-to-end**

```bash
cd D:/cc/metacognition && python -c "
import sys
sys.path.insert(0, 'expert-brain-server')
from tools.draft_insight import draft_insight

result = draft_insight(
    'conda command not found in VS Code terminal on Windows',
    'PowerShell profile does not have conda hooks configured',
    'Switch terminal profile to Git Bash',
    'high'
)
print('Duplicate test:', result)
assert result['status'] == 'duplicate'
print('DUPLICATE DETECTION VERIFIED')
"
```

Expected: `DUPLICATE DETECTION VERIFIED`

- [ ] **Step 6: Record the verification result**

Create `.cursor/insights/wiki/draft/spike-verified.md` as a real-world first insight:

```bash
cd D:/cc/metacognition && python -c "
import sys
sys.path.insert(0, 'expert-brain-server')
from tools.draft_insight import draft_insight

result = draft_insight(
    'MCP server tools not appearing in Claude Code after config change',
    'Claude Code must be restarted to pick up mcpServers changes in settings.local.json',
    'After editing settings.local.json, close and reopen Claude Code for the MCP server to register',
    'medium'
)
print('Real insight recorded:', result)
"
```

- [ ] **Step 7: Final commit**

```bash
git add .cursor/insights/wiki/
git commit -m "verify: end-to-end cross-session remember loop passes"
```

---

## Verification Checklist

Before claiming spike complete, confirm all 9 items:

- [ ] Step 2 of Task 2: `expert_brain` server starts, 2 tools registered
- [ ] Step 7 of Task 3: wiki_bridge ingest/query/check_duplicate all work independently
- [ ] Step 2 of Task 4: draft_insight creates new insight, returns `status: new`
- [ ] Step 3 of Task 4: duplicate detection returns `status: duplicate`
- [ ] Step 2 of Task 5: retrieve finds the insight from Task 4
- [ ] Step 5 of Task 7: duplicate detection works when same issue re-recorded
- [ ] Step 4 of Task 7: cross-session retrieve finds the insight (the core loop)
- [ ] log.md has entries for every ingest action
- [ ] index.md has entries for every new insight
