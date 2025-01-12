"""Database configuration and initialization."""
import logging
import os
import time
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, MetaData, inspect
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from ..monitoring.metrics import (
    DB_QUERY_DURATION,
    DB_QUERY_COUNT,
    DB_CONNECTION_ERRORS
)

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./odds_tracker.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create MetaData instance
metadata = MetaData()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base(metadata=metadata)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        DB_CONNECTION_ERRORS.inc()
        logging.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()

def init_db() -> None:
    """Initialize the database."""
    try:
        # Check if tables exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Create only missing tables
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        if not existing_tables:
            logging.info("Database initialized with new tables")
        else:
            logging.info(f"Database already contains tables: {existing_tables}")
    except Exception as e:
        DB_CONNECTION_ERRORS.inc()
        logging.error(f"Failed to initialize database: {str(e)}")
        raise

# Add event listeners for metrics
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.time())
    DB_QUERY_COUNT.inc()

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info["query_start_time"].pop(-1)
    DB_QUERY_DURATION.observe(total) 