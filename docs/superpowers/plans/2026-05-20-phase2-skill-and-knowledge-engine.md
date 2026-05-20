# Phase 2: Session Start + Knowledge Engine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make MetaCognition auto-fire at session start + upgrade knowledge engine from keyword to vector search with promotion and decay.

**Architecture:** Two tracks. Track B (Tasks 1-2): move skill to `.claude/skills/` standard path so Claude Code auto-loads it, with session-start `retrieve` instruction. Track A (Tasks 3-7): add vector embeddings via `all-MiniLM-L6-v2`, rewrite query/dedup, implement promote/decay.

**Tech Stack:** Python 3.10+, `mcp>=1.0.0`, `sentence-transformers`, existing wiki_bridge + MCP server

---

## Track B: Session Start Auto-Trigger

### Task B1: Move skill to .claude/skills/ and rewrite SKILL.md

**Files:**
- Delete: `metacognition-skill/SKILL.md`
- Create: `.claude/skills/metacognition/SKILL.md`

- [ ] **Step 1: Create directory and write the new SKILL.md**

```bash
mkdir -p D:/cc/metacognition/.claude/skills/metacognition
```

```markdown
---
name: metacognition
description: Cross-session knowledge persistence — auto-retrieves known pitfalls at session start, records lessons when user says "remembered"
---

# MetaCognition Skill

## Session Start (AUTO)

At the start of every session, you MUST execute this before responding to the user:

1. Call `mcp__expert-brain__expert_brain__retrieve` with a query that summarizes the current project
   context. Use the project name ("metacognition"), operating system ("Windows"), and technologies in use
   (Python, bash, VS Code, Claude Code).

2. If results are returned AND the top result has severity "high" or "critical":
   > "⚠️ 发现已知陷阱:"
   > List each result with its symptom and resolution.

3. If results exist but are all medium/low severity:
   > "💡 过往经验:"
   > List briefly.

4. If no results, proceed SILENTLY. Do NOT tell the user "no insights found."

## Recording Insights (TRIGGER)

When the user says "记住了", "记住这个坑", "以后别踩这个", "记下来", or similar:

1. Synthesize a concise insight:
   - **symptom**: What went wrong (1 sentence)
   - **root_cause**: Technical explanation (1-2 sentences)
   - **resolution**: Verified fix or workaround (1 sentence)
   - **severity**: "low" | "medium" | "high" | "critical"

2. Call `mcp__expert-brain__expert_brain__draft_insight` with these fields.

3. Report the result:
   - new → "已记录。Hit count: 1"
   - duplicate → "这条经验已经被记录过了。"

## Constraints

- NEVER write insight content directly to files — ALWAYS use the MCP tool.
- NEVER append rules to CLAUDE.md — all insights go through the MCP tool.
- The user can say "忽略" to skip recording.
```

- [ ] **Step 2: Delete old skill file**

```bash
rm -rf D:/cc/metacognition/metacognition-skill/
```

- [ ] **Step 3: Verify skill file is well-formed**

```bash
head -6 D:/cc/metacognition/.claude/skills/metacognition/SKILL.md
```

