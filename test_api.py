import os
import requests
import streamlit as st

# 1. Retrieve API key
try:
    API_KEY = st.secrets["thestatsapi"]["api_key"]
    print("✓ API Key loaded from st.secrets")
except Exception:
    API_KEY = os.getenv("THESTATSAPI_KEY", "")
    print(
        f"✓ API Key loaded from environment: {API_KEY[:4]}***"
        if API_KEY
        else "❌ No API Key found!"
    )

BASE_URL = "https://api.thestatsapi.com/api/football"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

print("\n--- TEST 1: Ping Matches Endpoint ---")
try:
    response = requests.get(
        f"{BASE_URL}/matches",
        headers=headers,
        params={"search": "Liverpool"},
        timeout=10,
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("Raw Response Data:")
        print(data)
    else:
        print(f"❌ Request failed with status {response.status_code}:")
        print(response.text)

except Exception as e:
    print(f"❌ Connection Exception: {e}")
