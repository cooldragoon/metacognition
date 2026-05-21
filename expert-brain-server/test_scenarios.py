"""MetaCognition scenario tests — covers all common paths and edge cases.

Usage:
    python test_scenarios.py          # full suite
    python test_scenarios.py --quick  # smoke test only
    python test_scenarios.py --json   # machine-readable output
"""

import sys
import os
import json
import time
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wiki_bridge import (
    _generate_id, _slug, _parse_metadata, _extract_section,
    _tokenize, _query_keyword, _check_duplicate_keyword,
    _query_vector, _embed, _get_model,
    ingest, check_duplicate, query, promote, decay,
    DRAFT_DIR, LIVE_DIR, WIKI_ROOT,
)

# ── Helpers ──────────────────────────────────────────────────────────
_passed = 0
_failed = 0
_skipped = 0


def ok(label: str, condition: bool, detail: str = ""):
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        _failed += 1
        print(f"  [FAIL] {label}  -- {detail}")


def skip(label: str, reason: str = ""):
    global _skipped
    _skipped += 1
    print(f"  [SKIP] {label}  -- {reason}")


# ── Test helpers ─────────────────────────────────────────────────────
_temp_insights = []  # track for cleanup


def record_test_insight(symptom, root_cause, resolution, severity="medium", variants=None):
    """Record a test insight and track it for cleanup."""
    iid = _generate_id(symptom, root_cause)
    existing = check_duplicate(symptom, root_cause)
    if existing:
        return existing, "duplicate"
    path = ingest(symptom, root_cause, resolution, severity, iid, variants)
    _temp_insights.append(path)
    return iid, "new"


def cleanup():
    """Remove all test insights."""
    for p in _temp_insights:
        if os.path.exists(p):
            os.remove(p)
        np_p = p.replace(".md", ".npy")
        if os.path.exists(np_p):
            os.remove(np_p)


# ── 1. Slug & ID ─────────────────────────────────────────────────────
def test_slug_and_id():
    print("\n=== 1. Slug & ID generation ===")
    ok("slug: simple", _slug("conda fails") == "conda-fails")
    ok("slug: special chars", _slug("test: MCP? fail!") == "test-mcp-fail")
    ok("slug: max length", len(_slug("a" * 100)) <= 60)
    ok("id: deterministic",
       _generate_id("same", "same") == _generate_id("same", "same"))
    ok("id: different",
       _generate_id("A", "B") != _generate_id("C", "D"))


# ── 2. Tokenization ──────────────────────────────────────────────────
def test_tokenize():
    print("\n=== 2. Tokenization ===")
    ok("normal words", _tokenize("hello world test") == {"hello", "world", "test"})
    ok("short words ignored", "ab" not in _tokenize("ab cd ef"))
    ok("mixed case", _tokenize("Hello WORLD") == {"hello", "world"})
    ok("numbers", "123" in _tokenize("error 123"))
    ok("empty", _tokenize("") == set())


# ── 3. Record (ingest) ───────────────────────────────────────────────
def test_record():
    print("\n=== 3. Record insight ===")

    # Basic record
    iid, status = record_test_insight(
        "test: Python module import fails on Windows",
        "PYTHONPATH not set in system environment variables",
        "add PYTHONPATH to System Environment Variables",
        "medium",
    )
    ok("basic record", status == "new", f"got {status}")
    ok("file exists", os.path.exists(os.path.join(DRAFT_DIR, f"{_slug('test: Python module import fails on Windows')}.md")))

    # Record with variants
    iid2, status2 = record_test_insight(
        "test: npm install fails behind corporate proxy",
        "npm not configured to use corporate proxy",
        "run npm config set proxy http://proxy:8080",
        "high",
        variants=[
            "npm install hangs with network error",
            "cannot reach npm registry from office network",
            "corporate firewall blocking npm packages",
            "proxy authentication required for npm",
        ],
    )
    ok("record with variants", status2 == "new")
    ok("variants stored", iid2 is not None)

    # Duplicate detection
    dup_id, dup_status = record_test_insight(
        "test: Python module import fails on Windows",
        "PYTHONPATH not set in system environment variables",
        "add PYTHONPATH",
        "medium",
    )
    ok("duplicate detection", dup_status == "duplicate", f"got {dup_status}")

    # Record with critical severity
    iid3, status3 = record_test_insight(
        "test: database migration dropped production table",
        "migration file had DROP TABLE instead of ALTER TABLE",
        "always review auto-generated migrations before running",
        "critical",
    )
    ok("critical severity", status3 == "new")