Expected: valid YAML frontmatter with `name: metacognition` and `description:`.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/ && git rm -r metacognition-skill/
git commit -m "refactor: move skill to .claude/skills/ with session-start auto-retrieve"
```

---

### Task B2: Verify session start auto-trigger

**Files:** None (verification only)

- [ ] **Step 1: Restart Claude Code and observe session start**

On next session start, Claude Code should automatically call `mcp__expert-brain__expert_brain__retrieve`
and present known high-severity pitfalls. Verify:

1. The tool call happens without user prompting
2. Results are presented with symptom + resolution
3. No "no insights found" message when results exist
4. No output when results are empty (optional — requires clearing wiki first)

- [ ] **Step 2: Verify "记住了" still works**

In session, say "记住了——刚才发现 settings.local.json 不支持 mcpServers" and verify
Claude Code calls `mcp__expert-brain__expert_brain__draft_insight`.

- [ ] **Step 3: Commit verification note**

```bash
git add .cursor/insights/wiki/
git commit -m "verify: session-start auto-retrieve works from .claude/skills/"
```

---

## Track A: Knowledge Engine Upgrade

### Task A3: Add vector embedding to wiki_bridge

**Files:**
- Modify: `expert-brain-server/wiki_bridge.py`
- Modify: `expert-brain-server/requirements.txt`

- [ ] **Step 1: Add sentence-transformers dependency**

```txt
mcp>=1.0.0
sentence-transformers>=3.0.0
```

- [ ] **Step 2: Install and choose model**

```bash
pip install sentence-transformers
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model loaded. Dim:', model.get_sentence_embedding_dimension())
"
```

Expected: `Model loaded. Dim: 384`

- [ ] **Step 3: Add embed function to wiki_bridge.py**

Add after the path constants and before `_slug()`:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

_EMBED_MODEL = None


def _get_model():
    """Lazy-load the embedding model (singleton)."""
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBED_MODEL


def _embed(text: str) -> np.ndarray:
    """Compute embedding vector for a text."""
    model = _get_model()
    return model.encode(text, normalize_embeddings=True)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two normalized vectors."""
    return float(np.dot(a, b))
```

- [ ] **Step 4: Store embedding alongside each draft insight**

Modify `ingest()` to compute and append an embedding after the file is written. Store as a `.npy` companion file:

```python
# In ingest(), after writing the .md file:
embedding = _embed(f"{symptom}\n{root_cause}\n{resolution}")
np_path = filepath.replace(".md", ".npy")
np.save(np_path, embedding)
```

- [ ] **Step 5: Verify embed + store works**

```bash
cd D:/cc/metacognition && python -c "
import sys; sys.path.insert(0, 'expert-brain-server')
from wiki_bridge import ingest, _generate_id, _embed
import os
import numpy as np

id1 = _generate_id('vector test symptom', 'vector test cause')
path = ingest('vector test symptom', 'vector test cause', 'test resolution', 'medium', id1)
npy_path = path.replace('.md', '.npy')
print('MD exists:', os.path.exists(path))
print('NPY exists:', os.path.exists(npy_path))
if os.path.exists(npy_path):
    emb = np.load(npy_path)
    print('Embedding shape:', emb.shape, 'norm:', np.linalg.norm(emb))
# Cleanup
os.remove(path)
os.remove(npy_path)
"
```

Expected: `MD exists: True`, `NPY exists: True`, `Embedding shape: (384,) norm: ~1.0`

- [ ] **Step 6: Commit**

```bash
git add expert-brain-server/requirements.txt expert-brain-server/wiki_bridge.py
git commit -m "feat: add vector embedding (all-MiniLM-L6-v2) to wiki_bridge ingest"
```

---

### Task A4: Rewrite query() with vector similarity

**Files:**
- Modify: `expert-brain-server/wiki_bridge.py`

- [ ] **Step 1: Rewrite query()**

Replace Jaccard keyword overlap with vector cosine similarity:

```python
def query(search: str, top_k: int = 5) -> list[dict]:
    """Search draft insights by vector similarity. Returns ranked results."""
    if not os.path.isdir(DRAFT_DIR):
        return []

    query_embedding = _embed(search)

    results = []
    for fname in os.listdir(DRAFT_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(DRAFT_DIR, fname)
        np_path = fpath.replace(".md", ".npy")
        if not os.path.exists(np_path):
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        doc_embedding = np.load(np_path)
        score = _cosine(query_embedding, doc_embedding)

        if score > 0:
            meta = _parse_metadata(content)
            meta["score"] = round(score, 4)
            meta["wiki_path"] = f"draft/{fname}"
            results.append(meta)

    results.sort(key=lambda r: r["score"], reverse=True)
    # Filter zero-score results
    results = [r for r in results if r["score"] > 0]
    # Bump hit count on returned results
    for r in results[:top_k]:
        fpath = os.path.join(DRAFT_DIR, os.path.basename(r["wiki_path"]))
        _bump_hit_count(fpath)
    return results[:top_k]
```

