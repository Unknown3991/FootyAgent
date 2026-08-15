# mock_data.py

MOCK_MATCH_DATA = {
    "fixture": {
        "home_team": "West Ham",
        "away_team": "Everton",
        "league": "Premier League",
        "kickoff": "Sunday, 15:00 UTC",
        "venue": "London Stadium"
    },
    "home_stats": {
        "team": "West Ham",
        "record_last_5": "5W - 0D - 0L",
        "recent_outcomes": ["WIN", "WIN", "WIN", "WIN", "WIN"],
        "goals_scored_avg": 2.2,
        "goals_conceded_avg": 1.2,
        "clean_sheets": 0,
        "avg_corners_overall": 7.0,
        "avg_corners_home": 6.0,
        "avg_xg": 1.85
    },
    "away_stats": {
        "team": "Everton",
        "record_last_5": "2W - 1D - 2L",
        "recent_outcomes": ["WIN", "LOSS", "DRAW", "WIN", "LOSS"],
        "goals_scored_avg": 1.1,
        "goals_conceded_avg": 1.4,
        "clean_sheets": 1,
        "avg_corners_overall": 4.5,
        "avg_corners_away": 4.0,
        "avg_xg": 1.20
    },
    "player_props": [
        {
            "name": "Jarrod Bowen",
            "team": "West Ham",
            "position": "FW",
            "goals_last_5": 3,
            "shots_on_target_last_5": 8,
            "avg_shots_per_game": 2.6
        },
        {
            "name": "Mohammed Kudus",
            "team": "West Ham",
            "position": "FW",
            "goals_last_5": 2,
            "shots_on_target_last_5": 6,
            "avg_shots_per_game": 2.1
        },
        {
            "name": "Dominic Calvert-Lewin",
            "team": "Everton",
            "position": "FW",
            "goals_last_5": 2,
            "shots_on_target_last_5": 5,
            "avg_shots_per_game": 1.9
        }
    ],
    "bet_builder_tiers": {
        "high_confidence": {
            "title": "🟢 High Confidence (Anchor)",
            "selection": "Both Teams To Score (BTTS - Yes)",
            "odds": "1.72",
            "reasoning": "West Ham have won their last 5 matches but conceded in every single game. Everton have scored in 4 of their last 5."
        },
        "medium_confidence": {
            "title": "🟡 Medium Confidence (Value)",
            "selection": "Jarrod Bowen 1+ Shot on Target & West Ham Over 4.5 Corners",
            "odds": "2.10",
            "reasoning": "Bowen has 8 shots on target in his last 5 appearances. West Ham average 6.0 corners per game at home."
        },
        "high_yield": {
            "title": "🔴 High Yield (Longshot Builder)",
            "selection": "West Ham Win + BTTS + Bowen Anytime Goalscorer",
            "odds": "4.50",
            "reasoning": "Combines West Ham's 5-match winning streak with their continuous lack of clean sheets and Bowen's recent scoring form (3 goals in 5 games)."
        }
    }
}
