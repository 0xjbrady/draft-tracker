"""Unit tests for odds scraper."""
import time
import asyncio
import pytest
from app.scrapers.odds_scraper import OddsScraper

@pytest.fixture
def scraper():
    """Create a scraper instance with mock data enabled."""
    return OddsScraper(use_mock=True)

@pytest.mark.asyncio
async def test_get_all_odds(scraper):
    """Test fetching all odds."""
    odds = await scraper.get_all_odds()
    assert len(odds) > 0
    
    # Check structure of odds entries
    for entry in odds:
        assert "player_name" in entry
        assert "market_type" in entry
        assert "odds" in entry
        assert "draft_position" in entry
        assert "sportsbook" in entry
        assert "timestamp" in entry
        
        # Verify data types
        assert isinstance(entry["player_name"], str)
        assert isinstance(entry["market_type"], str)
        assert isinstance(entry["odds"], (int, type(None)))
        assert isinstance(entry["draft_position"], (float, type(None)))
        assert isinstance(entry["sportsbook"], str)
        assert isinstance(entry["timestamp"], (int, float))

@pytest.mark.asyncio
async def test_odds_variation_over_time(scraper):
    """Test that odds vary over time."""
    # Get odds at different times
    current_time = int(time.time())
    odds1 = await scraper.get_nfl_draft_odds()
    
    # Wait a bit to ensure time difference
    await asyncio.sleep(1)
    
    odds2 = await scraper.get_nfl_draft_odds()
    
    # Helper function to get odds for a specific player
    def get_player_odds(odds_list, player_name, sportsbook):
        return next(
            (entry["odds"] for entry in odds_list 
             if entry["player_name"] == player_name 
             and entry["sportsbook"] == sportsbook),
            None
        )
    
    # Check odds for Caleb Williams from DraftKings
    odds1_cw = get_player_odds(odds1, "Caleb Williams", "DraftKings")
    odds2_cw = get_player_odds(odds2, "Caleb Williams", "DraftKings")
    
    assert odds1_cw is not None
    assert odds2_cw is not None
    assert odds1_cw != odds2_cw  # Odds should vary

@pytest.mark.asyncio
async def test_bookmaker_consistency(scraper):
    """Test that bookmaker odds maintain consistent relationships."""
    odds = await scraper.get_nfl_draft_odds()
    
    # Group odds by player and draft position
    player_odds = {}
    for entry in odds:
        key = (entry["player_name"], entry["draft_position"])
        if key not in player_odds:
            player_odds[key] = {}
        player_odds[key][entry["sportsbook"]] = entry["odds"]
    
    # Check relationships between bookmakers
    for odds_dict in player_odds.values():
        if "DraftKings" in odds_dict and "FanDuel" in odds_dict and "BetMGM" in odds_dict:
            dk_odds = odds_dict["DraftKings"]
            fd_odds = odds_dict["FanDuel"]
            mgm_odds = odds_dict["BetMGM"]
            
            # For positive odds (underdogs), higher odds mean better value
            if dk_odds > 0:
                assert fd_odds > dk_odds, "FanDuel should offer better odds for underdogs"
                assert mgm_odds < dk_odds, "BetMGM should offer worse odds for underdogs"
            # For negative odds (favorites), lower absolute value means better odds
            else:
                assert abs(fd_odds) < abs(dk_odds), "FanDuel should offer better odds for favorites"
                assert abs(mgm_odds) > abs(dk_odds), "BetMGM should offer worse odds for favorites"

@pytest.mark.asyncio
async def test_draft_position_consistency(scraper):
    """Test that draft positions are consistent with market types."""
    odds = await scraper.get_nfl_draft_odds()
    
    for entry in odds:
        if "Pick" in entry["market_type"]:
            position = entry["draft_position"]
            assert position is not None
            assert 1 <= position <= 10  # Should be within first 10 picks
            assert f"Pick {int(position)}" in entry["market_type"]

@pytest.mark.asyncio
async def test_timestamp_consistency(scraper):
    """Test that timestamps are recent and consistent."""
    odds = await scraper.get_nfl_draft_odds()
    current_time = time.time()
    
    for entry in odds:
        timestamp = entry["timestamp"]
        # Timestamp should be within the last minute
        assert current_time - timestamp < 60
        # Timestamp should not be in the future
        assert timestamp <= current_time 