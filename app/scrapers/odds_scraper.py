"""Scraper for fetching NFL Draft odds data."""
import os
import time
import logging
import httpx
from typing import List, Dict, Optional
from dotenv import load_dotenv

from ..cache.odds_cache import OddsCache
from . import mock_data
from ..monitoring.metrics import (
    ODDS_SCRAPING_DURATION,
    ODDS_SCRAPING_FAILURES,
    ODDS_SCRAPING_SUCCESS,
    ODDS_ENTRIES_COUNT,
)

# Load environment variables
load_dotenv()

class OddsScraper:
    def __init__(self, use_mock: bool = None, cache_duration: int = 300):
        """Initialize the odds scraper.
        
        Args:
            use_mock: Whether to use mock data instead of real API. If None, defaults to True if ENVIRONMENT is development
            cache_duration: How long to cache odds data in seconds
        """
        self.api_key = os.getenv("ODDS_API_KEY")
        self.api_base_url = "https://api.the-odds-api.com/v4"
        
        # Default to mock data in development
        if use_mock is None:
            use_mock = os.getenv("ENVIRONMENT", "development").lower() == "development"
        self.use_mock = use_mock
        
        self.cache = OddsCache(cache_duration=cache_duration)
        
        if use_mock:
            logging.info("OddsScraper initialized with mock data")
        else:
            if not self.api_key:
                raise ValueError("ODDS_API_KEY environment variable not set")
            logging.info("OddsScraper initialized with API key")

    async def _make_request(self, endpoint: str, extra_params: Dict = None) -> Dict:
        """Make a rate-limited request to The Odds API."""
        if not self.cache.can_make_request():
            raise Exception("Rate limit exceeded or too many requests")

        url = f"{self.api_base_url}/{endpoint}"
        params = {"apiKey": self.api_key}
        if extra_params:
            params.update(extra_params)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            
            # Update API limits from headers
            remaining = int(response.headers.get("x-requests-remaining", 0))
            used = int(response.headers.get("x-requests-used", 0))
            self.cache.update_api_limits(remaining, used)
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Request failed with status {response.status_code}")
                raise Exception(f"API request failed: {response.text}")

    def _transform_odds_data(self, raw_odds: List[Dict]) -> List[Dict]:
        """Transform raw odds data into the format expected by our database."""
        transformed_odds = []
        current_time = int(time.time())
        
        def decimal_to_american(decimal_odds: float) -> str:
            """Convert decimal odds to American format."""
            if decimal_odds >= 2.0:
                american = round((decimal_odds - 1) * 100)
                return f"+{american}"
            else:
                american = round(-100 / (decimal_odds - 1))
                return str(american)
        
        for event in raw_odds:
            pick_num = int(event["id"].split("_")[-1])
            for bookmaker in event["bookmakers"]:
                for market in bookmaker["markets"]:
                    for outcome in market["outcomes"]:
                        transformed_odds.append({
                            "player_name": outcome["name"],
                            "odds": decimal_to_american(float(outcome["price"])),
                            "sportsbook": bookmaker["title"],
                            "market_type": "draft_position",
                            "draft_position": pick_num,
                            "timestamp": current_time
                        })
        
        return transformed_odds

    async def get_nfl_draft_odds(self) -> List[Dict]:
        """Fetch NFL Draft odds from configured sportsbooks."""
        start_time = time.time()
        sport_key = "americanfootball_nfl_draft"
        
        try:
            odds_data = []
            if self.use_mock:
                raw_odds = mock_data.get_mock_draft_odds()
                odds_data = self._transform_odds_data(raw_odds)
                ODDS_SCRAPING_SUCCESS.inc()
                ODDS_ENTRIES_COUNT.set(len(odds_data))
            else:
                # Check cache first
                cached_odds = self.cache.get_cached_odds(sport_key)
                if cached_odds is not None:
                    logging.info("Using cached NFL Draft odds")
                    return self._transform_odds_data(cached_odds)

                # First get available sports
                sports = await self._make_request("sports")
                draft_sport = next(
                    (s for s in sports if any(key in s["key"].lower() 
                        for key in ["nfl_draft", "nfl_futures", "nfl_specials"])),
                    None
                )
                
                if not draft_sport:
                    logging.warning("No NFL Draft markets found")
                    return []

                # Get odds for the draft
                raw_odds = await self._make_request(
                    f"sports/{draft_sport['key']}/odds",
                    {
                        "regions": "us",
                        "markets": "outrights,futures",
                        "oddsFormat": "decimal",
                        "dateFormat": "unix"
                    }
                )
                
                self.cache.cache_odds(sport_key, raw_odds)
                odds_data = self._transform_odds_data(raw_odds)
                logging.info(f"Successfully fetched {len(odds_data)} NFL Draft odds entries")
                ODDS_SCRAPING_SUCCESS.inc()
                ODDS_ENTRIES_COUNT.set(len(odds_data))
            
            ODDS_SCRAPING_DURATION.observe(time.time() - start_time)
            return odds_data
        except Exception as e:
            ODDS_SCRAPING_FAILURES.inc()
            ODDS_SCRAPING_DURATION.observe(time.time() - start_time)
            logging.error(f"Error fetching NFL Draft odds: {str(e)}")
            # If API fails, try to use slightly expired cache as fallback
            cached_odds = self.cache.get_cached_odds(sport_key)
            if cached_odds is not None:
                logging.warning("Using expired cache as fallback")
                return self._transform_odds_data(cached_odds)
            # If no cache available, use mock data as last resort
            logging.warning("Using mock data as fallback")
            raw_odds = mock_data.get_mock_draft_odds()
            return self._transform_odds_data(raw_odds)

    async def get_all_odds(self) -> List[Dict]:
        """Get all available odds data."""
        return await self.get_nfl_draft_odds() 