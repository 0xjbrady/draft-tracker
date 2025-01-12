"""Pytest configuration file."""
import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging for tests
import logging
logging.basicConfig(level=logging.DEBUG)

# Disable APScheduler logging during tests
logging.getLogger('apscheduler').setLevel(logging.ERROR) 