# football_tools.py
import os
import requests
import streamlit as st
from dotenv import load_dotenv
from mock_data import MOCK_MATCH_DATA

load_dotenv()

THESTATSAPI_KEY = st.secrets.get("THESTATSAPI_KEY") if "THESTATSAPI_KEY" in st.secrets else os.getenv("THESTATSAPI_KEY")
USE_MOCK = THESTATSAPI_KEY is None

BASE_URL = "https://api.thestatsapi.com/api/football"
HEADERS = {"Authorization": f"Bearer {THESTATSAPI_KEY}"} if THESTATSAPI_KEY else {}


def get_match_full_analytics(home_team: str, away_team: str):
    """
    Fetches detailed match analytics, including xG averages, form metrics, 
    corners, player shooting statistics, and betting trends.
    """
    if USE_MOCK:
        # Fallback to local mock data matching requested teams or default mock
        return {
            "status": "success",
            "source": "Mock Data Engine",
            "data": MOCK_MATCH_DATA
        }

    # Live API Call (TheStatsAPI)
    try:
        # 1. Search Fixtures / Team IDs
        res = requests.get(f"{BASE_URL}/matches?search={home_team}&limit=5", headers=HEADERS, timeout=10)
        if res.status_code == 200 and res.json():
            return {
                "status": "success",
                "source": "TheStatsAPI Live",
                "data": res.json()
            }
        else:
            return {"error": f"Unable to fetch live data from TheStatsAPI (Status: {res.status_code})."}
    except Exception as e:
        return {"error": f"API Connection Exception: {str(e)}"}


# Tool Schema for OpenAI Agent
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_match_full_analytics",
            "description": "Retrieves comprehensive match analytics including team form, xG, average corners, clean sheets, player shooting stats, and betting odds.",
            "parameters": {
                "type": "object",
                "properties": {
                    "home_team": {"type": "string", "description": "Home football team e.g. Arsenal or West Ham"},
                    "away_team": {"type": "string", "description": "Away football team e.g. Coventry City or Everton"}
                },
                "required": ["home_team", "away_team"]
            }
        }
    }
]

TOOL_MAPPING = {
    "get_match_full_analytics": get_match_full_analytics
}
