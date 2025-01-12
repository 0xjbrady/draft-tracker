"""Database models for the application."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class Player(Base):
    """Model for NFL Draft prospects."""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    position = Column(String)
    college = Column(String)
    
    # Relationships
    odds = relationship("Odds", back_populates="player")

class Odds(Base):
    """Model for draft odds entries."""
    __tablename__ = "odds"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    odds = Column(String)  # Store as string to preserve exact format (+150, -180, etc.)
    draft_position = Column(Float, nullable=True)
    sportsbook = Column(String)
    market_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player = relationship("Player", back_populates="odds") 