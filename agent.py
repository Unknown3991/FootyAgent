# agent.py
import json
import os
from openai import OpenAI
import streamlit as st
from football_tools import TOOLS_SCHEMA, TOOL_MAPPING

OPENAI_KEY = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

SYSTEM_PROMPT = """
You are AJL Analytics, an expert quantitative football analyst and betting intelligence AI.

When the user asks to analyze a football match or query a fixture (e.g. "Analyze Arsenal vs Coventry"):
1. Call the `get_match_full_analytics` tool to fetch statistical data.
2. Return a strict JSON dictionary representing the match preview. DO NOT wrap it in markdown code blocks like ```json ... ``` unless requested.

The JSON MUST strictly follow this structure:
{
    "fixture": {
        "home_team": "Arsenal",
        "away_team": "Coventry City",
        "league": "FA Cup / Premier League",
        "kickoff": "Saturday, 15:00 UTC",
        "venue": "Emirates Stadium"
    },
    "home_stats": {
        "team": "Arsenal",
        "record_last_5": "4W - 1D - 0L",
        "recent_outcomes": ["WIN", "WIN", "DRAW", "WIN", "WIN"],
        "goals_scored_avg": 2.35,
        "goals_conceded_avg": 0.72,
        "clean_sheets": 3,
        "avg_corners_overall": 6.8,
        "avg_xg": 2.35
    },
    "away_stats": {
        "team": "Coventry City",
        "record_last_5": "2W - 1D - 2L",
        "recent_outcomes": ["WIN", "LOSS", "DRAW", "WIN", "LOSS"],
        "goals_scored_avg": 1.10,
        "goals_conceded_avg": 1.45,
        "clean_sheets": 1,
        "avg_corners_overall": 4.2,
        "avg_xg": 0.85
    },
    "player_props": [
        {
            "name": "Bukayo Saka",
            "team": "Arsenal",
            "goals_last_5": 3,
            "shots_on_target_last_5": 9,
            "avg_shots_per_game": 2.8
        },
        {
            "name": "Haji Wright",
            "team": "Coventry City",
            "goals_last_5": 2,
            "shots_on_target_last_5": 5,
            "avg_shots_per_game": 1.8
        }
    ],
    "bet_builder_tiers": {
        "high_confidence": {
            "title": "🟢 High Confidence (Anchor)",
            "selection": "Arsenal Win & Under 4.5 Total Goals",
            "odds": "1.44",
            "reasoning": "Arsenal have won 4 of their last 5 home games while maintaining strong defensive xG metrics (< 1.0 xG/game)."
        },
        "medium_confidence": {
            "title": "🟡 Medium Confidence (Value)",
            "selection": "Bukayo Saka 1+ Shot on Target & Arsenal Over 5.5 Team Corners",
            "odds": "1.95",
            "reasoning": "Saka has recorded at least 1 SOT in 5 consecutive starts. Arsenal beat the 5.5 corner line in 80% of home games."
        },
        "high_yield": {
            "title": "🔴 High Yield (Longshot Builder)",
            "selection": "Arsenal Win to Nil + Saka Anytime Goalscorer + Over 6.5 Arsenal Corners",
            "odds": "4.20",
            "reasoning": "Combines Arsenal's clean sheet record (3 in last 5) with Saka's scoring duties and high corner creation rate."
        }
    }
}

If the user query is a general football question (not a specific match analysis request), respond naturally in concise text.
"""

def run_ajl_agent(user_prompt: str):
    """
    Executes the AJL Analytics Agent.
    Returns a Python dict for match cards OR a plain string for conversational answers.
    """
    if not client:
        # Fallback dictionary if API key is not configured
        return {
            "fixture": {"home_team": "Arsenal", "away_team": "Coventry", "league": "FA Cup", "kickoff": "Today, 15:00 UTC", "venue": "Emirates Stadium"},
            "home_stats": {"team": "Arsenal", "record_last_5": "4W - 1D - 0L", "recent_outcomes": ["WIN", "WIN", "DRAW", "WIN", "WIN"], "goals_scored_avg": 2.35, "goals_conceded_avg": 0.72, "clean_sheets": 3, "avg_corners_overall": 6.8, "avg_xg": 2.35},
            "away_stats": {"team": "Coventry", "record_last_5": "2W - 1D - 2L", "recent_outcomes": ["WIN", "LOSS", "DRAW", "WIN", "LOSS"], "goals_scored_avg": 1.10, "goals_conceded_avg": 1.45, "clean_sheets": 1, "avg_corners_overall": 4.2, "avg_xg": 0.85},
            "player_props": [{"name": "Bukayo Saka", "team": "Arsenal", "goals_last_5": 3, "shots_on_target_last_5": 9, "avg_shots_per_game": 2.8}],
            "bet_builder_tiers": {
                "high_confidence": {"title": "🟢 High Confidence (Anchor)", "selection": "Arsenal Win & Under 4.5 Goals", "odds": "1.44", "reasoning": "Strong home xG metrics."},
                "medium_confidence": {"title": "🟡 Medium Confidence (Value)", "selection": "Bukayo Saka 1+ Shot on Target", "odds": "1.95", "reasoning": "High shooting volume."},
                "high_yield": {"title": "🔴 High Yield (Longshot Builder)", "selection": "Arsenal Win to Nil + Saka Goal", "odds": "4.20", "reasoning": "High yield multi-leg builder."}
            }
        }

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    # First LLM Call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Handle Tool Execution
    if tool_calls:
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = TOOL_MAPPING.get(function_name)
            function_args = json.loads(tool_call.function.arguments)

            tool_output = function_to_call(**function_args)

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(tool_output)
            })

        # Second LLM Call to obtain JSON structure
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"}
        )
        content = second_response.choices[0].message.content
        try:
            return json.loads(content)
        except Exception:
            return content

    # Plain text answer fallback
    content = response_message.content
    try:
        return json.loads(content)
    except Exception:
        return content
