"""
Step 3: Assemble the full pipeline.
Runs the searches, extracts structured records for each result, filters out
low-relevance noise, and returns a sorted digest (most relevant first).

Also saves the digest to a timestamped JSON file so you have a record of
each run — useful for showing "this is a tool that produces real output"
in an interview or resume conversation.

Run standalone:
    python -m src.digest
"""

import json
from datetime import datetime
from pathlib import Path

from src.search import run_all_searches, get_client as get_tavily_client
from src.extract import extract_one, get_client as get_openai_client
from src.config import EXTRACTION_MODEL

MIN_RELEVANCE_SCORE = 3  # drop anything scored below this
OUTPUT_DIR = Path("digests")


def build_digest() -> list[dict]:
    print("Searching...")
    raw_results = run_all_searches()
    print(f"  -> {len(raw_results)} unique raw results")

    print("Extracting structured records...")
    openai_client = get_openai_client()
    structured = []
    for i, raw in enumerate(raw_results, 1):
        try:
            record = extract_one(openai_client, raw)
            structured.append(record)
        except Exception as e:
            print(f"  ! Skipped one result due to error: {e}")
        print(f"  -> {i}/{len(raw_results)} processed")

    # filter + sort
    filtered = [r for r in structured if r.get("relevance_score", 0) >= MIN_RELEVANCE_SCORE]
    filtered.sort(key=lambda r: r.get("relevance_score", 0), reverse=True)

    print(f"Kept {len(filtered)} of {len(structured)} after relevance filter (score >= {MIN_RELEVANCE_SCORE})")
    return filtered


def save_digest(digest: list[dict]) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = OUTPUT_DIR / f"digest_{timestamp}.json"
    with open(path, "w") as f:
        json.dump(digest, f, indent=2)
    return path


if __name__ == "__main__":
    digest = build_digest()
    path = save_digest(digest)
    print(f"\nSaved digest to {path}")

    print("\n" + "=" * 60)
    print("DIGEST PREVIEW")
    print("=" * 60)
    for item in digest:
        print(f"\n[{item.get('relevance_score')}/5] {item.get('headline')}")
        print(f"  Companies : {', '.join(item.get('companies_involved', []))}")
        print(f"  Type      : {item.get('event_type')}")
        print(f"  BD note   : {item.get('bd_relevance')}")
        print(f"  Source    : {item.get('source_url')}")
