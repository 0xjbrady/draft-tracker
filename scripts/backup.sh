#!/bin/bash
# Wrapper script for running backups via cron

# Change to application directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/Scripts/activate
fi

# Run backup script
python scripts/backup.py

# Deactivate virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 