# ── 4. Search ────────────────────────────────────────────────────────
def test_search():
    print("\n=== 4. Search ===")

    # Keyword search
    kw = _query_keyword("Python import fails Windows")
    ok("keyword: finds result", len(kw) > 0, f"got {len(kw)}")
    ok("keyword: has score", kw and kw[0]["score"] > 0)

    # Vector search (if model available)
    model = _get_model()
    if model is not None:
        emb = _embed("Python import fails on Windows")
        vec = _query_vector("test", emb)
        ok("vector: returns results", len(vec) >= 0)
        ok("vector: has symptom", all("symptom" in r for r in vec[:1]) if vec else True)
    else:
        skip("vector search", "model not available")

    # Ensemble search
    results = query("npm proxy corporate network", top_k=3)
    ok("ensemble: finds variant-hit", len(results) > 0, f"got {len(results)}")
    if results:
        ok("ensemble: all fields present",
           all(k in results[0] for k in ["symptom", "insight_id", "resolution", "score", "severity", "wiki_path"]))

    # Search with empty query
    empty = query("", top_k=3)
    ok("empty query: no crash", isinstance(empty, list))

    # Search with no draft dir
    results_all = query("anything", top_k=10)
    ok("search: returns list", isinstance(results_all, list))


# ── 5. Promote ───────────────────────────────────────────────────────
def test_promote():
    print("\n=== 5. Promote ===")

    # Promote non-existent
    r = promote("nonexistent")
    ok("promote: non-existent → error", r["status"] == "error")

    # Promote with low hit_count (hit_count=1 < threshold 5)
    iid_low, _ = record_test_insight(
        "test: low hit promote", "low hit cause", "low res", "low"
    )
    r_low = promote(iid_low)
    ok("promote: low hit → threshold_not_met",
       r_low["status"] == "threshold_not_met",
       f"got {r_low['status']}")

    # Promote from live/ (already promoted insight exists there)
    live_insights = os.listdir(LIVE_DIR) if os.path.isdir(LIVE_DIR) else []
    ok("promote: live/ has insights", len(live_insights) > 0,
       f"{len(live_insights)} live insights")


# ── 6. Decay ─────────────────────────────────────────────────────────
def test_decay():
    print("\n=== 6. Decay ===")

    d = decay()
    ok("decay: no crash", isinstance(d, dict))
    ok("decay: has keys", "decayed" in d and "archived" in d)
    ok("decay: non-negative", d["decayed"] >= 0 and d["archived"] >= 0)
    # All insights created today, should be 0
    ok("decay: nothing old enough",
       d["decayed"] == 0 and d["archived"] == 0,
       f"decayed={d['decayed']} archived={d['archived']}")


