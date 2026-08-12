# agent.py
import os
import json
import streamlit as st
from openai import OpenAI
from football_tools import TOOLS_SCHEMA, TOOL_MAPPING

# 1. Initialize OpenAI Client (Handles both Streamlit Cloud Secrets & Local Env)
api_key = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 2. Comprehensive System Prompt focused on Last 5 Matches Analysis
SYSTEM_PROMPT = """You are a Lead Football Betting Quantitative Analyst.

TOOL NAMING RULE:
- When calling tool functions, always pass simple core team names without official club suffixes (e.g., use 'Hull City' instead of 'Hull City AFC', 'Manchester United' instead of 'Manchester United FC').

CRITICAL INSTRUCTIONS:
- When analyzing a match between two teams, call `get_team_last_5_matches` for BOTH teams AND call `get_head_to_head_last_5` for the match-up.
- Output your ENTIRE analysis strictly using BULLET POINTS. Avoid dense prose paragraphs.

REQUIRED RESPONSE STRUCTURE (STRICT BULLET POINTS):

### Match Overview
* **Fixture:** [Home Team] vs [Away Team]
* **Context:** [Brief match background, competition, and current stakes]

### [Home Team] Last 5 Matches Form & Stats
* **Record (Last 5):** [e.g. 3W - 1D - 1L]
* **Goals Scored:** [Total goals] ([Average per game] / game)
* **Goals Conceded:** [Total conceded] ([Average per game] / game)
* **Clean Sheets:** [Count]
* **Failed to Score:** [Count]
* **Recent Match Results:**
  * [Date] | [Competition] | [Venue] vs [Opponent] | Score: [Score] ([Outcome])
  * [List all matches returned by tool]

### [Away Team] Last 5 Matches Form & Stats
* **Record (Last 5):** [e.g. 2W - 2D - 1L]
* **Goals Scored:** [Total goals] ([Average per game] / game)
* **Goals Conceded:** [Total conceded] ([Average per game] / game)
* **Clean Sheets:** [Count]
* **Failed to Score:** [Count]
* **Recent Match Results:**
  * [Date] | [Competition] | [Venue] vs [Opponent] | Score: [Score] ([Outcome])
  * [List all matches returned by tool]

### Head-to-Head (H2H) History (Last 5 Meetings)
* **H2H Summary:** [Total Meetings, Team 1 Wins, Team 2 Wins, Draws]
* **Recent Meetings:**
  * [List individual H2H match scorelines returned by tool]

### Key Form & Statistical Trends
* [Bullet point highlighting scoring trends (Over/Under 2.5 goals, Both Teams to Score)]
* [Bullet point highlighting defensive trends and clean sheet consistency]
* [Bullet point highlighting home/away performance variances]

### Recommended Betting Options
Provide 4 distinct betting options directly supported by the last 5 match metrics:

1. **Option 1: Primary Value Bet (Match Result / Double Chance)**
2. **Option 2: Goals Market Special (Over/Under 2.5 Goals or Both Teams To Score)**
3. **Option 3: Team Prop / Half-Time Special**
4. **Option 4: High-Yield Value / Bet Builder Combination**
"""


def run_football_agent(messages):
    """
    Executes the multi-step OpenAI Tool Calling Agent loop.
    """
    # Prepend System Prompt to history
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    # Agent Loop (max 5 tool iterations)
    for _ in range(5):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        conversation.append(response_message)

        # Check if model wants to call tools
        tool_calls = response_message.tool_calls
        if not tool_calls:
            # Final text answer reached
            return response_message.content, conversation[1:]

        # Execute requested tools
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            if func_name in TOOL_MAPPING:
                tool_output = TOOL_MAPPING[func_name](**func_args)
            else:
                tool_output = {"error": f"Tool '{func_name}' not implemented."}

            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_output)
            })

    # Final fallback if loop ends
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation
    )
    return final_response.choices[0].message.content, conversation[1:]
