"""Evaluate search quality: keyword baseline vs vector (when model available).

Usage:
    python eval_search.py          # runs both if model available, keyword-only otherwise
    python eval_search.py --json   # machine-readable output

Test queries are designed to verify:
    Q1: Exact keyword match (easy — both should pass)
    Q2: Synonym/semantic match (hard — vector should win)
    Q3: Cross-language rewording (hard — vector should win)
    Q4: Ambiguous short query (hard — both may struggle)
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wiki_bridge import _query_keyword
from wiki_bridge import query as query_vector

# ── Test queries mapped to expected insight IDs ──────────────────────────
# Only test against insights that actually exist in the current wiki
TEST_CASES = [
    # (query, expected_insight_id, description)
    (
        "conda activate fails terminal",
        "55eb6bff0e8c",
        "Q1: Direct keyword match — conda terminal issue",
    ),
    (
        "python environment setup not working in editor",
        "55eb6bff0e8c",
        "Q2: Semantic — different words, same conda/terminal problem",
    ),
    (
        "MCP tools disappeared after I changed the config",
        "15078b21adc7",
        "Q3: Rewording — MCP config format issue",
    ),
    (
        "服务器启动失败",
        None,
        "Q4: Chinese query — cross-language (bonus, expected to miss)",
    ),
]


def evaluate(engine_name, search_fn, test_cases):
    """Run evaluation for a search function. Returns metrics dict."""
    results = []
    total_time = 0

    for query, expected_id, desc in test_cases:
        start = time.perf_counter()
        hits = search_fn(query)
        if isinstance(hits, dict):
            hits = hits.get("results", hits)
        hits = hits[:5]
        elapsed = time.perf_counter() - start
        total_time += elapsed

        # Check if expected insight is in results
        found_at = None
        for rank, r in enumerate(hits, 1):
            if r.get("insight_id") == expected_id:
                found_at = rank
                break

        results.append({
            "query": query,
            "desc": desc,
            "expected_id": expected_id,
            "found": found_at is not None,
            "rank": found_at,
            "top_score": hits[0]["score"] if hits else 0,
            "num_results": len(hits),
            "elapsed_ms": round(elapsed * 1000, 1),
        })

    # Aggregate metrics
    testable = [r for r in results if r["expected_id"] is not None]
    recall = sum(1 for r in testable if r["found"]) / len(testable) if testable else 0
    mrr = sum(1.0 / r["rank"] for r in testable if r["found"]) / len(testable) if testable else 0

    return {
        "engine": engine_name,
        "recall@5": round(recall, 3),
        "MRR": round(mrr, 3),
        "total_queries": len(results),
        "total_ms": round(total_time * 1000, 1),
        "per_query": results,
    }


def main():
    as_json = "--json" in sys.argv

    if not as_json:
        print("=" * 60)
        print("MetaCognition Search Evaluation")
        print("=" * 60)

    # ── Keyword baseline ──────────────────────────────────────────────
    kw_metrics = evaluate("keyword (Jaccard)", lambda q: _query_keyword(q), TEST_CASES)

    # ── Vector (if available) ─────────────────────────────────────────
    vec_metrics = None
    try:
        # Force a fresh model attempt (resets _EMBED_UNAVAILABLE flag)
        import wiki_bridge
        wiki_bridge._EMBED_UNAVAILABLE = False
        wiki_bridge._STATIC_MODEL = None

        test_emb = wiki_bridge._embed("test")
        if test_emb is not None:
            vec_metrics = evaluate("vector (model2vec)", lambda q: query_vector(q, top_k=5), TEST_CASES)
            vec_available = True
        else:
            vec_available = False
    except Exception:
        vec_available = False

    # ── Output ────────────────────────────────────────────────────────
    if as_json:
        output = {
            "keyword": kw_metrics,
            "vector": vec_metrics,
            "vector_available": vec_available,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        _print_report(kw_metrics, vec_metrics, vec_available)


def _print_report(kw, vec, vec_available):
    print(f"\nKeyword (Jaccard):  Recall@5={kw['recall@5']:.0%}  MRR={kw['MRR']:.3f}  {kw['total_ms']:.0f}ms")
    for r in kw["per_query"]:
        status = f"[PASS rank={r['rank']}]" if r["found"] else "[MISS]"
        print(f"  {status:<18} score={r['top_score']:.4f}  {r['desc']}")

    if vec_available and vec:
        print(f"\nVector (model2vec):  Recall@5={vec['recall@5']:.0%}  MRR={vec['MRR']:.3f}  {vec['total_ms']:.0f}ms")
        for r in vec["per_query"]:
            status = f"[PASS rank={r['rank']}]" if r["found"] else "[MISS]"
            print(f"  {status:<18} score={r['top_score']:.4f}  {r['desc']}")
    else:
        print(f"\nVector (model2vec):  Model not available — download with:")
        print(f"  huggingface-cli download minishlab/potion-base-8M --local-dir expert-brain-server/models/potion-base-8M")

    print()


if __name__ == "__main__":
    main()
