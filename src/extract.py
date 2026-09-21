"""
Step 2: Extraction / structuring layer.
Takes one raw search result (title, url, snippet) and asks an LLM to turn it
into a structured record: what happened, who's involved, why a BD analyst
at an energy company would care, and a confidence flag for relevance.

Run standalone to test on a couple of hand-written examples (no API cost
for search, just one OpenAI call each):
    python -m src.extract
"""

import json
from openai import OpenAI

from src.config import OPENAI_API_KEY, EXTRACTION_MODEL

EXTRACTION_SYSTEM_PROMPT = """You are a research analyst supporting a business development \
team at a U.S. power/energy company (natural gas, battery storage, renewables). \
You will be given the title, URL, and a text snippet of a news article. \
Extract a structured summary useful for BD market monitoring.

Return ONLY valid JSON with these fields:
{
  "headline": "short restatement of what happened, one sentence",
  "companies_involved": ["list", "of", "company names"],
  "event_type": "one of: project_announcement, acquisition, partnership, regulatory, financing, market_data, other",
  "bd_relevance": "1-2 sentences on why a BD analyst at an energy company should care",
  "relevance_score": 1-5 integer, 5 = highly relevant to Texas power market / BESS / gas BD strategy, 1 = not relevant,
  "region": "e.g. ERCOT/Texas, US, other"
}

If the snippet doesn't contain enough information to fill a field, use your best \
judgement from the title/URL, and use "unknown" rather than omitting the field. \
If the article is clearly irrelevant to energy/power markets, still return the JSON \
with relevance_score 1.
"""


def get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set. Copy .env.example to .env and fill it in.")
    return OpenAI(api_key=OPENAI_API_KEY)


def extract_one(client: OpenAI, raw_result: dict) -> dict:
    """Send one raw search result to the LLM, get back a structured dict."""
    user_content = (
        f"Title: {raw_result.get('title', '')}\n"
        f"URL: {raw_result.get('url', '')}\n"
        f"Published: {raw_result.get('published_date', 'unknown')}\n"
        f"Snippet: {raw_result.get('content', '')[:1500]}"
    )

    response = client.chat.completions.create(
        model=EXTRACTION_MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    structured = json.loads(response.choices[0].message.content)
    # carry through the source info so the digest can link back to it
    structured["source_title"] = raw_result.get("title", "")
    structured["source_url"] = raw_result.get("url", "")
    structured["source_topic"] = raw_result.get("topic", "")
    return structured


if __name__ == "__main__":
    client = get_client()

    # Two hand-written test cases so you can validate the extraction step
    # without needing Tavily results yet.
    test_results = [
        {
            "title": "Developer announces 200 MWh battery storage project in ERCOT West zone",
            "url": "https://example.com/bess-announcement",
            "published_date": "2026-09-15",
            "content": (
                "A Houston-based independent power producer announced Monday it has reached "
                "financial close on a 100 MW / 200 MWh battery energy storage project in the "
                "ERCOT West load zone, with commercial operation targeted for late 2027. "
                "The project will participate in ERCOT's merchant energy and ancillary services markets."
            ),
            "topic": "battery energy storage system (BESS) project announcement Texas ERCOT",
        },
        {
            "title": "Local bakery wins county fair pie contest",
            "url": "https://example.com/pie-contest",
            "published_date": "2026-09-10",
            "content": "A small bakery in central Texas won first place for its peach pie at the county fair.",
            "topic": "battery energy storage system (BESS) project announcement Texas ERCOT",
        },
    ]

    for r in test_results:
        print("=" * 60)
        print("INPUT:", r["title"])
        result = extract_one(client, r)
        print(json.dumps(result, indent=2))
