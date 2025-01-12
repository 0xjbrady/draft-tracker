"""Module for analyzing NFL Draft odds data."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy.orm import Session
import logging

from ..models import crud
from ..models.database import SessionLocal

class OddsAnalyzer:
    def __init__(self):
        """Initialize the odds analyzer."""
        pass

    def get_player_odds_history(self, player_name: str, days: int = 7) -> pd.DataFrame:
        """Get historical odds data for a player over the specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        with SessionLocal() as db:
            odds_data = crud.get_player_odds_history(db, player_name, cutoff_date)
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame([{
                'timestamp': odds.timestamp,
                'odds': odds.odds,
                'draft_position': odds.draft_position,
                'sportsbook': odds.sportsbook,
                'market_type': odds.market_type
            } for odds in odds_data])
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
            
            return df

    def create_odds_movement_chart(self, player_name: str, days: int = 7) -> Dict:
        """Create chart data showing odds movement over time."""
        df = self.get_player_odds_history(player_name, days)
        
        if df.empty:
            return None
        
        # Convert data to the format expected by the frontend
        chart_data = []
        for _, row in df.iterrows():
            chart_data.append({
                'timestamp': row['timestamp'].isoformat(),
                'value': float(row['odds'].replace('+', '')) if row['odds'].startswith('+') else float(row['odds']),
                'label': f"{row['market_type']} ({row['sportsbook']})"
            })
        
        return {
            'data': chart_data,
            'xAxisLabel': 'Date',
            'yAxisLabel': 'American Odds',
            'title': f'Odds Movement for {player_name}'
        }

    def get_consensus_rankings(self) -> pd.DataFrame:
        """Calculate consensus draft rankings based on current odds."""
        try:
            with SessionLocal() as db:
                # Get latest odds for each player
                latest_odds = crud.get_latest_odds_all_players(db)
                logging.info(f"Retrieved {len(latest_odds)} latest odds entries")
                
                # Convert to DataFrame
                df = pd.DataFrame([{
                    'player_name': odds.player.name if odds.player else 'Unknown',
                    'draft_position': odds.draft_position,
                    'odds': odds.odds,
                    'sportsbook': odds.sportsbook,
                    'market_type': odds.market_type,
                    'timestamp': odds.timestamp
                } for odds in latest_odds])
                
                if df.empty:
                    logging.warning("No odds data available for rankings")
                    return pd.DataFrame()
                
                logging.info(f"Processing rankings for {len(df['player_name'].unique())} players")
                
                # Calculate consensus ranking
                rankings = (df[df['draft_position'].notna()]
                           .groupby('player_name')['draft_position']
                           .agg(['mean', 'std', 'count'])
                           .round(2)
                           .sort_values('mean'))
                
                rankings.columns = ['Consensus Position', 'Standard Deviation', 'Number of Markets']
                logging.info(f"Generated rankings for {len(rankings)} players")
                return rankings
        except Exception as e:
            logging.error(f"Error calculating consensus rankings: {str(e)}")
            raise

    def create_draft_board_visualization(self) -> List[Dict]:
        """Create draft board data for visualization."""
        rankings = self.get_consensus_rankings()
        
        if rankings.empty:
            return None
        
        # Convert data to the format expected by the frontend
        board_data = []
        for player_name, row in rankings.iterrows():
            board_data.append({
                'player_name': player_name,
                'consensus_position': row['Consensus Position'],
                'standard_deviation': row['Standard Deviation']
            })
        
        return board_data 