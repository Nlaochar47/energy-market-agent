# Energy Market Intelligence Agent

Automated monitoring tool for BD-relevant developments in Texas power markets:
BESS projects, ERCOT regulatory activity, natural gas investment, and competitor
partnerships/acquisitions.

## How it works
1. **Search** (`src/search.py`) — queries Tavily for recent articles across a set
   of watched topics (see `src/config.py`).
2. **Extract** (`src/extract.py`) — sends each article to OpenAI, which returns
   a structured JSON record: headline, companies involved, event type, why it
   matters for BD, and a 1-5 relevance score.
3. **Digest** (`src/digest.py`) — runs steps 1-2 across all topics, filters out
   low-relevance noise, sorts by score, and saves a timestamped JSON file.
4. **UI** (`app.py`) — a Streamlit page with a button to run the digest and
   view results as cards with source links.

## Setup (run these yourself, in order)

### 1. Get your API keys ready
- OpenAI: https://platform.openai.com/api-keys
- Tavily: https://app.tavily.com (free tier available)

### 2. Create a virtual environment and install dependencies
```bash
cd energy-market-agent
python3 -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add your API keys
```bash
cp .env.example .env
```
Open `.env` and paste in your real keys:
```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

### 4. Test the search layer alone
```bash
python -m src.search
```
You should see ~5-25 unique articles printed with title/url/snippet.
If this errors, double check `TAVILY_API_KEY` in `.env`.

### 5. Test the extraction layer alone
```bash
python -m src.extract
```
This runs 2 hand-written test articles (one relevant BESS story, one
irrelevant bakery story) through the LLM and prints the structured JSON.
Confirm the bakery story gets a low `relevance_score` and the BESS story
gets a high one — that tells you the filter logic will work.

### 6. Run the full pipeline end-to-end (search + extract + filter)
```bash
python -m src.digest
```
This will take 30-90 seconds depending on how many articles come back.
It prints a preview and saves a JSON file to `digests/`.

### 7. Launch the UI
```bash
streamlit run app.py
```
This opens a browser tab. Click "Run digest now" in the sidebar.

## Tuning
- Edit `WATCH_TOPICS` in `src/config.py` to add/remove topics (e.g. add
  "Banpu Power" or "BKV Corporation" by name once you want to track them
  specifically as competitors/partners).
- Adjust `MIN_RELEVANCE_SCORE` in `src/digest.py` if you're getting too much
  or too little noise.
- `RESULTS_PER_TOPIC` and `MAX_RESULT_AGE_DAYS` in `config.py` control how
  wide/recent the search casts.

## Cost note
Each digest run makes 1 Tavily search per topic (5 topics = 5 searches) and
1 OpenAI call per article found (~5-25 calls using `gpt-4o-mini`, which is
cheap — a full run should cost well under $0.05).
