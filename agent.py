# agent.py
import json
from openai import OpenAI
import streamlit as st
import os
from football_tools import TOOLS_SCHEMA, TOOL_MAPPING

OPENAI_KEY = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

SYSTEM_PROMPT = """
You are AJL Analytics, an elite quant football analyst and betting intelligence agent.
Your objective is to analyze football fixtures using Expected Goals (xG), corner trends, 
clean sheet rates, and key player shooting stats (shots, shots on target, goals).

Always format match predictions cleanly with:
1. Match Statistical Overview (Form, xG home/away, Corner averages, Key Player prop trends).
2. Recommended 3-Tier Bet Builder:
   - 🟢 High Confidence (Anchor): Safe/low-risk selection backed by high statistical probability.
   - 🟡 Medium Confidence (Value): Balanced value bet combining team and player props.
   - 🔴 High Yield (Longshot Builder): Multi-leg high-odds builder.

Keep prose direct, concise, and structured. Use bold formatting and clean bullet points.
"""

def run_ajl_agent(user_prompt: str):
    if not client:
        return "OpenAI API Key is missing. Please set OPENAI_API_KEY in Streamlit Secrets."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    # First completion call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

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

        # Second completion after tool execution
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return second_response.choices[0].message.content

    return response_message.content
