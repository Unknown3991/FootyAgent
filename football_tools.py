# football_tools.py
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Check Streamlit Cloud secrets first, fallback to os.getenv for local dev
FD_KEY = st.secrets.get("FOOTBALL_DATA_KEY") if "FOOTBALL_DATA_KEY" in st.secrets else os.getenv("FOOTBALL_DATA_KEY")
API_FOOTBALL_KEY = st.secrets.get("API_FOOTBALL_KEY") if "API_FOOTBALL_KEY" in st.secrets else os.getenv("API_FOOTBALL_KEY")

FD_BASE = "https://api.football-data.org/v4"
APIF_BASE = "https://v3.football.api-sports.io"

FD_HEADERS = {"X-Auth-Token": FD_KEY}
APIF_HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}


# -----------------------------------------------------------------------------
# 1. UPCOMING FIXTURES TOOL
# -----------------------------------------------------------------------------
# Replace get_upcoming_fixtures in football_tools.py with this:

def get_upcoming_fixtures(league="PL", limit=5):
    """Fetches the next 'limit' upcoming scheduled matches from Football-Data.org."""
    url = f"{FD_BASE}/competitions/{league}/matches?status=SCHEDULED"
    
    try:
        res = requests.get(url, headers=FD_HEADERS, timeout=10)
        
        if res.status_code != 200:
            print(f"Football-Data API Error [{res.status_code}]: {res.text}")
            
        matches = res.json().get("matches", []) if res.status_code == 200 else []

        # Fallback: If no SCHEDULED matches found, query matches directly
        if not matches:
            fallback_url = f"{FD_BASE}/competitions/{league}/matches"
            res_fb = requests.get(fallback_url, headers=FD_HEADERS, timeout=10)
            if res_fb.status_code == 200:
                all_matches = res_fb.json().get("matches", [])
                matches = [m for m in all_matches if m.get("status") in ["SCHEDULED", "TIMED", "POSTPONED"]]

        # CRITICAL FIX: Slice to return only the next 'limit' fixtures (e.g. 5)
        upcoming_slice = matches[:limit]

        return [
            {
                "id": m["id"],
                "home_team": m["homeTeam"]["name"],
                "away_team": m["awayTeam"]["name"],
                "utc_date": m["utcDate"]
            }
            for m in upcoming_slice
        ]

    except Exception as e:
        print(f"Exception fetching upcoming fixtures: {e}")
        return []


# -----------------------------------------------------------------------------
# 2. FULL TEAM 22 METRICS TOOL
# -----------------------------------------------------------------------------
def get_team_full_22_stats(team_name):
    """
    Queries API-Football for comprehensive team stats across 22 key metrics.
    """
    # Search for Team ID
    res = requests.get(f"{APIF_BASE}/teams?search={team_name}", headers=APIF_HEADERS)
    if res.status_code != 200 or not res.json().get("response"):
        return {"error": f"Team '{team_name}' not found."}

    team_data = res.json()["response"][0]["team"]
    team_id = team_data["id"]
    official_name = team_data["name"]

    # Get Team Statistics
    stats_url = f"{APIF_BASE}/teams/statistics?team={team_id}&league=39&season=2025"
    s_res = requests.get(stats_url, headers=APIF_HEADERS)
    
    if s_res.status_code != 200 or not s_res.json().get("response"):
        # Fallback to previous season parameter if current season data is pending
        s_res = requests.get(f"{APIF_BASE}/teams/statistics?team={team_id}&league=39&season=2024", headers=APIF_HEADERS)

    if s_res.status_code != 200 or not s_res.json().get("response"):
        return {"error": f"Could not fetch team statistics for {official_name}."}

    s = s_res.json()["response"]
    fixtures = s.get("fixtures", {})
    goals = s.get("goals", {})
    clean_sheets = s.get("clean_sheet", {})
    failed_to_score = s.get("failed_to_score", {})
    penalty = s.get("penalty", {})
    cards = s.get("cards", {})

    played = fixtures.get("played", {}).get("total", 1) or 1

    # Extract 22 Quantitative Metrics
    metrics_22 = {
        "team": official_name,
        "1_matches_played": played,
        "2_wins_total": fixtures.get("wins", {}).get("total", 0),
        "3_draws_total": fixtures.get("draws", {}).get("total", 0),
        "4_losses_total": fixtures.get("loses", {}).get("total", 0),
        "5_goals_scored_total": goals.get("for", {}).get("total", {}).get("total", 0),
        "6_goals_conceded_total": goals.get("against", {}).get("total", {}).get("total", 0),
        "7_avg_goals_scored_per_game": goals.get("for", {}).get("average", {}).get("total", "0.0"),
        "8_avg_goals_conceded_per_game": goals.get("against", {}).get("average", {}).get("total", "0.0"),
        "9_clean_sheets_total": clean_sheets.get("total", 0),
        "10_failed_to_score_total": failed_to_score.get("total", 0),
        "11_home_wins": fixtures.get("wins", {}).get("home", 0),
        "12_away_wins": fixtures.get("wins", {}).get("away", 0),
        "13_home_goals_scored": goals.get("for", {}).get("total", {}).get("home", 0),
        "14_away_goals_scored": goals.get("for", {}).get("total", {}).get("away", 0),
        "15_penalties_scored": penalty.get("scored", {}).get("total", 0),
        "16_penalties_missed": penalty.get("missed", {}).get("total", 0),
        "17_yellow_cards_total": cards.get("yellow", {}).get("total", 0) or sum([v.get("total") or 0 for v in cards.get("yellow", {}).values() if isinstance(v, dict)]),
        "18_red_cards_total": cards.get("red", {}).get("total", 0) or sum([v.get("total") or 0 for v in cards.get("red", {}).values() if isinstance(v, dict)]),
        "19_biggest_win_home": s.get("biggest", {}).get("wins", {}).get("home"),
        "20_biggest_win_away": s.get("biggest", {}).get("wins", {}).get("away"),
        "21_biggest_loss_home": s.get("biggest", {}).get("loses", {}).get("home"),
        "22_biggest_loss_away": s.get("biggest", {}).get("loses", {}).get("away")
    }

    return metrics_22


