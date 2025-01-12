"""Unit tests for the odds analyzer."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import pandas as pd
import plotly.graph_objects as go

from app.analysis.odds_analysis import OddsAnalyzer

@pytest.fixture
def mock_odds_data():
    """Create mock odds data for testing."""
    player = MagicMock()
    player.name = "Caleb Williams"
    
    odds1 = MagicMock()
    odds1.player = player
    odds1.odds = "+150"
    odds1.draft_position = 1.5
    odds1.sportsbook = "DraftKings"
    odds1.market_type = "Draft Position Over/Under"
    odds1.timestamp = datetime.now() - timedelta(days=1)
    
    odds2 = MagicMock()
    odds2.player = player
    odds2.odds = "-180"
    odds2.draft_position = 1.5
    odds2.sportsbook = "DraftKings"
    odds2.market_type = "Draft Position Over/Under"
    odds2.timestamp = datetime.now()
    
    return [odds1, odds2]

@pytest.fixture
def analyzer():
    """Create an OddsAnalyzer instance."""
    with patch('app.models.database.SessionLocal') as mock_session:
        return OddsAnalyzer()

def test_get_player_odds_history(analyzer, mock_odds_data):
    """Test retrieving player odds history."""
    with patch('app.models.crud.get_player_odds_history', return_value=mock_odds_data):
        df = analyzer.get_player_odds_history("Caleb Williams")
        
        assert not df.empty
        assert len(df) == 2
        assert list(df.columns) == ['timestamp', 'odds', 'draft_position', 'sportsbook', 'market_type']
        assert df['odds'].tolist() == ['+150', '-180']

def test_get_player_odds_history_empty(analyzer):
    """Test handling empty odds history."""
    with patch('app.models.crud.get_player_odds_history', return_value=[]):
        df = analyzer.get_player_odds_history("Nonexistent Player")
        assert df.empty

def test_create_odds_movement_chart(analyzer, mock_odds_data):
    """Test creating odds movement chart."""
    with patch('app.models.crud.get_player_odds_history', return_value=mock_odds_data):
        fig = analyzer.create_odds_movement_chart("Caleb Williams")
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == 'Odds Movement for Caleb Williams'
        assert len(fig.data) == 1  # One line for the market type

def test_create_odds_movement_chart_empty(analyzer):
    """Test handling empty data for chart creation."""
    with patch('app.models.crud.get_player_odds_history', return_value=[]):
        fig = analyzer.create_odds_movement_chart("Nonexistent Player")
        assert fig is None

def test_get_consensus_rankings(analyzer, mock_odds_data):
    """Test calculating consensus rankings."""
    with patch('app.models.crud.get_latest_odds_all_players', return_value=mock_odds_data):
        rankings = analyzer.get_consensus_rankings()
        
        assert not rankings.empty
        assert len(rankings) == 1  # One player
        assert list(rankings.columns) == ['Consensus Position', 'Standard Deviation', 'Number of Markets']
        assert rankings.index[0] == "Caleb Williams"

def test_get_consensus_rankings_empty(analyzer):
    """Test handling empty data for rankings."""
    with patch('app.models.crud.get_latest_odds_all_players', return_value=[]):
        rankings = analyzer.get_consensus_rankings()
        assert rankings.empty

def test_create_draft_board_visualization(analyzer, mock_odds_data):
    """Test creating draft board visualization."""
    with patch('app.models.crud.get_latest_odds_all_players', return_value=mock_odds_data):
        fig = analyzer.create_draft_board_visualization()
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == 'NFL Draft Consensus Board'
        assert len(fig.data) == 3  # Main points and two traces for error bars

def test_create_draft_board_visualization_empty(analyzer):
    """Test handling empty data for draft board."""
    with patch('app.models.crud.get_latest_odds_all_players', return_value=[]):
        fig = analyzer.create_draft_board_visualization()
        assert fig is None 