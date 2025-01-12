"""Configuration management for the NFL Draft Odds Tracker."""
import os
from typing import Dict, Any
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    # Environment
    ENV: str = "development"
    DEBUG: bool = False
    
    # API Settings
    ODDS_API_KEY: str
    ODDS_API_BASE_URL: str = "https://api.the-odds-api.com/v4"
    
    # Database
    DATABASE_URL: str = "sqlite:///./odds_tracker.db"
    
    # Cache Settings
    CACHE_DURATION: int = 300  # 5 minutes
    CACHE_FILE: str = "odds_cache.json"
    
    # Scraper Settings
    SCRAPE_INTERVAL: int = 1800  # 30 minutes
    MIN_REQUEST_INTERVAL: float = 1.0
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list = ["http://localhost:5173"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "odds_tracker.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    env = os.getenv("ENV", "development")
    return Settings(_env_file=f".env.{env}")

def get_config_dict() -> Dict[str, Any]:
    """Get configuration as a dictionary for logging."""
    settings = get_settings()
    config_dict = settings.dict()
    # Remove sensitive information
    config_dict.pop("ODDS_API_KEY", None)
    return config_dict 