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
from datetime import date


# ---------------------------------------------------------------------------
# Path constants — derived from this file's location
# ---------------------------------------------------------------------------

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_ROOT = os.path.join(_PROJECT_ROOT, ".cursor", "insights", "wiki")
DRAFT_DIR = os.path.join(WIKI_ROOT, "draft")
INDEX_PATH = os.path.join(WIKI_ROOT, "index.md")
LOG_PATH = os.path.join(WIKI_ROOT, "log.md")


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


def _append_log(action: str, title: str) -> None:
    """Append an entry to log.md."""
    today = date.today().isoformat()
    entry = f"\n## [{today}] {action} | {title}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def _update_index(filename: str, title: str, summary: str) -> None:
    """Insert a row into the ## draft table of index.md."""
    today = date.today().isoformat()
    row = f"| [{title}](draft/{filename}) | {summary} | {today} |\n"

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
    """Extract metadata from blockquote lines and the # Title heading."""
    meta: dict = {}

    # Title from the first level-1 heading
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        meta["title"] = title_match.group(1).strip()

    # Blockquote metadata lines:  > Key: Value
    for match in re.finditer(r"^>\s*([A-Za-z ]+?):\s*(.*)$", content, re.MULTILINE):
        key = match.group(1).strip().lower().replace(" ", "_")
        value = match.group(2).strip()
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


def _words(text: str) -> set[str]:
    """Return set of lowercase words > 3 characters from *text*."""
    tokens = re.findall(r"[a-zA-Z0-9]{4,}", text.lower())
    return set(tokens)


def _draft_files() -> list[str]:
    """Return absolute paths to every .md file in DRAFT_DIR."""
    try:
        entries = os.listdir(DRAFT_DIR)
    except FileNotFoundError:
        return []
    return [
        os.path.join(DRAFT_DIR, e)
        for e in entries
        if e.endswith(".md") and os.path.isfile(os.path.join(DRAFT_DIR, e))
    ]


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

    # Append to log and update the index.
    _append_log("ingest", symptom.strip()[:80])
    _update_index(filename, symptom.strip(), overview[:80])

    return filepath


def check_duplicate(symptom: str, root_cause: str) -> str | None:
    """Check if a similar insight already exists in draft/.

    Uses keyword overlap (words > 3 chars).  If more than 60 % of the
    query words are found in an existing draft file the insight is
    considered a duplicate and its ``insight_id`` is returned.
    """
    query_words = _words(symptom + " " + root_cause)
    if not query_words:
        return None

    for filepath in _draft_files():
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        file_words = _words(content)
        if not file_words:
            continue

        overlap = len(query_words & file_words) / len(query_words)
        if overlap > 0.6:
            # Extract the > ID: {id} line
            id_match = re.search(r"^>\s*ID:\s*(\S+)", content, re.MULTILINE)
            if id_match:
                return id_match.group(1)

    return None


def query(search: str, top_k: int = 5) -> list[dict]:
    """Search draft/*.md by keyword overlap.

    Returns a list of result dicts sorted by score (descending):
        [{insight_id, symptom, resolution, severity, hit_count, score, wiki_path}, …]
    """
    query_words = _words(search)
    results: list[dict] = []

    for filepath in _draft_files():
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        file_words = _words(content)

        if not query_words or not file_words:
            score = 0.0
        else:
            # Jaccard similarity
            score = len(query_words & file_words) / len(query_words | file_words)

        meta = _parse_metadata(content)

        # Increment hit count when a file is returned in results.
        # (We'll bump it after ranking so we only bump top_k results.)
        results.append(
            {
                "insight_id": meta.get("id", ""),
                "symptom": meta.get("title", ""),
                "resolution": _extract_section(content, "Resolution"),
                "severity": meta.get("severity", "low"),
                "hit_count": meta.get("hit_count", 0),
                "score": score,
                "wiki_path": filepath,
            }
        )

    # Sort descending by score
    results.sort(key=lambda r: r["score"], reverse=True)

    # Bump hit count on the top_k results
    for r in results[:top_k]:
        _bump_hit_count(r["wiki_path"])

    return results[:top_k]


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
