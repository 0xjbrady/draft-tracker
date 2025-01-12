"""Unit tests for the odds scheduler."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from app.scheduler.odds_scheduler import OddsScheduler
from app.models import crud
from tests.data.draftkings_responses import EXPECTED_PARSED_ODDS

@pytest.fixture
def scheduler():
    return OddsScheduler()

@pytest.mark.asyncio
async def test_update_odds_success(scheduler):
    """Test successful odds update."""
    # Mock the scraper response
    mock_odds = EXPECTED_PARSED_ODDS.copy()
    for odds in mock_odds:
        odds['timestamp'] = datetime.now().timestamp()
    
    # Mock dependencies
    mock_scraper = AsyncMock()
    mock_scraper.get_all_odds.return_value = mock_odds
    scheduler.scraper = mock_scraper
    
    mock_session = MagicMock()
    mock_player = MagicMock()
    mock_player.id = 1
    
    with patch('app.models.crud.get_player_by_name', return_value=mock_player), \
         patch('app.models.crud.create_odds') as mock_create_odds, \
         patch('app.models.database.get_db', return_value=iter([mock_session])):
        
        await scheduler.update_odds()
        
        # Verify that create_odds was called for each odds entry
        assert mock_create_odds.call_count == len(mock_odds)

@pytest.mark.asyncio
async def test_update_odds_new_player(scheduler):
    """Test odds update with new player creation."""
    # Mock the scraper response
    mock_odds = [EXPECTED_PARSED_ODDS[0].copy()]
    mock_odds[0]['timestamp'] = datetime.now().timestamp()
    
    # Mock dependencies
    mock_scraper = AsyncMock()
    mock_scraper.get_all_odds.return_value = mock_odds
    scheduler.scraper = mock_scraper
    
    mock_session = MagicMock()
    mock_player = MagicMock()
    mock_player.id = 1
    
    with patch('app.models.crud.get_player_by_name', return_value=None), \
         patch('app.models.crud.create_player', return_value=mock_player) as mock_create_player, \
         patch('app.models.crud.create_odds') as mock_create_odds, \
         patch('app.models.database.get_db', return_value=iter([mock_session])):
        
        await scheduler.update_odds()
        
        # Verify player was created
        mock_create_player.assert_called_once()
        # Verify odds were created
        mock_create_odds.assert_called_once()

@pytest.mark.asyncio
async def test_update_odds_scraper_error(scheduler):
    """Test handling of scraper errors."""
    # Mock scraper to raise an exception
    mock_scraper = AsyncMock()
    mock_scraper.get_all_odds.side_effect = Exception("Scraper error")
    scheduler.scraper = mock_scraper
    
    mock_session = MagicMock()
    
    with patch('app.models.database.get_db', return_value=iter([mock_session])):
        await scheduler.update_odds()
        # Test should complete without raising an exception

def test_scheduler_start(scheduler):
    """Test scheduler job configuration."""
    with patch('apscheduler.schedulers.asyncio.AsyncIOScheduler.add_job') as mock_add_job, \
         patch('apscheduler.schedulers.asyncio.AsyncIOScheduler.start') as mock_start:
        
        scheduler.start()
        
        # Verify that three jobs were added (regular, peak hours, and draft day)
        assert mock_add_job.call_count == 3
        # Verify scheduler was started
        mock_start.assert_called_once() 