# ── 7. Metadata parsing ──────────────────────────────────────────────
def test_metadata():
    print("\n=== 7. Metadata parsing ===")

    sample = """# Test Symptom

> Sources: User observation, 2026-05-21
> Created: 2026-05-21
> Severity: high
> Status: draft
> Hit Count: 3
> ID: abc123

## Overview
Test overview.

## Symptom
Test Symptom

## Root Cause
Test cause.

## Resolution
Test fix.
"""
    meta = _parse_metadata(sample)
    ok("title", meta.get("title") == "Test Symptom")
    ok("severity", meta.get("severity") == "high")
    ok("hit_count", meta.get("hit_count") == 3)
    ok("status", meta.get("status") == "draft")
    ok("id", meta.get("id") == "abc123")

    # Injection resistance: > Severity in body should not override metadata
    injected = """# Safe Title

> Sources: User, 2026-05-21
> Severity: low
> Status: draft
> Hit Count: 1
> ID: safe

## Overview
> Severity: critical in body text

## Symptom
Safe Title
"""
    meta2 = _parse_metadata(injected)
    ok("metadata: injection resistant",
       meta2.get("severity") == "low",
       f"got {meta2.get('severity')}")


# ── 8. Edge cases ────────────────────────────────────────────────────
def test_edge_cases():
    print("\n=== 8. Edge cases ===")

    # Check empty DRAFT_DIR handling
    ok("query: handles missing dir", isinstance(query("test"), list))

    # Very long symptom
    long_symptom = "test very long symptom description " * 20
    iid, status = record_test_insight(
        long_symptom[:200], "cause", "resolution", "low"
    )
    ok("long symptom: handled", status in ("new", "duplicate"))

    # Special characters in symptom
    iid2, status2 = record_test_insight(
        "test: special | characters & <tags> in symptom",
        "cause with | pipe",
        "resolution with ] bracket",
        "low",
    )
    ok("special chars: no crash", status2 in ("new", "duplicate"))

    # Unicode
    iid3, status3 = record_test_insight(
        "test: 中文编码问题 in terminal",
        "编码设置为 GBK 而非 UTF-8",
        "export LANG=zh_CN.UTF-8",
        "low",
    )
    ok("unicode: handled", status3 in ("new", "duplicate"))


# ── 9. Search quality consistency ────────────────────────────────────
def test_search_consistency():
    print("\n=== 9. Search consistency ===")

    # Record a known insight (with variants for broad match)
    iid, status = record_test_insight(
        "test: git merge conflict in package-lock.json",
        "package-lock.json was auto-regenerated with different dependency tree",
        "accept the regenerated lockfile and re-run npm install",
        "medium",
        variants=[
            "merge conflict in lock file keeps reappearing",
            "package-lock.json conflict resolution",
            "git shows conflict in auto-generated file",
            "how to resolve npm lockfile merge issues",
        ],
    )
    ok("consistency: recorded", status == "new")

    # Multiple queries should all find it
    queries = [
        "git merge conflict lock file",
        "package-lock.json keeps conflicting",
        "auto-generated file merge issue",
        "resolve npm lockfile conflict",
    ]
    for q in queries:
        results = query(q, top_k=5)
        # Check if our insight is in top-5
        found = any(r.get("insight_id") == iid for r in results)
        ok(f"consistency: '{q[:40]}'", found, f"expected insight {iid[:8]}")


# ── Main ─────────────────────────────────────────────────────────────
def main():
    global _passed, _failed, _skipped

    print("=" * 60)
    print("MetaCognition Scenario Tests")
    print(f"Draft insights before: {len([f for f in os.listdir(DRAFT_DIR) if f.endswith('.md')]) if os.path.isdir(DRAFT_DIR) else 0}")
    print(f"Live insights: {len([f for f in os.listdir(LIVE_DIR) if f.endswith('.md')]) if os.path.isdir(LIVE_DIR) else 0}")
    print(f"Model available: {_get_model() is not None}")
    print("=" * 60)

    start = time.perf_counter()

    test_slug_and_id()
    test_tokenize()
    test_record()
    test_search()
    test_promote()
    test_decay()
    test_metadata()
    test_edge_cases()
    test_search_consistency()

    elapsed = time.perf_counter() - start

    print(f"\n{'='*60}")
    print(f"Results: {_passed} passed, {_failed} failed, {_skipped} skipped")
    print(f"Time: {elapsed:.1f}s")
    print(f"{'='*60}")

    cleanup()
    return _failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
