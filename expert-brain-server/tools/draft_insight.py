"""Record a draft insight from a resolved bug or lesson learned."""

from wiki_bridge import ingest, check_duplicate, _generate_id


def draft_insight(
    symptom: str,
    root_cause: str,
    resolution: str,
    severity: str = "medium",
) -> dict:
    """Record a draft insight. Deduplicates before writing.

    Args:
        symptom: What went wrong (1 sentence)
        root_cause: Technical explanation (1-2 sentences)
        resolution: Verified fix or workaround (1 sentence)
        severity: low, medium, high, or critical
    """
    insight_id = _generate_id(symptom, root_cause)

    existing_id = check_duplicate(symptom, root_cause)
    if existing_id:
        return {
            "insight_id": existing_id,
            "status": "duplicate",
            "hit_count": -1,
        }

    filepath = ingest(symptom, root_cause, resolution, severity, insight_id)

    return {
        "insight_id": insight_id,
        "status": "new",
        "hit_count": 1,
    }
