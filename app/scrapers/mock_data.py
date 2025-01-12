"""Mock data generator for NFL Draft odds testing."""
import time
import math
import random
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

# Mock news events that could affect odds
MOCK_NEWS_EVENTS = [
    {
        "timestamp": int(time.time()) - 86400 * 5,  # 5 days ago
        "event": "Caleb Williams Pro Day",
        "impact": {"Caleb Williams": -50}  # Odds shortened (became more favorable)
    },
    {
        "timestamp": int(time.time()) - 86400 * 3,  # 3 days ago
        "event": "Drake Maye Team Visit",
        "impact": {"Drake Maye": -30}
    },
    {
        "timestamp": int(time.time()) - 86400 * 2,  # 2 days ago
        "event": "Jayden Daniels Heisman Ceremony",
        "impact": {"Jayden Daniels": -100}
    }
]

def get_mock_sports() -> List[Dict]:
    """Generate mock sports list including NFL Draft."""
    return [
        {
            "key": "americanfootball_nfl_draft",
            "group": "American Football",
            "title": "NFL Draft 2024",
            "description": "NFL Draft Odds",
            "active": True,
            "has_outrights": True
        }
    ]

def _get_base_prospects() -> List[Tuple[str, int, int]]:
    """Get base prospects data with initial odds."""
    return [
        ("Caleb Williams", 1, -300),  # Heavy favorite for #1
        ("Drake Maye", 2, -150),
        ("Marvin Harrison Jr.", 3, -110),
        ("Malik Nabers", 4, +150),
        ("Joe Alt", 5, +200),
        ("Brock Bowers", 6, +250),
        ("Jayden Daniels", 7, +300),
        ("Rome Odunze", 8, +350),
        ("Dallas Turner", 9, +400),
        ("Jared Verse", 10, +450)
    ]

def _apply_time_based_variation(base_odds: int, current_time: int) -> int:
    """Apply time-based variation to odds."""
    # Create a sine wave variation with a period of 1 week
    time_factor = math.sin(2 * math.pi * ((current_time % (86400 * 7)) / (86400 * 7)))
    variation = int(time_factor * 20)  # Vary by up to ±20
    return base_odds + variation

def _apply_news_impact(player_name: str, base_odds: int, current_time: int) -> int:
    """Apply impact of news events to odds."""
    total_impact = 0
    for event in MOCK_NEWS_EVENTS:
        if current_time >= event["timestamp"] and player_name in event["impact"]:
            # Impact decays over time (3 days to return to normal)
            time_since_event = current_time - event["timestamp"]
            decay_factor = max(0, 1 - (time_since_event / (86400 * 3)))
            total_impact += int(event["impact"][player_name] * decay_factor)
    return base_odds + total_impact

def _apply_random_variation(odds: int) -> int:
    """Apply small random variations to odds."""
    variation = random.randint(-10, 10)
    return odds + variation

def _apply_bookmaker_variation(base_price, bookmaker):
    """Apply bookmaker-specific variations to the base price."""
    if base_price > 0:
        # For positive odds (underdogs), higher odds mean better value
        if bookmaker == "FanDuel":
            return base_price * 1.02  # FanDuel offers slightly better odds
        elif bookmaker == "BetMGM":
            return base_price * 0.98  # BetMGM offers slightly worse odds
    else:
        # For negative odds (favorites), lower absolute value means better odds
        if bookmaker == "FanDuel":
            return base_price * 0.98  # FanDuel offers slightly better odds
        elif bookmaker == "BetMGM":
            return base_price * 1.02  # BetMGM offers slightly worse odds
    
    # DraftKings is our baseline
    return base_price

def _get_adjusted_prospects(current_time: int) -> List[Tuple[str, int, int]]:
    """Get prospects with odds adjusted for time and events."""
    base_prospects = _get_base_prospects()
    adjusted_prospects = []
    
    for player, position, base_odds in base_prospects:
        # Apply various adjustments
        odds = base_odds
        odds = _apply_time_based_variation(odds, current_time)
        odds = _apply_news_impact(player, odds, current_time)
        odds = _apply_random_variation(odds)
        
        # Ensure odds stay within realistic bounds
        if odds > 0:
            odds = min(odds, 2000)  # Cap positive odds
        else:
            odds = max(odds, -1000)  # Cap negative odds
            
        adjusted_prospects.append((player, position, odds))
    
    return adjusted_prospects

def get_mock_draft_odds(current_time: int = None) -> List[Dict]:
    """Get mock NFL Draft odds data."""
    if current_time is None:
        current_time = int(time.time())
    
    prospects = _get_adjusted_prospects(current_time)
    odds_data = []
    
    for pick in range(1, 11):  # First 10 picks
        event_id = f"nfl_draft_2024_pick_{pick}"
        
        bookmakers = []
        for bookmaker in ["DraftKings", "FanDuel", "BetMGM"]:
            outcomes = []
            for name, position, base_odds in prospects:
                if position == pick:
                    # Convert odds to decimal format for consistency
                    decimal_odds = _convert_american_to_decimal(base_odds)
                    # Apply bookmaker-specific variation
                    adjusted_odds = _apply_bookmaker_variation(decimal_odds, bookmaker)
                    
                    outcomes.append({
                        "name": name,
                        "price": adjusted_odds
                    })
            
            if outcomes:  # Only add markets with outcomes
                bookmakers.append({
                    "key": bookmaker.lower(),
                    "title": bookmaker,
                    "markets": [{
                        "key": "outrights",
                        "outcomes": outcomes
                    }]
                })
        
        if bookmakers:  # Only add events with bookmakers
            odds_data.append({
                "id": event_id,
                "sport_key": "americanfootball_nfl_draft",
                "sport_title": "NFL Draft 2024",
                "commence_time": current_time + 86400,  # 24 hours from now
                "bookmakers": bookmakers
            })
    
    return odds_data

def _convert_american_to_decimal(american_odds: int) -> float:
    """Convert American odds to decimal format."""
    if american_odds > 0:
        return 1 + (american_odds / 100)
    else:
        return 1 + (100 / abs(american_odds)) 