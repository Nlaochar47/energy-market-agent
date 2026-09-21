"""
Step 1: Sourcing layer.
Queries Tavily for recent articles on each watched topic and returns
a flat list of raw result dicts (title, url, content snippet, published date).

Run standalone to test:
    python -m src.search
"""

from datetime import datetime, timedelta
from tavily import TavilyClient

from src.config import TAVILY_API_KEY, WATCH_TOPICS, MAX_RESULT_AGE_DAYS, RESULTS_PER_TOPIC


def get_client() -> TavilyClient:
    if not TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY is not set. Copy .env.example to .env and fill it in.")
    return TavilyClient(api_key=TAVILY_API_KEY)


def search_topic(client: TavilyClient, topic: str) -> list[dict]:
    """Run one Tavily search for a topic, return raw hits."""
    response = client.search(
        query=topic,
        search_depth="advanced",
        max_results=RESULTS_PER_TOPIC,
        days=MAX_RESULT_AGE_DAYS,  # Tavily's own recency filter
        include_answer=False,
    )
    hits = response.get("results", [])
    # tag each hit with which topic query produced it, useful for debugging/filtering
    for hit in hits:
        hit["topic"] = topic
    return hits


def run_all_searches() -> list[dict]:
    """Search every topic in WATCH_TOPICS, return combined + de-duplicated raw results."""
    client = get_client()
    all_hits: list[dict] = []
    seen_urls: set[str] = set()

    for topic in WATCH_TOPICS:
        hits = search_topic(client, topic)
        for hit in hits:
            url = hit.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_hits.append(hit)

    return all_hits


if __name__ == "__main__":
    results = run_all_searches()
    print(f"Fetched {len(results)} unique raw results across {len(WATCH_TOPICS)} topics.\n")
    for r in results[:5]:
        print("-" * 60)
        print("Topic   :", r.get("topic"))
        print("Title   :", r.get("title"))
        print("URL     :", r.get("url"))
        print("Snippet :", (r.get("content") or "")[:200], "...")