- [ ] **Step 2: Rewrite check_duplicate()**

Replace keyword overlap with vector cosine similarity:

```python
def check_duplicate(symptom: str, root_cause: str) -> str | None:
    """Check if a similar insight exists by vector similarity (threshold 0.92)."""
    if not os.path.isdir(DRAFT_DIR):
        return None

    query_embedding = _embed(f"{symptom}\n{root_cause}")

    best_score = 0.0
    best_id = None
    for fname in os.listdir(DRAFT_DIR):
        if not fname.endswith(".md"):
            continue
        np_path = os.path.join(DRAFT_DIR, fname.replace(".md", ".npy"))
        if not os.path.exists(np_path):
            continue
        doc_embedding = np.load(np_path)
        score = _cosine(query_embedding, doc_embedding)
        if score > best_score:
            best_score = score
            fpath = os.path.join(DRAFT_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                meta = _parse_metadata(f.read())
            best_id = meta.get("id", None)

    if best_score > 0.92 and best_id:
        return best_id
    return None
```

- [ ] **Step 3: Verify vector search outperforms keyword**

```bash
cd D:/cc/metacognition && python -c "
import sys; sys.path.insert(0, 'expert-brain-server')
from wiki_bridge import query

# This query uses different words than 'conda terminal PowerShell'
# but should still find the conda insight via semantic similarity
results = query('python environment not working in terminal')
print('Vector search results:')
for r in results:
    print(f'  [{r[\"score\"]:.4f}] {r[\"symptom\"]}')
assert len(results) >= 1, 'Should find conda insight via semantic similarity'
assert results[0]['score'] > 0.3, f'Score too low: {results[0][\"score\"]}'
print('PASS: vector search works')
"
```

Expected: conda insight found with score > 0.3 even though query uses different words.

- [ ] **Step 4: Verify duplicate detection with vectors**

```bash
cd D:/cc/metacognition && python -c "
import sys; sys.path.insert(0, 'expert-brain-server')
from wiki_bridge import check_duplicate

# Semantically similar to the conda insight, different words
dup = check_duplicate(
    'Python virtual environment fails to activate in VS Code',
    'Terminal shell does not load anaconda due to profile misconfiguration'
)
print('Duplicate check:', dup)
assert dup is not None, 'Should detect semantic duplicate'
print('PASS: vector dedup works')
"
```

Expected: Returns the conda insight ID.

- [ ] **Step 5: Commit**

```bash
git add expert-brain-server/wiki_bridge.py
git commit -m "feat: upgrade query and dedup to vector similarity (cosine)"
```

---

### Task A5: Implement promote (draft → live)

**Files:**
- Modify: `expert-brain-server/wiki_bridge.py`

- [ ] **Step 1: Add promote() function**

```python
def promote(insight_id: str) -> dict:
    """Promote a draft insight to live constraint. Returns promotion result."""
    # Find the draft file by ID
    draft_path = None
    draft_content = None
    if not os.path.isdir(DRAFT_DIR):
        return {"promoted_id": None, "status": "error", "reason": "no draft dir"}

    for fname in os.listdir(DRAFT_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(DRAFT_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        meta = _parse_metadata(content)
        if meta.get("id") == insight_id:
            draft_path = fpath
            draft_content = content
            break

    if draft_path is None:
        return {"promoted_id": None, "status": "error", "reason": "insight not found"}

    hit_count = int(_parse_metadata(draft_content).get("hit_count", 0))
    if hit_count < 5:
        return {
            "promoted_id": None,
            "status": "threshold_not_met",
            "reason": f"Hit count {hit_count} < 5",
        }

    # Write live constraint
    os.makedirs(LIVE_DIR, exist_ok=True)
    live_fname = os.path.basename(draft_path)
    live_path = os.path.join(LIVE_DIR, live_fname)

    # Update status in content
    live_content = draft_content.replace("> Status: draft", "> Status: live")
    with open(live_path, "w", encoding="utf-8") as f:
        f.write(live_content)

    # Mark original as promoted
    updated_content = draft_content.replace("> Status: draft", "> Status: promoted")
    updated_content += "\n> Promoted to: live\n"
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    _append_log("promote", _parse_metadata(draft_content).get("title", insight_id))
    _update_index(live_fname, _parse_metadata(live_content).get("title", insight_id), "promoted")

    return {"promoted_id": insight_id, "status": "promoted", "live_path": live_path}
```

