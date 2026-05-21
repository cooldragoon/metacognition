"""Adapter layer for karpathy-llm-wiki file conventions.

Follows the karpathy-llm-wiki pattern:
- wiki/draft/*.md — draft insight nodes
- wiki/live/*.md  — promoted constraints
- wiki/index.md   — content directory
- wiki/log.md     — append-only timeline

All paths are derived from __file__, not os.getcwd().
"""

import hashlib
import os
import re
import shutil
from datetime import date

import numpy as np


# ---------------------------------------------------------------------------
# Path constants — derived from this file's location
# ---------------------------------------------------------------------------

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_ROOT = os.path.join(_PROJECT_ROOT, ".cursor", "insights", "wiki")
DRAFT_DIR = os.path.join(WIKI_ROOT, "draft")
LIVE_DIR = os.path.join(WIKI_ROOT, "live")
INDEX_PATH = os.path.join(WIKI_ROOT, "index.md")
LOG_PATH = os.path.join(WIKI_ROOT, "log.md")


# ---------------------------------------------------------------------------
# Embedding: model2vec (8MB, numpy-only, 500x faster than sentence-transformers)
# Falls back to keyword search when model unavailable.
# ---------------------------------------------------------------------------

_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "potion-base-8M")
_STATIC_MODEL = None
_EMBED_UNAVAILABLE = False


def _get_model():
    """Load model2vec from local path or HuggingFace. Returns None → keyword fallback."""
    global _STATIC_MODEL, _EMBED_UNAVAILABLE
    if _EMBED_UNAVAILABLE:
        return None
    if _STATIC_MODEL is not None:
        return _STATIC_MODEL
    try:
        from model2vec import StaticModel
        if os.path.isdir(_MODEL_DIR):
            _STATIC_MODEL = StaticModel.from_pretrained(_MODEL_DIR, normalize=True)
        else:
            _STATIC_MODEL = StaticModel.from_pretrained(
                "minishlab/potion-base-8M", normalize=True
            )
    except Exception:
        _EMBED_UNAVAILABLE = True
        return None
    return _STATIC_MODEL


def _embed(text: str) -> "np.ndarray | None":
    """Compute embedding. Returns None → keyword fallback."""
    model = _get_model()
    if model is None:
        return None
    return model.encode(text)


def _cosine(a: "np.ndarray", b: "np.ndarray") -> float:
    """Cosine similarity between two normalized vectors."""
    return float(np.dot(a, b))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _slug(text: str, max_len: int = 60) -> str:
    """Convert a symptom text to a kebab-case-ish filename slug."""
    slug = text.strip().lower()
    # Replace any non-alphanumeric / non-hyphen / non-underscore with hyphen
    slug = re.sub(r"[^a-z0-9\-_]", "-", slug)
    # Collapse consecutive hyphens
    slug = re.sub(r"-{2,}", "-", slug)
    # Trim to max_len without breaking a word (cut at last hyphen if possible)
    if len(slug) > max_len:
        slug = slug[:max_len]
        # Try to cut at the last hyphen so we don't split a word
        last_hyphen = slug.rfind("-")
        if last_hyphen > max_len // 2:
            slug = slug[:last_hyphen]
    # Strip leading/trailing hyphens
    slug = slug.strip("-")
    return slug


def _generate_id(symptom: str, root_cause: str) -> str:
    """Generate a stable 12-character hex insight ID."""
    payload = (symptom[:100] + root_cause[:100]).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def _create_skeleton_index() -> None:
    """Create a minimal index.md with the ## draft table header."""
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(
            "# MetaCognition Insights Index\n\n"
            "## draft\n\n"
            "| Insight | Summary | Updated |\n"
            "|---------|---------|----------|\n"
        )


