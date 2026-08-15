# football_tools.py
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

FD_KEY = st.secrets.get("FOOTBALL_DATA_KEY") if "FOOTBALL_DATA_KEY" in st.secrets else os.getenv("FOOTBALL_DATA_KEY")
API_FOOTBALL_KEY = st.secrets.get("API_FOOTBALL_KEY") if "API_FOOTBALL_KEY" in st.secrets else os.getenv("API_FOOTBALL_KEY")

FD_BASE = "https://api.football-data.org/v4"
APIF_BASE = "https://v3.football.api-sports.io"

FD_HEADERS = {"X-Auth-Token": FD_KEY} if FD_KEY else {}
APIF_HEADERS = {"x-apisports-key": API_FOOTBALL_KEY} if API_FOOTBALL_KEY else {}

# Direct lookup map for common API-Football IDs (bypasses API search completely)
KNOWN_TEAM_IDS = {
    "arsenal": (42, "Arsenal"),
    "arsenal fc": (42, "Arsenal"),
    "coventry": (1070, "Coventry"),
    "coventry city": (1070, "Coventry"),
    "coventry city fc": (1070, "Coventry"),
    "everton": (45, "Everton"),
    "everton fc": (45, "Everton"),
    "nottingham forest": (65, "Nottingham Forest"),
    "nottingham forest fc": (65, "Nottingham Forest"),
    "leeds": (63, "Leeds"),
    "leeds united": (63, "Leeds"),
    "leeds united fc": (63, "Leeds"),
    "manchester united": (33, "Manchester United"),
    "manchester united fc": (33, "Manchester United"),
    "manchester city": (50, "Manchester City"),
    "manchester city fc": (50, "Manchester City"),
    "chelsea": (49, "Chelsea"),
    "chelsea fc": (49, "Chelsea"),
    "liverpool": (40, "Liverpool"),
    "liverpool fc": (40, "Liverpool"),
    "tottenham": (47, "Tottenham"),
    "tottenham hotspur": (47, "Tottenham"),
    "tottenham hotspur fc": (47, "Tottenham"),
    "aston villa": (66, "Aston Villa"),
    "aston villa fc": (66, "Aston Villa"),
    "newcastle": (34, "Newcastle"),
    "newcastle united": (34, "Newcastle"),
    "west ham": (48, "West Ham"),
    "west ham united": (48, "West Ham"),
    "wolves": (39, "Wolves"),
    "wolverhampton wanderers": (39, "Wolves"),
    "brighton": (51, "Brighton"),
    "brighton & hove albion": (51, "Brighton"),
    "fulham": (36, "Fulham"),
    "brentford": (55, "Brentford"),
    "bournemouth": (35, "Bournemouth"),
    "crystal palace": (52, "Crystal Palace"),
    "leicester": (46, "Leicester"),
    "leicester city": (46, "Leicester"),
    "southampton": (41, "Southampton"),
    "ipswich": (1079, "Ipswich"),
    "ipswich town": (1079, "Ipswich"),
    "sunderland": (746, "Sunderland"),
}


def clean_team_name(team_name: str) -> str:
    """Strips common suffixes and normalizes team names."""
    clean = team_name.strip()
    for suffix in [" AFC", " FC", " Football Club", " Club", " FC."]:
        if clean.lower().endswith(suffix.lower()):
            clean = clean[:-len(suffix)].strip()
    return clean


def resolve_team_id(team_name: str):
    """
    Resolves a team name to an API-Football Team ID using a direct lookup table 
    first, falling back to multi-query API search logic if not found.
    """
    normalized = team_name.strip().lower()
    
    # 1. Direct match check
    if normalized in KNOWN_TEAM_IDS:
        return KNOWN_TEAM_IDS[normalized]

    clean = clean_team_name(team_name)
    if clean.lower() in KNOWN_TEAM_IDS:
        return KNOWN_TEAM_IDS[clean.lower()]

    # 2. API-Football Search Fallback
    search_queries = [clean]
    words = clean.split()
    if len(words) > 1 and words[0].lower() not in ["manchester", "sheffield", "west"]:
        search_queries.append(words[0])
    search_queries.append(team_name.strip())

    for query in search_queries:
        if len(query) < 3:
            continue
        try:
            res = requests.get(f"{APIF_BASE}/teams?search={query}", headers=APIF_HEADERS, timeout=10)
            if res.status_code == 200 and res.json().get("response"):
                response_list = res.json()["response"]
                
                # Check for exact name match
                for item in response_list:
                    t_name = item["team"]["name"]
                    if clean.lower() == t_name.lower():
                        return item["team"]["id"], item["team"]["name"]

                # Check for partial match
                for item in response_list:
                    t_name = item["team"]["name"]
                    if clean.lower() in t_name.lower() or t_name.lower() in clean.lower():
                        return item["team"]["id"], item["team"]["name"]

                # Default to first returned result
                return response_list[0]["team"]["id"], response_list[0]["team"]["name"]
        except Exception:
            continue

    return None, None


