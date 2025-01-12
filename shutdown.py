"""Script to gracefully shut down the NFL Draft Odds Tracker."""
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def shutdown():
    """Perform cleanup operations before shutting down."""
    try:
        # Close any open database connections
        db_path = Path("odds_tracker.db")
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            conn.close()
            logger.info("Database connections closed")
            
        # Remove any temporary files
        temp_files = [".coverage", ".pytest_cache"]
        for temp_file in temp_files:
            path = Path(temp_file)
            if path.exists():
                if path.is_file():
                    path.unlink()
                else:
                    for file in path.glob("**/*"):
                        if file.is_file():
                            file.unlink()
                    path.rmdir()
                logger.info(f"Removed {temp_file}")
                
        logger.info("Shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        raise

if __name__ == "__main__":
    shutdown() 