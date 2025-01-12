"""CRUD operations for the database."""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from sqlalchemy.sql import text
from sqlalchemy.orm import joinedload

from ..models.models import Player, Odds

def get_player_by_name(db: Session, name: str) -> Optional[Player]:
    """Get a player by name."""
    return db.query(Player).filter(func.lower(Player.name) == func.lower(name)).first()

def create_player(db: Session, name: str, position: str = "Unknown", college: str = "Unknown") -> Player:
    """Create a new player."""
    # First try to get the player by name (case-insensitive)
    existing_player = get_player_by_name(db, name)
    if existing_player:
        return existing_player
        
    # Create new player if not found
    player = Player(name=name, position=position, college=college)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

def create_odds(
    db: Session,
    player_id: int,
    odds: str,
    sportsbook: str,
    market_type: str,
    draft_position: Optional[int] = None,
    timestamp: Optional[datetime] = None
) -> Odds:
    """Create a new odds entry."""
    if timestamp is None:
        timestamp = datetime.now()
        
    odds_entry = Odds(
        player_id=player_id,
        odds=odds,
        sportsbook=sportsbook,
        market_type=market_type,
        draft_position=draft_position,
        timestamp=timestamp
    )
    db.add(odds_entry)
    db.commit()
    db.refresh(odds_entry)
    return odds_entry

def get_player_odds_history(
    db: Session,
    player_name: str,
    since: datetime
) -> List[Odds]:
    """Get odds history for a player since a given date."""
    return (
        db.query(Odds)
        .join(Player)
        .filter(
            and_(
                Player.name == player_name,
                Odds.timestamp >= since
            )
        )
        .order_by(desc(Odds.timestamp))
        .all()
    )

def get_latest_odds_all_players(db: Session) -> List[Odds]:
    """Get the latest odds for all players."""
    subquery = (
        db.query(
            Odds.player_id,
            Odds.market_type,
            func.max(Odds.timestamp).label('max_timestamp')
        )
        .group_by(Odds.player_id, Odds.market_type)
        .subquery()
    )
    
    return (
        db.query(Odds)
        .join(
            subquery,
            and_(
                Odds.player_id == subquery.c.player_id,
                Odds.market_type == subquery.c.market_type,
                Odds.timestamp == subquery.c.max_timestamp
            )
        )
        .options(joinedload(Odds.player))
        .order_by(Odds.draft_position)
        .all()
    ) 