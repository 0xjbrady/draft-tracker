from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..models.database import DraftOdds, get_db
import pandas as pd

router = APIRouter()

@router.get("/odds/current")
async def get_current_odds(
    db: Session = Depends(get_db),
    sportsbook: Optional[str] = None,
    player_name: Optional[str] = None
):
    """Get the most recent odds for all players or a specific player."""
    query = db.query(DraftOdds)
    
    if player_name:
        query = query.filter(DraftOdds.player_name == player_name)
    if sportsbook:
        query = query.filter(DraftOdds.sportsbook == sportsbook)
    
    # Get the most recent timestamp
    latest_time = query.order_by(DraftOdds.timestamp.desc()).first().timestamp
    
    # Get odds from the latest timestamp
    latest_odds = query.filter(DraftOdds.timestamp == latest_time).all()
    
    return latest_odds

@router.get("/odds/historical")
async def get_historical_odds(
    player_name: str,
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365),
    sportsbook: Optional[str] = None
):
    """Get historical odds data for a specific player."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(DraftOdds).filter(
        DraftOdds.player_name == player_name,
        DraftOdds.timestamp >= start_date
    )
    
    if sportsbook:
        query = query.filter(DraftOdds.sportsbook == sportsbook)
    
    historical_odds = query.order_by(DraftOdds.timestamp.asc()).all()
    
    return historical_odds

@router.get("/odds/movement")
async def get_odds_movement(
    db: Session = Depends(get_db),
    days: int = Query(default=7, ge=1, le=30)
):
    """Get the biggest odds movements in the past X days."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all odds data for the time period
    odds_data = db.query(DraftOdds).filter(
        DraftOdds.timestamp >= start_date
    ).all()
    
    # Convert to pandas DataFrame for easier analysis
    df = pd.DataFrame([{
        'player_name': odd.player_name,
        'odds': odd.odds,
        'timestamp': odd.timestamp,
        'sportsbook': odd.sportsbook
    } for odd in odds_data])
    
    if df.empty:
        return []
    
    # Calculate odds movement
    movements = []
    for player in df['player_name'].unique():
        player_data = df[df['player_name'] == player]
        for book in player_data['sportsbook'].unique():
            book_data = player_data[player_data['sportsbook'] == book].sort_values('timestamp')
            if len(book_data) >= 2:
                start_odds = book_data.iloc[0]['odds']
                end_odds = book_data.iloc[-1]['odds']
                movement = end_odds - start_odds
                movements.append({
                    'player_name': player,
                    'sportsbook': book,
                    'start_odds': start_odds,
                    'end_odds': end_odds,
                    'movement': movement
                })
    
    # Sort by absolute movement
    movements.sort(key=lambda x: abs(x['movement']), reverse=True)
    
    return movements[:10]  # Return top 10 movements 