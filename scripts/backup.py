#!/usr/bin/env python3
"""Backup script for NFL Draft Odds Tracker."""
import os
import shutil
import datetime
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_backup_directory():
    """Create backup directory with timestamp."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path('backups') / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir

def backup_database(backup_dir: Path):
    """Backup SQLite database."""
    try:
        # Create database backup inside container
        result = subprocess.run(
            ['docker-compose', 'exec', '-T', 'backend', 'sh', '-c',
             'sqlite3 /app/data/odds_tracker.db ".backup /app/data/backup.db"'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Database backup failed: {result.stderr}")
            return False

        # Copy backup file from container
        result = subprocess.run(
            ['docker', 'cp',
             'nfl-draft-odds-backend:/app/data/backup.db',
             backup_dir / 'odds_tracker.db'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Database copy failed: {result.stderr}")
            return False

        logger.info("Database backup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Database backup failed: {str(e)}")
        return False

def backup_cache(backup_dir: Path):
    """Backup cache file."""
    try:
        result = subprocess.run(
            ['docker', 'cp',
             'nfl-draft-odds-backend:/app/data/odds_cache.json',
             backup_dir / 'odds_cache.json'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Cache backup failed: {result.stderr}")
            return False

        logger.info("Cache backup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Cache backup failed: {str(e)}")
        return False

def backup_logs(backup_dir: Path):
    """Backup log files."""
    try:
        log_backup_dir = backup_dir / 'logs'
        log_backup_dir.mkdir(exist_ok=True)

        result = subprocess.run(
            ['docker', 'cp',
             'nfl-draft-odds-backend:/app/logs/.',
             str(log_backup_dir)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Logs backup failed: {result.stderr}")
            return False

        logger.info("Logs backup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Logs backup failed: {str(e)}")
        return False

def cleanup_old_backups(max_backups: int = 7):
    """Remove old backups keeping only the specified number of recent ones."""
    try:
        backup_root = Path('backups')
        if not backup_root.exists():
            return

        # List all backup directories
        backups = sorted(
            [d for d in backup_root.iterdir() if d.is_dir()],
            key=lambda x: x.name,
            reverse=True
        )

        # Remove old backups
        for backup_dir in backups[max_backups:]:
            shutil.rmtree(backup_dir)
            logger.info(f"Removed old backup: {backup_dir}")

    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")

def main():
    """Main backup function."""
    logger.info("Starting backup process")
    
    # Create backup directory
    backup_dir = create_backup_directory()
    logger.info(f"Created backup directory: {backup_dir}")

    # Perform backups
    success = all([
        backup_database(backup_dir),
        backup_cache(backup_dir),
        backup_logs(backup_dir)
    ])

    # Cleanup old backups
    cleanup_old_backups()

    if success:
        logger.info("Backup completed successfully")
        return 0
    else:
        logger.error("Backup failed")
        return 1

if __name__ == '__main__':
    exit(main()) 