def _append_log(action: str, title: str) -> None:
    """Append an entry to log.md."""
    today = date.today().isoformat()
    entry = f"\n## [{today}] {action} | {title}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def _update_index(filename: str, title: str, summary: str) -> None:
    """Insert a row into the ## draft table of index.md."""
    today = date.today().isoformat()
    # Sanitize values to prevent markdown/table injection
    title = title.replace("|", "\\|").replace("]", "\\]").replace("\n", " ")
    summary = summary.replace("|", "\\|").replace("\n", " ")
    row = f"| [{title}](draft/{filename}) | {summary} | {today} |\n"

    if not os.path.exists(INDEX_PATH):
        _create_skeleton_index()

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the draft table header row: the line after "## draft" that
    # contains the column headings.
    draft_header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("## draft"):
            # The header row is two lines after the section heading
            # (there's a blank description line in between).
            for j in range(i + 1, min(i + 6, len(lines))):
                if "| Insight | Summary | Updated |" in lines[j]:
                    draft_header_idx = j
                    break
            break

    if draft_header_idx is None:
        raise RuntimeError("Could not locate ## draft table header in index.md")

    # Insert the new row after the header row (and its separator row)
    insert_idx = draft_header_idx + 2  # skip header + separator
    lines.insert(insert_idx, row)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)


def _parse_metadata(content: str) -> dict:
    """Extract metadata from blockquote lines and the # Title heading.

    Only parses blockquotes that appear before the first ``## `` section
    heading, so that blockquote-like text in symptom/overview sections
    cannot spoof metadata fields.
    """
    meta: dict = {}

    for line in content.split("\n"):
        # Stop parsing metadata once we reach a level-2 heading
        if line.startswith("## "):
            break

        if line.startswith("# ") and "title" not in meta:
            meta["title"] = line[2:].strip()
        elif line.startswith("> "):
            m = re.match(r"^>\s*([A-Za-z ]+?):\s*(.*)$", line)
            if m:
                key = m.group(1).strip().lower().replace(" ", "_")
                value = m.group(2).strip()
                meta[key] = value

    # Hit Count may be bare integer; try to coerce
    if "hit_count" in meta:
        try:
            meta["hit_count"] = int(meta["hit_count"])
        except ValueError:
            meta["hit_count"] = 0
    else:
        meta["hit_count"] = 0

    return meta


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ingest(
    symptom: str,
    root_cause: str,
    resolution: str,
    severity: str,
    insight_id: str,
) -> str:
    """Create a new draft insight .md node.

    Returns the absolute file path to the created draft file.
    """
    os.makedirs(DRAFT_DIR, exist_ok=True)

    today = date.today().isoformat()
    slug = _slug(symptom)
    filename = f"{slug}.md"
    filepath = os.path.join(DRAFT_DIR, filename)

    # Build a brief overview by combining symptom and resolution.
    overview = f"{symptom.strip()}. Root cause: {root_cause.strip()}. Resolution: {resolution.strip()}"

    content = f"""# {symptom.strip()}

> Sources: User observation, {today}
> Created: {today}
> Severity: {severity}
> Status: draft
> Hit Count: 0
> ID: {insight_id}

## Overview
{overview}

## Symptom
{symptom.strip()}

## Root Cause
{root_cause.strip()}

## Resolution
{resolution.strip()}

## Notes

## See Also
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Store vector embedding as companion .npy file (if model available)
    embedding = _embed(f"{symptom}\n{root_cause}\n{resolution}")
    if embedding is not None:
        np_path = filepath.replace(".md", ".npy")
        np.save(np_path, embedding)

    # Append to log and update the index.
    _append_log("ingest", symptom.strip()[:80])
    _update_index(filename, symptom.strip(), overview[:80])

    return filepath


def check_duplicate(symptom: str, root_cause: str) -> str | None:
    """Check if a similar insight exists. Uses vector similarity if model available,
    falls back to keyword overlap otherwise."""
    if not os.path.isdir(DRAFT_DIR):
        return None

    query_embedding = _embed(f"{symptom}\n{root_cause}")

    if query_embedding is not None:
        # Vector path
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
    else:
        # Keyword fallback
        return _check_duplicate_keyword(symptom, root_cause)


def query(search: str, top_k: int = 5) -> list[dict]:
    """Search draft insights. Uses vector similarity if model available, falls back to keyword."""
    if not os.path.isdir(DRAFT_DIR):
        return []

    query_embedding = _embed(search)

    if query_embedding is not None:
        # Vector path
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
                meta["symptom"] = meta.get("title", "")
                meta["insight_id"] = meta.get("id", "")
                meta["resolution"] = _extract_section(content, "Resolution")
                results.append(meta)
        results.sort(key=lambda r: r["score"], reverse=True)
        results = [r for r in results if r["score"] > 0]
    else:
        # Keyword fallback
        results = _query_keyword(search)

    # Bump hit count on returned results
    for r in results[:top_k]:
        fpath = os.path.join(DRAFT_DIR, os.path.basename(r["wiki_path"]))
        _bump_hit_count(fpath)
    return results[:top_k]


def _query_keyword(search: str) -> list[dict]:
    """Keyword-based search (Jaccard overlap), used as fallback when vector model unavailable."""
    results = []
    query_words = _tokenize(search)
    if not query_words:
        return results
    for fname in os.listdir(DRAFT_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(DRAFT_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        file_words = _tokenize(content)
        if not file_words:
            continue
        score = len(query_words & file_words) / len(query_words | file_words)
        if score > 0:
            meta = _parse_metadata(content)
            meta["score"] = round(score, 4)
            meta["wiki_path"] = f"draft/{fname}"
            meta["symptom"] = meta.get("title", "")
            meta["insight_id"] = meta.get("id", "")
            meta["resolution"] = _extract_section(content, "Resolution")
            results.append(meta)
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def _check_duplicate_keyword(symptom: str, root_cause: str) -> str | None:
    """Keyword-based duplicate check (fallback when vector model unavailable)."""
    query_words = _tokenize(symptom + " " + root_cause)
    if not query_words:
        return None
    best_score = 0.0
    best_id = None
    for fname in os.listdir(DRAFT_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(DRAFT_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        file_words = _tokenize(content)
        if not file_words:
            continue
        overlap = len(query_words & file_words) / len(query_words)
        if overlap > best_score:
            best_score = overlap
            meta = _parse_metadata(content)
            best_id = meta.get("id", None)
    if best_score > 0.6 and best_id:
        return best_id
    return None


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase words >= 3 characters."""
    return {w.lower() for w in re.findall(r"[a-zA-Z0-9]{3,}", text)}