# -----------------------------------------------------------------------------
# 3. DEEP HEAD-TO-HEAD (H2H) TOOL
# -----------------------------------------------------------------------------
def get_deep_head_to_head(team1_name, team2_name):
    """
    Fetches the historical head-to-head match records between two teams.
    """
    # 1. Resolve Team 1
    t1_res = requests.get(f"{APIF_BASE}/teams?search={team1_name}", headers=APIF_HEADERS)
    if not t1_res.json().get("response"):
        return {"error": f"Team '{team1_name}' not found."}
    t1_id = t1_res.json()["response"][0]["team"]["id"]

    # 2. Resolve Team 2
    t2_res = requests.get(f"{APIF_BASE}/teams?search={team2_name}", headers=APIF_HEADERS)
    if not t2_res.json().get("response"):
        return {"error": f"Team '{team2_name}' not found."}
    t2_id = t2_res.json()["response"][0]["team"]["id"]

    # 3. Fetch H2H Fixtures
    h2h_url = f"{APIF_BASE}/fixtures/headtohead?h2h={t1_id}-{t2_id}"
    res = requests.get(h2h_url, headers=APIF_HEADERS)
    
    if res.status_code != 200 or not res.json().get("response"):
        return {"error": f"No H2H history found between {team1_name} and {team2_name}."}

    fixtures = res.json()["response"][:8]

    history = []
    for f in fixtures:
        league_name = f.get("league", {}).get("name")
        match_date = f.get("fixture", {}).get("date", "")[:10]
        home = f.get("teams", {}).get("home", {}).get("name")
        away = f.get("teams", {}).get("away", {}).get("name")
        goals_home = f.get("goals", {}).get("home")
        goals_away = f.get("goals", {}).get("away")

        history.append({
            "date": match_date,
            "competition": league_name,
            "match": f"{home} {goals_home} - {goals_away} {away}"
        })

    return {
        "teams": [team1_name, team2_name],
        "recent_meetings_count": len(history),
        "history": history
    }


