"""Retrieve insights from the wiki."""

from wiki_bridge import query as wiki_query


def retrieve(query: str, top_k: int = 5) -> dict:
    """Search the wiki for insights matching the query.

    Args:
        query: Search terms
        top_k: Max results to return
    """
    results = wiki_query(query, top_k)
    return {"results": results}