# -----------------------------------------------------------------------------
# 1. UPCOMING FIXTURES TOOL
# -----------------------------------------------------------------------------
def get_upcoming_fixtures(league="PL", limit=10):
    """Fetches upcoming scheduled matches from Football-Data.org."""
    url = f"{FD_BASE}/competitions/{league}/matches?status=SCHEDULED"
    
    try:
        res = requests.get(url, headers=FD_HEADERS, timeout=10)
        matches = res.json().get("matches", []) if res.status_code == 200 else []

        if not matches:
            fallback_url = f"{FD_BASE}/competitions/{league}/matches"
            res_fb = requests.get(fallback_url, headers=FD_HEADERS, timeout=10)
            if res_fb.status_code == 200:
                all_matches = res_fb.json().get("matches", [])
                matches = [m for m in all_matches if m.get("status") in ["SCHEDULED", "TIMED", "POSTPONED"]]

        upcoming_slice = matches[:limit]

        return [
            {
                "id": m.get("id"),
                "home_team": clean_team_name(m.get("homeTeam", {}).get("name", "")),
                "away_team": clean_team_name(m.get("awayTeam", {}).get("name", "")),
                "utc_date": m.get("utcDate")
            }
            for m in upcoming_slice
        ]

    except Exception as e:
        return {"error": f"Exception fetching upcoming fixtures: {str(e)}"}


# -----------------------------------------------------------------------------
# 2. LAST 5 MATCHES STATS TOOL
# -----------------------------------------------------------------------------
def get_team_last_5_matches(team_name: str):
    """Retrieves form, results, goals, and clean sheets from the last 5 matches for a team."""
    team_id, official_name = resolve_team_id(team_name)
    if not team_id:
        return {"error": f"Team '{team_name}' could not be resolved."}

    url = f"{APIF_BASE}/fixtures?team={team_id}&last=5"
    try:
        res = requests.get(url, headers=APIF_HEADERS, timeout=10)
        if res.status_code != 200 or not res.json().get("response"):
            return {"error": f"No recent match data found for {official_name}."}

        raw_fixtures = res.json()["response"]
        match_history = []
        wins = 0
        draws = 0
        losses = 0
        goals_scored = 0
        goals_conceded = 0
        clean_sheets = 0
        failed_to_score = 0

        for f in raw_fixtures:
            home_id = f.get("teams", {}).get("home", {}).get("id")
            home_name = f.get("teams", {}).get("home", {}).get("name")
            away_name = f.get("teams", {}).get("away", {}).get("name")
            
            g_home = f.get("goals", {}).get("home", 0) or 0
            g_away = f.get("goals", {}).get("away", 0) or 0

            is_home = (home_id == team_id)
            team_score = g_home if is_home else g_away
            opp_score = g_away if is_home else g_home
            opp_name = away_name if is_home else home_name

            if team_score > opp_score:
                result = "WIN"
                wins += 1
            elif team_score == opp_score:
                result = "DRAW"
                draws += 1
            else:
                result = "LOSS"
                losses += 1

            goals_scored += team_score
            goals_conceded += opp_score

            if opp_score == 0:
                clean_sheets += 1
            if team_score == 0:
                failed_to_score += 1

            match_history.append({
                "date": f.get("fixture", {}).get("date", "")[:10],
                "competition": f.get("league", {}).get("name"),
                "venue": "Home" if is_home else "Away",
                "opponent": opp_name,
                "score": f"{g_home}-{g_away}",
                "outcome": result
            })

        total_played = len(raw_fixtures)
        return {
            "team": official_name,
            "last_5_summary": {
                "matches_played": total_played,
                "record": f"{wins}W - {draws}D - {losses}L",
                "total_goals_scored": goals_scored,
                "total_goals_conceded": goals_conceded,
                "avg_goals_scored_per_game": round(goals_scored / max(1, total_played), 2),
                "avg_goals_conceded_per_game": round(goals_conceded / max(1, total_played), 2),
                "clean_sheets": clean_sheets,
                "failed_to_score": failed_to_score
            },
            "recent_matches": match_history
        }

    except Exception as e:
        return {"error": f"Error fetching last 5 matches for {official_name}: {str(e)}"}


