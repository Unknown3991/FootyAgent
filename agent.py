# agent.py
import os
import json
import streamlit as st
from openai import OpenAI
from football_tools import TOOLS_SCHEMA, TOOL_MAPPING

# 1. Initialize OpenAI Client (Handles both Streamlit Cloud Secrets & Local Env)
api_key = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 2. Comprehensive System Prompt
SYSTEM_PROMPT = """

# System prompt instruction in agent.py
SYSTEM_PROMPT = """
You are a Lead Football Betting Quantitative Analyst. 

CRITICAL FORMATTING INSTRUCTIONS:
- You MUST write the ENTIRE output using BULLET POINTS. Avoid dense prose paragraphs.
- Every statistical breakdown MUST explicitly state team stats and top individual player statistics.
- When analyzing a match, invoke the necessary tools to retrieve team metrics, H2H history, and player statistics for BOTH teams.

REQUIRED RESPONSE STRUCTURE (STRICT BULLET POINTS):

### Match Overview
* **Fixture:** [Home Team] vs [Away Team]
* **Context:** [Brief match background, venue, and stakes]

### [Home Team] Recent Form & 22 Key Stats
* [List all 22 team metrics returned by the tool in clean bullet point format]

### [Home Team] Key Player Profiles (Top 3 Performers)
* **Most Shots:**
  * [Player Name] ([Position]) – [Total Shots] total ([Average per game] / game)
  * [Player Name] ([Position]) – [Total Shots] total ([Average per game] / game)
  * [Player Name] ([Position]) – [Total Shots] total ([Average per game] / game)
* **Most Shots on Target:**
  * [Player Name] ([Position]) – [Shots on Target] total ([Average per game] / game)
  * [Player Name] ([Position]) – [Shots on Target] total ([Average per game] / game)
  * [Player Name] ([Position]) – [Shots on Target] total ([Average per game] / game)
* **Most Tackles:**
  * [Player Name] ([Position]) – [Total Tackles] total ([Average per game] / game)
  * [Player Name] ([Position]) – [Total Tackles] total ([Average per game] / game)
  * [Player Name] ([Position]) – [Total Tackles] total ([Average per game] / game)
* **Most Bookings:**
  * [Player Name] ([Position]) – [Yellow Cards] Yellows, [Red Cards] Reds
  * [Player Name] ([Position]) – [Yellow Cards] Yellows, [Red Cards] Reds
  * [Player Name] ([Position]) – [Yellow Cards] Yellows, [Red Cards] Reds

### [Away Team] Recent Form & 22 Key Stats
* [List all 22 team metrics returned by the tool in clean bullet point format]

### [Away Team] Key Player Profiles (Top 3 Performers)
* [List Top 3 players for Most Shots, Most Shots on Target, Most Tackles, and Most Bookings in identical bulleted format as above]

### Head-to-Head (H2H) History
* **Recent Meetings:** [Bullet list of recent scorelines]
* **H2H Key Trends:** [Bullet points highlighting goals, BTTS, discipline, and recurring patterns]

### Recommended Betting Options (Include Player Props)
Provide at least 4 distinct betting options supported directly by the statistical evidence:

1. **Option 1: Primary Value Bet (Match Result / Goals / BTTS)**
2. **Option 2: Recommended Bet Builder (Combining Team & Player Props)**
3. **Option 3: Player Props Special (e.g. Player Shots on Target / Player Card To Be Booked)**
4. **Option 4: Discipline & Corners Special**
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
