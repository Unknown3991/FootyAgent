# football_tools.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

FD_KEY = os.getenv("FOOTBALL_DATA_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

FD_HEADERS = {"X-Auth-Token": FD_KEY}
APIF_HEADERS = {
    "x-apisports-key": API_FOOTBALL_KEY,
    "x-rapidapi-key": API_FOOTBALL_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

FD_BASE = "https://api.football-data.org/v4"
APIF_BASE = "https://v3.football.api-sports.io"


def get_upcoming_fixtures(league="PL"):
    """Fetches upcoming scheduled matches from Football-Data.org."""
    url = f"{FD_BASE}/competitions/{league}/matches?status=SCHEDULED"
    res = requests.get(url, headers=FD_HEADERS)
    if res.status_code == 200:
        matches = res.json().get("matches", [])[:5]
        return [
            {
                "id": m["id"],
                "home_team": m["homeTeam"]["name"],
                "away_team": m["awayTeam"]["name"],
                "utc_date": m["utcDate"]
            }
            for m in matches
        ]
    return []


def get_team_full_22_stats(team_name):
    """
    Calculates the 22 specific statistical requirements across the last 5 completed games.
    """
    # 1. Get Team ID
    res = requests.get(f"{APIF_BASE}/teams?search={team_name}", headers=APIF_HEADERS)
    if res.status_code != 200 or not res.json().get("response"):
        return {"error": f"Team '{team_name}' could not be located."}
        
    team_data = res.json()["response"][0]["team"]
    team_id = team_data["id"]
    official_name = team_data["name"]

    # 2. Get last 5 finished fixtures
    fix_res = requests.get(f"{APIF_BASE}/fixtures?team={team_id}&last=5&status=FT", headers=APIF_HEADERS)
    if fix_res.status_code != 200 or not fix_res.json().get("response"):
        return {"error": f"Could not pull match history for {official_name}."}

    fixtures = fix_res.json()["response"]
    if not fixtures:
        return {"error": f"No recent completed matches found for {official_name}."}

    sample_size = len(fixtures)

    # Metrics Trackers
    wins, draws, losses = 0, 0, 0
    goals_scored, goals_conceded = 0, 0
    clean_sheets = 0
    btts_count = 0
    over_1_5, over_2_5, over_3_5 = 0, 0, 0

    total_shots = 0
    total_shots_on_target = 0
    total_corners = 0
    total_yellows = 0
    total_reds = 0
    total_fouls_committed = 0
    total_fouls_won = 0
    total_free_kicks = 0
    total_possession = 0

    for f in fixtures:
        is_home = f["teams"]["home"]["id"] == team_id
        t_goals = f["goals"]["home"] if is_home else f["goals"]["away"]
        o_goals = f["goals"]["away"] if is_home else f["goals"]["home"]

        if t_goals is not None and o_goals is not None:
            goals_scored += t_goals
            goals_conceded += o_goals
            
            if t_goals > o_goals: wins += 1
            elif t_goals == o_goals: draws += 1
            else: losses += 1

            if o_goals == 0: clean_sheets += 1
            if t_goals > 0 and o_goals > 0: btts_count += 1
            
            m_goals = t_goals + o_goals
            if m_goals > 1.5: over_1_5 += 1
            if m_goals > 2.5: over_2_5 += 1
            if m_goals > 3.5: over_3_5 += 1

        # Deep Game Stats (Shots, Corners, Cards, Fouls, Possession)
        fix_id = f["fixture"]["id"]
        st_res = requests.get(f"{APIF_BASE}/fixtures/statistics?fixture={fix_id}", headers=APIF_HEADERS)
        if st_res.status_code == 200 and st_res.json().get("response"):
            for item in st_res.json()["response"]:
                if item["team"]["id"] == team_id:
                    stats = {s["type"]: s["value"] for s in item["statistics"]}
                    
                    total_shots += (stats.get("Total Shots") or 0)
                    total_shots_on_target += (stats.get("Shots on Goal") or 0)
                    total_corners += (stats.get("Corner Kicks") or 0)
                    total_yellows += (stats.get("Yellow Cards") or 0)
                    total_reds += (stats.get("Red Cards") or 0)
                    total_fouls_committed += (stats.get("Fouls") or 0)
                    
                    # Possession extraction (remove % string)
                    poss_raw = str(stats.get("Ball Possession") or "50%").replace("%", "")
                    try:
                        total_possession += float(poss_raw)
                    except ValueError:
                        total_possession += 50.0

                else:
                    # Opponent stats used for calculating fouls won & free kicks
                    opp_stats = {s["type"]: s["value"] for s in item["statistics"]}
                    total_fouls_won += (opp_stats.get("Fouls") or 0)
                    total_free_kicks += (opp_stats.get("Fouls") or 0)

    return {
        "team": official_name,
        "sample_size": f"Last {sample_size} Matches",
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_scored": goals_scored,
        "goals_conceded": goals_conceded,
        "avg_goals_scored_per_game": round(goals_scored / sample_size, 2),
        "avg_goals_conceded_per_game": round(goals_conceded / sample_size, 2),
        "total_shots_per_game": round(total_shots / sample_size, 2),
        "shots_on_target_per_game": round(total_shots_on_target / sample_size, 2),
        "corners_per_game": round(total_corners / sample_size, 2),
        "yellow_cards_per_game": round(total_yellows / sample_size, 2),
        "red_cards_per_game": round(total_reds / sample_size, 2),
        "fouls_committed_per_game": round(total_fouls_committed / sample_size, 2),
        "fouls_won_per_game": round(total_fouls_won / sample_size, 2),
        "free_kicks_won_per_game": round(total_free_kicks / sample_size, 2),
        "possession_pct": f"{round(total_possession / sample_size, 1)}%",
        "clean_sheets": clean_sheets,
        "btts_rate": f"{round((btts_count / sample_size) * 100, 1)}%",
        "over_1_5_goals_pct": f"{round((over_1_5 / sample_size) * 100, 1)}%",
        "over_2_5_goals_pct": f"{round((over_2_5 / sample_size) * 100, 1)}%",
        "over_3_5_goals_pct": f"{round((over_3_5 / sample_size) * 100, 1)}%"
    }


def get_deep_head_to_head(home_team, away_team):
    """Retrieves head-to-head match history."""
    res_home = requests.get(f"{APIF_BASE}/teams?search={home_team}", headers=APIF_HEADERS)
    res_away = requests.get(f"{APIF_BASE}/teams?search={away_team}", headers=APIF_HEADERS)
    
    h_resp = res_home.json().get("response")
    a_resp = res_away.json().get("response")

    if not h_resp or not a_resp:
        return {"error": "Could not identify teams for H2H lookup."}
        
    h_id = h_resp[0]["team"]["id"]
    a_id = a_resp[0]["team"]["id"]
    
    h2h_res = requests.get(f"{APIF_BASE}/fixtures/headtohead?h2h={h_id}-{a_id}&last=5", headers=APIF_HEADERS)
    
    if h2h_res.status_code == 200:
        matches = h2h_res.json().get("response", [])
        history = []
        for m in matches:
            history.append({
                "date": m["fixture"]["date"][:10],
                "score": f"{m['teams']['home']['name']} {m['goals']['home']} - {m['goals']['away']} {m['teams']['away']['name']}"
            })
        return {"matchup": f"{home_team} vs {away_team}", "recent_h2h_meetings": history}
        
    return {"error": "Failed to fetch H2H data."}


# Tool Definitions
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_fixtures",
            "description": "Get upcoming fixtures for Premier League (PL) or Championship (ELC).",
            "parameters": {
                "type": "object",
                "properties": {
                    "league": {"type": "string"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_full_22_stats",
            "description": "Retrieves the exact 22 requested stats for a team calculated over their last 5 matches.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_name": {"type": "string"}
                },
                "required": ["team_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_deep_head_to_head",
            "description": "Retrieves head to head historical matches.",
            "parameters": {
                "type": "object",
                "properties": {
                    "home_team": {"type": "string"},
                    "away_team": {"type": "string"}
                },
                "required": ["home_team", "away_team"]
            }
        }
    }
]

TOOL_MAPPING = {
    "get_upcoming_fixtures": get_upcoming_fixtures,
    "get_team_full_22_stats": get_team_full_22_stats,
    "get_deep_head_to_head": get_deep_head_to_head
}