# -----------------------------------------------------------------------------
# 3. HEAD-TO-HEAD (LAST 5 MEETINGS) TOOL
# -----------------------------------------------------------------------------
def get_head_to_head_last_5(team1_name: str, team2_name: str):
    """Retrieves the last 5 head-to-head match results between two teams."""
    t1_id, t1_official = resolve_team_id(team1_name)
    t2_id, t2_official = resolve_team_id(team2_name)

    if not t1_id:
        return {"error": f"Team '{team1_name}' not found."}
    if not t2_id:
        return {"error": f"Team '{team2_name}' not found."}

    h2h_url = f"{APIF_BASE}/fixtures/headtohead?h2h={t1_id}-{t2_id}&last=5"
    try:
        res = requests.get(h2h_url, headers=APIF_HEADERS, timeout=10)
        
        if res.status_code != 200 or not res.json().get("response"):
            return {
                "teams": [t1_official, t2_official],
                "h2h_summary": "No recent head-to-head meetings recorded.",
                "last_5_meetings": []
            }

        fixtures = res.json()["response"]
        history = []
        t1_wins = 0
        t2_wins = 0
        draws = 0

        for f in fixtures:
            league_name = f.get("league", {}).get("name")
            match_date = f.get("fixture", {}).get("date", "")[:10]
            home_id = f.get("teams", {}).get("home", {}).get("id")
            home_name = f.get("teams", {}).get("home", {}).get("name")
            away_name = f.get("teams", {}).get("away", {}).get("name")
            goals_home = f.get("goals", {}).get("home", 0) or 0
            goals_away = f.get("goals", {}).get("away", 0) or 0

            if goals_home == goals_away:
                draws += 1
            elif (home_id == t1_id and goals_home > goals_away) or (home_id != t1_id and goals_away > goals_home):
                t1_wins += 1
            else:
                t2_wins += 1

            history.append({
                "date": match_date,
                "competition": league_name,
                "match": f"{home_name} {goals_home} - {goals_away} {away_name}"
            })

        return {
            "teams": [t1_official, t2_official],
            "h2h_summary": {
                "total_meetings": len(history),
                f"{t1_official}_wins": t1_wins,
                f"{t2_official}_wins": t2_wins,
                "draws": draws
            },
            "last_5_meetings": history
        }
    except Exception as e:
        return {"error": f"Error fetching H2H history: {str(e)}"}


# -----------------------------------------------------------------------------
# 4. OPENAI TOOL SCHEMAS & MAPPINGS
# -----------------------------------------------------------------------------
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_fixtures",
            "description": "Retrieves upcoming scheduled match fixtures.",
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
            "name": "get_team_last_5_matches",
            "description": "Retrieves form, results, goals, clean sheets, and scorelines from the last 5 matches for a team.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_name": {"type": "string", "description": "Football team name e.g. Arsenal, Everton, Coventry City"}
                },
                "required": ["team_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_head_to_head_last_5",
            "description": "Retrieves the last 5 head-to-head match results between two football teams.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team1_name": {"type": "string", "description": "First team name"},
                    "team2_name": {"type": "string", "description": "Second team name"}
                },
                "required": ["team1_name", "team2_name"]
            }
        }
    }
]

TOOL_MAPPING = {
    "get_upcoming_fixtures": get_upcoming_fixtures,
    "get_team_last_5_matches": get_team_last_5_matches,
    "get_head_to_head_last_5": get_head_to_head_last_5
}
