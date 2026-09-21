"""
Step 4: Streamlit front end.
A button-triggered UI that runs the digest pipeline and displays results
as readable cards, with sources linked. This is the demoable piece.

Run:
    streamlit run app.py
"""

import streamlit as st
from src.digest import build_digest, save_digest
from src.config import WATCH_TOPICS

st.set_page_config(page_title="Energy Market Intel Agent", page_icon="⚡", layout="wide")

st.title("⚡ Energy Market Intelligence Agent")
st.caption(
    "Automated monitoring for BD-relevant developments in Texas power markets, "
    "BESS, natural gas, and ERCOT regulatory activity."
)

with st.sidebar:
    st.header("Watched topics")
    for topic in WATCH_TOPICS:
        st.markdown(f"- {topic}")
    st.divider()
    run_button = st.button("🔍 Run digest now", type="primary", use_container_width=True)

if "digest" not in st.session_state:
    st.session_state.digest = None

if run_button:
    with st.spinner("Searching sources and extracting structured findings..."):
        digest = build_digest()
        save_digest(digest)
        st.session_state.digest = digest

if st.session_state.digest is None:
    st.info("Click **Run digest now** in the sidebar to fetch the latest market intelligence.")
else:
    digest = st.session_state.digest
    if not digest:
        st.warning("No sufficiently relevant results found in this run. Try again later or widen topics.")
    else:
        st.success(f"Found {len(digest)} relevant items.")
        for item in digest:
            score = item.get("relevance_score", 0)
            stars = "⭐" * score
            with st.container(border=True):
                st.markdown(f"### {item.get('headline', 'Untitled')}")
                st.markdown(f"{stars}  ·  **{item.get('event_type', 'unknown').replace('_', ' ').title()}**  ·  {item.get('region', 'unknown')}")
                st.write(item.get("bd_relevance", ""))
                companies = item.get("companies_involved", [])
                if companies:
                    st.markdown("**Companies:** " + ", ".join(companies))
                st.markdown(f"[Source: {item.get('source_title', 'link')}]({item.get('source_url', '#')})")