def promote(insight_id: str) -> dict:
    """Promote a draft insight to live constraint. Returns promotion result."""
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

    os.makedirs(LIVE_DIR, exist_ok=True)
    live_fname = os.path.basename(draft_path)
    live_path = os.path.join(LIVE_DIR, live_fname)

    live_content = draft_content.replace("> Status: draft", "> Status: live")
    with open(live_path, "w", encoding="utf-8") as f:
        f.write(live_content)

    updated_content = draft_content.replace("> Status: draft", "> Status: promoted")
    updated_content += "\n> Promoted to: live\n"
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    title = _parse_metadata(draft_content).get("title", insight_id)
    _append_log("promote", title)
    _update_index(live_fname, title, "promoted")

    return {"promoted_id": insight_id, "status": "promoted", "live_path": live_path}


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


def _extract_section(content: str, heading: str) -> str:
    """Extract the body text under a level-2 heading like '## Resolution'."""
    pattern = rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def _bump_hit_count(filepath: str) -> None:
    """Increment the Hit Count metadata field in a draft file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    def _inc(m: re.Match) -> str:
        try:
            new_count = int(m.group(1)) + 1
        except ValueError:
            new_count = 1
        return f"> Hit Count: {new_count}"

    new_content = re.sub(r"^> Hit Count:\s*(\d+)", _inc, content, flags=re.MULTILINE)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
