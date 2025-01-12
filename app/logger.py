"""Logging configuration for the NFL Draft Odds Tracker."""
import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional

from .config import get_settings

def setup_logging(log_file: Optional[str] = None) -> None:
    """Configure application logging.
    
    Args:
        log_file: Optional path to log file. If not provided, uses setting from config.
    """
    settings = get_settings()
    log_file = log_file or settings.LOG_FILE
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Format for logging
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, log_file),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Log startup information
    logger.info("Logging configured with level: %s", settings.LOG_LEVEL)
    if settings.ENV == "production":
        logger.info("Running in production mode")
    else:
        logger.info("Running in development mode")

def log_startup_info() -> None:
    """Log application startup information."""
    settings = get_settings()
    logger = logging.getLogger(__name__)
    
    logger.info("NFL Draft Odds Tracker starting up")
    logger.info("Environment: %s", settings.ENV)
    logger.info("Debug mode: %s", settings.DEBUG)
    logger.info("Database URL: %s", settings.DATABASE_URL)
    logger.info("Cache duration: %d seconds", settings.CACHE_DURATION)
    logger.info("Scrape interval: %d seconds", settings.SCRAPE_INTERVAL)
    logger.info("Server running on: %s:%d", settings.HOST, settings.PORT)
    
    # Log when the application was last started
    with open(os.path.join("logs", "last_startup.txt"), "w") as f:
        f.write(datetime.now().isoformat()) 