- [ ] **Step 2: Add LIVE_DIR constant**

Add to path constants at the top of wiki_bridge.py:

```python
LIVE_DIR = os.path.join(WIKI_ROOT, "live")
```

- [ ] **Step 3: Register promote as MCP tool**

Add a third tool to `server.py`:

Register in `handle_list_tools()`:
```python
Tool(
    name="expert_brain__promote",
    description="Promote a draft insight to a live constraint.",
    inputSchema={
        "type": "object",
        "properties": {
            "insight_id": {"type": "string", "description": "The insight ID to promote"},
        },
        "required": ["insight_id"],
    },
),
```

Add dispatch in `handle_call_tool()`:
```python
if name == "expert_brain__promote":
    from wiki_bridge import promote as wiki_promote
    result = wiki_promote(insight_id=arguments.get("insight_id", ""))
    return [TextContent(type="text", text=str(result))]
```

- [ ] **Step 4: Verify promote works**

```bash
cd D:/cc/metacognition && python -c "
import sys; sys.path.insert(0, 'expert-brain-server')
from wiki_bridge import promote

# The conda insight has hit_count >= 5 by now
result = promote('55eb6bff0e8c')
print('Promotion result:', result)
assert result['status'] == 'promoted', f'Expected promoted, got {result[\"status\"]}'
print('PASS')
"
```

- [ ] **Step 5: Clean up and commit**

```bash
# Revert the promotion for clean state (optional — or keep the first live insight!)
git add expert-brain-server/wiki_bridge.py expert-brain-server/server.py
git commit -m "feat: implement promote (draft -> live constraint)"
```

---

### Task A6: Implement decay

**Files:**
- Modify: `expert-brain-server/wiki_bridge.py`

- [ ] **Step 1: Add decay() function**

```python
def decay() -> dict:
    """Run knowledge decay: halve hit_count for insights untouched in 90 days,
    archive those untouched in 180 days.
    """
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    decay_90d = now - timedelta(days=90)
    decay_180d = now - timedelta(days=180)

    decayed = 0
    archived = 0

    if not os.path.isdir(DRAFT_DIR):
        return {"decayed": 0, "archived": 0}

    for fname in os.listdir(DRAFT_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(DRAFT_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        meta = _parse_metadata(content)

        # Parse the date from > Created: YYYY-MM-DD
        created_str = ""
        for line in content.split("\n"):
            if line.startswith("> Created:"):
                created_str = line.split(":", 1)[1].strip()
                break

        if not created_str:
            continue

        try:
            created_date = datetime.strptime(created_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue

        # 180 days: archive
        if created_date < decay_180d:
            archive_dir = os.path.join(WIKI_ROOT, "archive")
            os.makedirs(archive_dir, exist_ok=True)
            shutil.move(fpath, os.path.join(archive_dir, fname))
            # Also move .npy if present
            np_path = fpath.replace(".md", ".npy")
            if os.path.exists(np_path):
                shutil.move(np_path, os.path.join(archive_dir, fname.replace(".md", ".npy")))
            _append_log("archive", meta.get("title", fname))
            archived += 1
            continue

        # 90 days: halve hit count
        if created_date < decay_90d:
            old_hit = int(meta.get("hit_count", 1))
            new_hit = max(old_hit // 2, 1)
            content = content.replace(
                f"> Hit Count: {old_hit}", f"> Hit Count: {new_hit}"
            )
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            decayed += 1

    return {"decayed": decayed, "archived": archived}
```