# -----------------------------------------------------------------------------
# 4. PLAYER STATISTICS & PLAYER PROPS TOOL
# -----------------------------------------------------------------------------
def get_top_player_stats(team_name):
    """
    Retrieves the top 3 players for a team across 4 key player betting markets:
    - Shots
    - Shots on Target
    - Tackles
    - Bookings / Yellow Cards
    """
    res = requests.get(f"{APIF_BASE}/teams?search={team_name}", headers=APIF_HEADERS)
    if res.status_code != 200 or not res.json().get("response"):
        return {"error": f"Team '{team_name}' not found for player statistics."}

    team_data = res.json()["response"][0]["team"]
    team_id = team_data["id"]
    official_name = team_data["name"]

    # Query Team Player Statistics
    players_url = f"{APIF_BASE}/players?team={team_id}&season=2025"
    p_res = requests.get(players_url, headers=APIF_HEADERS)

    if p_res.status_code != 200 or not p_res.json().get("response"):
        p_res = requests.get(f"{APIF_BASE}/players?team={team_id}&season=2024", headers=APIF_HEADERS)

    if p_res.status_code != 200 or not p_res.json().get("response"):
        return {"error": f"Could not retrieve player statistics for {official_name}."}

    players_raw = p_res.json()["response"]

    parsed_players = []
    for item in players_raw:
        player_info = item["player"]
        stats_list = item["statistics"]
        if not stats_list:
            continue
        
        s = stats_list[0]
        
        parsed_players.append({
            "name": player_info.get("name"),
            "position": s.get("games", {}).get("position"),
            "appearances": s.get("games", {}).get("appearences") or 0,
            "shots_total": s.get("shots", {}).get("total") or 0,
            "shots_on_target": s.get("shots", {}).get("on") or 0,
            "tackles_total": s.get("tackles", {}).get("total") or 0,
            "yellow_cards": s.get("cards", {}).get("yellow") or 0,
            "red_cards": s.get("cards", {}).get("red") or 0
        })

    if not parsed_players:
        return {"error": f"No detailed player profiles returned for {official_name}."}

    # Sort & Extract Top 3 for each category
    top_shots = sorted(parsed_players, key=lambda x: x["shots_total"], reverse=True)[:3]
    top_shots_on_target = sorted(parsed_players, key=lambda x: x["shots_on_target"], reverse=True)[:3]
    top_tackles = sorted(parsed_players, key=lambda x: x["tackles_total"], reverse=True)[:3]
    top_bookings = sorted(parsed_players, key=lambda x: x["yellow_cards"], reverse=True)[:3]

    return {
        "team": official_name,
        "most_shots": [
            {"player": p["name"], "position": p["position"], "total_shots": p["shots_total"], "per_game": round(p["shots_total"] / max(1, p["appearances"]), 2)}
            for p in top_shots
        ],
        "most_shots_on_target": [
            {"player": p["name"], "position": p["position"], "shots_on_target": p["shots_on_target"], "per_game": round(p["shots_on_target"] / max(1, p["appearances"]), 2)}
            for p in top_shots_on_target
        ],
        "most_tackles": [
            {"player": p["name"], "position": p["position"], "tackles": p["tackles_total"], "per_game": round(p["tackles_total"] / max(1, p["appearances"]), 2)}
            for p in top_tackles
        ],
        "most_bookings": [
            {"player": p["name"], "position": p["position"], "yellow_cards": p["yellow_cards"], "red_cards": p["red_cards"]}
            for p in top_bookings
        ]
    }


# -----------------------------------------------------------------------------
# 5. OPENAI TOOL SCHEMAS & MAPPINGS
# -----------------------------------------------------------------------------
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_fixtures",
            "description": "Retrieves upcoming scheduled Premier League match fixtures.",
            "parameters": {
                "type": "object",
                "properties": {
                    "league": {"type": "string", "description": "League code e.g. PL for Premier League"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_full_22_stats",
            "description": "Retrieves 22 comprehensive team metrics including goals, clean sheets, penalties, and discipline.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_name": {"type": "string", "description": "Football team name e.g. Arsenal or Chelsea"}
                },
                "required": ["team_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_deep_head_to_head",
            "description": "Retrieves head-to-head match history between two football teams.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team1_name": {"type": "string", "description": "First team name"},
                    "team2_name": {"type": "string", "description": "Second team name"}
                },
                "required": ["team1_name", "team2_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_player_stats",
            "description": "Retrieves top 3 players for a team for total shots, shots on target, tackles, and bookings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_name": {"type": "string", "description": "Football team name e.g. Arsenal or Chelsea"}
                },
                "required": ["team_name"]
            }
        }
    }
]

TOOL_MAPPING = {
    "get_upcoming_fixtures": get_upcoming_fixtures,
    "get_team_full_22_stats": get_team_full_22_stats,
    "get_deep_head_to_head": get_deep_head_to_head,
    "get_top_player_stats": get_top_player_stats
}
