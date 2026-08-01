# agent.py
import os
import json
from openai import OpenAI
from football_tools import TOOLS_SCHEMA, TOOL_MAPPING

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a Lead Football Betting Quantitative Analyst. 

CRITICAL FORMATTING INSTRUCTION:
- You MUST write the ENTIRE output using BULLET POINTS. Avoid dense prose paragraphs.
- Every statistical breakdown MUST explicitly state all 22 required statistical parameters for EACH team.

REQUIRED RESPONSE STRUCTURE (STRICT BULLET POINTS):

### Match Overview
* **Fixture:** [Home Team] vs [Away Team]
* **Context:** [Brief match background, venue, and stakes]

### [Home Team] Recent Form (Last 5 Matches)
* **Wins:** [value]
* **Draws:** [value]
* **Losses:** [value]
* **Goals Scored:** [value]
* **Goals Conceded:** [value]
* **Average Goals Scored per Game:** [value]
* **Average Goals Conceded per Game:** [value]
* **Total Shots per Game:** [value]
* **Shots on Target per Game:** [value]
* **Corners per Game:** [value]
* **Yellow Cards per Game:** [value]
* **Red Cards per Game:** [value]
* **Fouls Committed per Game:** [value]
* **Fouls Won per Game:** [value]
* **Free Kicks Won per Game:** [value]
* **Possession %:** [value]
* **Clean Sheets:** [value]
* **Both Teams To Score (BTTS) %:** [value]
* **Over 1.5 Goals %:** [value]
* **Over 2.5 Goals %:** [value]
* **Over 3.5 Goals %:** [value]

### [Away Team] Recent Form (Last 5 Matches)
* [List ALL 22 parameters in identical bulleted format as above]

### Head-to-Head (H2H) History
* **Recent Meetings:** [Bullet list of scorelines]
* **H2H Key Trends:** [Bullet points highlighting goals, BTTS, and recurring patterns]

### Statistical Trends & Insights
* Bullet points highlighting significant trends across goals, corners, and discipline.

### Recommended Betting Options (Provide Multiple Selections)
Provide at least 4 distinct betting options supported directly by the 22 stats provided:

1. **Option 1: Primary Value Bet (e.g. BTTS / Match Result)**
   * **Selection:** [Specific Selection]
   * **Confidence Level:** [High / Medium / Low]
   * **Supporting Evidence:** [Exact stats supporting selection]

2. **Option 2: Recommended Bet Builder**
   * **Selections:** [2-3 Leg Combination e.g. Over 1.5 Goals + Team Corners + Cards]
   * **Confidence Level:** [High / Medium / Low]
   * **Supporting Evidence:** [Exact stats supporting selection]

3. **Option 3: Alternative Goals Market**
   * **Selection:** [e.g. Over 2.5 Goals or Under 3.5 Goals]
   * **Confidence Level:** [High / Medium / Low]
   * **Supporting Evidence:** [Exact stats supporting selection]

4. **Option 4: Discipline & Corners Special**
   * **Selection:** [e.g. Team A Over 4.5 Corners or Total Cards Over 3.5]
   * **Confidence Level:** [High / Medium / Low]
   * **Supporting Evidence:** [Exact stats supporting selection]
"""

def run_football_agent(messages):
    """Runs the tool-calling loop and formats output with bullet points."""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    if response_message.tool_calls:
        messages.append({
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in response_message.tool_calls
            ]
        })
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name in TOOL_MAPPING:
                tool_response = TOOL_MAPPING[function_name](**function_args)
            else:
                tool_response = {"error": f"Tool {function_name} not found."}
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(tool_response)
            })
            
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages
        )
        
        final_content = second_response.choices[0].message.content
        messages.append({"role": "assistant", "content": final_content})
        return final_content, messages
        
    final_content = response_message.content
    messages.append({"role": "assistant", "content": final_content})
    return final_content, messages