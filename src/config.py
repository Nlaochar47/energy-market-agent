"""
Central config for the energy market monitoring agent.
Keep topics/keywords here so they're easy to tune without touching pipeline code.
"""

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Topics to monitor. Each becomes one or more Tavily search queries.
# Tuned toward BESS / ERCOT / Texas power market / competitor BD activity.
WATCH_TOPICS = [
    # Direct competitors in Texas BESS / ERCOT merchant storage
    "Energy Vault battery storage Texas ERCOT",
    "Jupiter Power ERCOT battery storage project",
    "battery energy storage system (BESS) project announcement Texas ERCOT",

    # Financing/offtake comparables relevant to Megamouth's economics
    "battery storage project financing offtake agreement ERCOT",

    # Market conditions that change project economics
    "ERCOT power market regulatory update ancillary services",
    "ERCOT interconnection queue battery storage",

    # Adjacent gas market activity (Banpu also has gas assets)
    "natural gas power plant investment Texas",
    "independent power producer acquisition Texas natural gas",
]

# How many days back to consider a result "recent"
MAX_RESULT_AGE_DAYS = 14

# How many raw search results to pull per topic
RESULTS_PER_TOPIC = 5

# Model for the extraction/structuring step
EXTRACTION_MODEL = "gpt-4o-mini"
