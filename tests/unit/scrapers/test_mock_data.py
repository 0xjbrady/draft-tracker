"""Unit tests for mock data generator."""
import time
from datetime import datetime, timedelta
import pytest
from app.scrapers.mock_data import (
    get_mock_sports,
    get_mock_draft_odds,
    _apply_time_based_variation,
    _apply_news_impact,
    _get_adjusted_prospects,
    MOCK_NEWS_EVENTS
)

def test_get_mock_sports():
    """Test mock sports list generation."""
    sports = get_mock_sports()
    assert len(sports) == 1
    sport = sports[0]
    assert sport["key"] == "americanfootball_nfl_draft"
    assert "NFL Draft 2024" in sport["title"]
    assert sport["active"] is True
    assert sport["has_outrights"] is True

def test_get_mock_draft_odds_structure():
    """Test structure of mock draft odds data."""
    odds = get_mock_draft_odds()
    assert len(odds) == 10  # 10 draft positions
    
    # Check first event structure
    event = odds[0]
    assert "id" in event
    assert "sport_key" in event
    assert "sport_title" in event
    assert "commence_time" in event
    assert "bookmakers" in event
    
    # Check bookmaker structure
    bookmaker = event["bookmakers"][0]
    assert "key" in bookmaker
    assert "title" in bookmaker
    assert "markets" in bookmaker
    assert len(bookmaker["markets"]) == 1
    
    # Check market structure
    market = bookmaker["markets"][0]
    assert market["key"] == "outrights"
    assert "outcomes" in market
    assert len(market["outcomes"]) > 0
    
    # Check outcome structure
    outcome = market["outcomes"][0]
    assert "name" in outcome
    assert "price" in outcome
    assert isinstance(outcome["price"], float)

def test_time_based_variations():
    """Test that odds vary over time."""
    current_time = int(time.time())
    base_odds = 100
    
    # Test variations at different times
    variations = set()
    for hour in range(24):
        test_time = current_time + (hour * 3600)
        varied_odds = _apply_time_based_variation(base_odds, test_time)
        variations.add(varied_odds)
    
    # Should have multiple different values due to time-based variation
    assert len(variations) > 1
    # Variations should be within ±20 of base odds
    assert all(abs(v - base_odds) <= 20 for v in variations)

def test_news_impact():
    """Test that news events affect odds appropriately."""
    current_time = int(time.time())
    base_odds = -300
    player = "Caleb Williams"
    
    # Test immediate impact
    for event in MOCK_NEWS_EVENTS:
        if player in event["impact"]:
            odds_at_event = _apply_news_impact(player, base_odds, event["timestamp"])
            expected_impact = event["impact"][player]
            assert abs(odds_at_event - base_odds) == abs(expected_impact)
            
            # Test decay over time
            odds_after_decay = _apply_news_impact(
                player, 
                base_odds,
                event["timestamp"] + 86400  # 1 day later
            )
            assert abs(odds_after_decay - base_odds) < abs(expected_impact)

def test_odds_consistency():
    """Test that odds remain within realistic bounds."""
    prospects = _get_adjusted_prospects(int(time.time()))
    
    for _, _, odds in prospects:
        if odds > 0:
            assert odds <= 2000  # Check positive odds cap
        else:
            assert odds >= -1000  # Check negative odds cap

def test_bookmaker_variations():
    """Test that different bookmakers offer slightly different odds."""
    odds = get_mock_draft_odds()
    event = odds[0]
    
    # Get odds from different bookmakers for the same outcome
    bookmaker_prices = {}
    for bookmaker in event["bookmakers"]:
        outcome = bookmaker["markets"][0]["outcomes"][0]
        bookmaker_prices[bookmaker["title"]] = outcome["price"]
    
    # Verify FanDuel has slightly higher odds than DraftKings
    assert bookmaker_prices["FanDuel"] > bookmaker_prices["DraftKings"]
    # Verify BetMGM has slightly lower odds than DraftKings
    assert bookmaker_prices["BetMGM"] < bookmaker_prices["DraftKings"]

def test_temporal_consistency():
    """Test that odds changes are consistent over time."""
    # Get odds at three points in time
    time1 = int(time.time())
    time2 = time1 + 3600  # 1 hour later
    time3 = time2 + 3600  # 2 hours later
    
    odds1 = get_mock_draft_odds(time1)
    odds2 = get_mock_draft_odds(time2)
    odds3 = get_mock_draft_odds(time3)
    
    # Helper function to get first outcome price
    def get_first_price(odds):
        return odds[0]["bookmakers"][0]["markets"][0]["outcomes"][0]["price"]
    
    # Verify that changes are smooth (no extreme jumps)
    price1 = get_first_price(odds1)
    price2 = get_first_price(odds2)
    price3 = get_first_price(odds3)
    
    # Changes should be relatively small between consecutive hours
    assert abs(price2 - price1) < 0.5
    assert abs(price3 - price2) < 0.5 