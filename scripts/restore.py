#!/usr/bin/env python3
"""Restore script for NFL Draft Odds Tracker."""
import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def list_backups():
    """List available backups."""
    backup_root = Path('backups')
    if not backup_root.exists():
        logger.error("No backups directory found")
        return []

    backups = sorted(
        [d for d in backup_root.iterdir() if d.is_dir()],
        key=lambda x: x.name,
        reverse=True
    )
    return backups

def get_latest_backup() -> Optional[Path]:
    """Get the most recent backup directory."""
    backups = list_backups()
    return backups[0] if backups else None

def restore_database(backup_dir: Path):
    """Restore SQLite database from backup."""
    try:
        # Copy backup file to container
        result = subprocess.run(
            ['docker', 'cp',
             backup_dir / 'odds_tracker.db',
             'nfl-draft-odds-backend:/app/data/restore.db'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Database copy failed: {result.stderr}")
            return False

        # Restore database inside container
        result = subprocess.run(
            ['docker-compose', 'exec', '-T', 'backend', 'sh', '-c',
             'sqlite3 /app/data/odds_tracker.db ".restore /app/data/restore.db"'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Database restore failed: {result.stderr}")
            return False

        logger.info("Database restored successfully")
        return True
    except Exception as e:
        logger.error(f"Database restore failed: {str(e)}")
        return False

def restore_cache(backup_dir: Path):
    """Restore cache file from backup."""
    try:
        result = subprocess.run(
            ['docker', 'cp',
             backup_dir / 'odds_cache.json',
             'nfl-draft-odds-backend:/app/data/odds_cache.json'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Cache restore failed: {result.stderr}")
            return False

        logger.info("Cache restored successfully")
        return True
    except Exception as e:
        logger.error(f"Cache restore failed: {str(e)}")
        return False

def restore_logs(backup_dir: Path):
    """Restore log files from backup."""
    try:
        result = subprocess.run(
            ['docker', 'cp',
             str(backup_dir / 'logs') + '/.',
             'nfl-draft-odds-backend:/app/logs/'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Logs restore failed: {result.stderr}")
            return False

        logger.info("Logs restored successfully")
        return True
    except Exception as e:
        logger.error(f"Logs restore failed: {str(e)}")
        return False

def main():
    """Main restore function."""
    logger.info("Starting restore process")

    # List available backups
    backups = list_backups()
    if not backups:
        logger.error("No backups found")
        return 1

    # Get backup to restore
    if len(sys.argv) > 1:
        # Use specified backup
        backup_dir = Path(sys.argv[1])
        if not backup_dir.exists():
            logger.error(f"Backup directory not found: {backup_dir}")
            return 1
    else:
        # Use latest backup
        backup_dir = get_latest_backup()
        if not backup_dir:
            logger.error("No backups found")
            return 1

    logger.info(f"Restoring from backup: {backup_dir}")

    # Perform restore
    success = all([
        restore_database(backup_dir),
        restore_cache(backup_dir),
        restore_logs(backup_dir)
    ])

    if success:
        logger.info("Restore completed successfully")
        return 0
    else:
        logger.error("Restore failed")
        return 1

if __name__ == '__main__':
    exit(main()) 