Add `import shutil` to the top of wiki_bridge.py.

- [ ] **Step 2: Register decay as MCP tool**

Add to `server.py` — `handle_list_tools()`:
```python
Tool(
    name="expert_brain__decay",
    description="Run knowledge decay: halve hit_count for 90-day stale insights, archive 180-day ones.",
    inputSchema={"type": "object", "properties": {}},
),
```

Add to `handle_call_tool()`:
```python
if name == "expert_brain__decay":
    from wiki_bridge import decay as wiki_decay
    result = wiki_decay()
    return [TextContent(type="text", text=str(result))]
```

- [ ] **Step 3: Verify decay runs without errors**

```bash
cd D:/cc/metacognition && python -c "
import sys; sys.path.insert(0, 'expert-brain-server')
from wiki_bridge import decay
result = decay()
print('Decay result:', result)
assert result['decayed'] >= 0 and result['archived'] >= 0
print('PASS')
"
```

Expected: `Decay result: {'decayed': 0, 'archived': 0}` — no insights old enough yet.

- [ ] **Step 4: Commit**

```bash
git add expert-brain-server/wiki_bridge.py expert-brain-server/server.py
git commit -m "feat: implement knowledge decay (90d halve, 180d archive)"
```

---

### Task A7: End-to-end Phase 2 verification

**Files:** None (verification only)

- [ ] **Step 1: Verify vector search quality**

Compare keyword vs vector search on a tricky query:

```bash
cd D:/cc/metacognition && python -c "
import sys; sys.path.insert(0, 'expert-brain-server')
from wiki_bridge import query as vec_query

# Would fail with keyword search
results = vec_query('environment setup not working', 5)
print('Vector results for \"environment setup not working\":')
for r in results[:3]:
    print(f'  [{r[\"score\"]:.4f}] {r[\"symptom\"]}')
assert len(results) >= 1
assert results[0]['score'] > 0.3
print('Vector search quality: PASS')
"
```

- [ ] **Step 2: Verify promote + decay pipeline**

```bash
cd D:/cc/metacognition && python -c "
import sys; sys.path.insert(0, 'expert-brain-server')
from wiki_bridge import promote, decay

# Promote a high-hit insight
r = promote('55eb6bff0e8c')
print('Promote:', r['status'])

# Run decay
d = decay()
print('Decay:', d)

assert r['status'] in ('promoted', 'threshold_not_met')
assert d['decayed'] >= 0
print('Pipeline: PASS')
"
```

- [ ] **Step 3: Verify MCP tools appear after restart**

Restart Claude Code. The following MCP tools should all be available:
- `mcp__expert-brain__expert_brain__draft_insight`
- `mcp__expert-brain__expert_brain__retrieve`
- `mcp__expert-brain__expert_brain__promote`
- `mcp__expert-brain__expert_brain__decay`

- [ ] **Step 4: Verify session start auto-trigger with new vector search**

After restart, Claude Code should automatically present known pitfalls with better
semantic matching.

- [ ] **Step 5: Commit final verification**

```bash
git add .cursor/insights/wiki/
git commit -m "verify: Phase 2 vector search, promote, decay all pass"
```

---

## Verification Checklist

- [ ] B1: SKILL.md in `.claude/skills/metacognition/`, old `metacognition-skill/` deleted
- [ ] B2: Session start auto-calls `expert_brain__retrieve`
- [ ] A3: `ingest()` creates `.npy` embeddings alongside `.md` files
- [ ] A4: `query()` uses cosine similarity, >0.3 scores for semantic matches
- [ ] A4: `check_duplicate()` detects semantic duplicates at >0.92 threshold
- [ ] A5: `promote()` moves hit_count>=5 insights to live/ with status change
- [ ] A6: `decay()` runs without errors (no insights old enough to trigger yet)
- [ ] A7: All 4 MCP tools registered after restart
