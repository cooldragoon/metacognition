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
