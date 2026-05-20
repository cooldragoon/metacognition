"""Retrieve insights from the wiki."""

from wiki_bridge import query


def retrieve(query_text: str, top_k: int = 5) -> dict:
    """Search the wiki for insights matching the query.

    Args:
        query_text: Search terms
        top_k: Max results to return
    """
    results = query(query_text, top_k)
    return {"results": results}
