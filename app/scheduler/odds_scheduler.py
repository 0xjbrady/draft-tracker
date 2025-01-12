import asyncio
from datetime import datetime
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from typing import List, Dict

from ..scrapers.odds_scraper import OddsScraper
from ..models import crud, database as db

logger = logging.getLogger(__name__)

class OddsScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scraper = OddsScraper()

    async def update_odds(self):
        """Fetch latest odds and update the database."""
        logger.info("Starting NFL Draft odds update...")
        try:
            # Fetch odds from all sportsbooks
            odds_data = await self.scraper.get_all_odds()
            
            # Get database session
            with db.get_db() as session:
                # Process each odds entry
                for odds in odds_data:
                    try:
                        # Get or create player
                        player = crud.get_player_by_name(session, odds["player_name"])
                        if not player:
                            player = crud.create_player(
                                session,
                                name=odds["player_name"],
                                position="Unknown",  # Will be updated when we add player info scraping
                                college="Unknown"    # Will be updated when we add player info scraping
                            )
                        
                        # Create odds entry
                        crud.create_odds(
                            db=session,
                            player_id=player.id,
                            odds=odds["odds"],
                            sportsbook=odds["sportsbook"],
                            market_type=odds["market_type"],
                            draft_position=odds.get("draft_position"),
                            timestamp=datetime.fromtimestamp(odds["timestamp"])
                        )
                    except Exception as e:
                        logger.error(f"Error processing odds for {odds['player_name']}: {str(e)}")
                        continue
                
                logger.info(f"Successfully updated NFL Draft odds at {datetime.now()}")
        except Exception as e:
            logger.error(f"Error updating NFL Draft odds: {str(e)}")

    def start(self):
        """Start the scheduler."""
        # Regular updates throughout the day
        self.scheduler.add_job(
            self.update_odds,
            trigger=CronTrigger(
                hour='*/4'  # Run every 4 hours
            ),
            id='update_odds_regular',
            name='Update NFL Draft Odds - Regular Schedule',
            replace_existing=True
        )
        
        # More frequent updates during peak hours (9 AM - 11 PM ET)
        self.scheduler.add_job(
            self.update_odds,
            trigger=CronTrigger(
                hour='9-23',  # 9 AM to 11 PM
                minute='*/30'  # Every 30 minutes
            ),
            id='update_odds_peak',
            name='Update NFL Draft Odds - Peak Hours',
            replace_existing=True
        )
        
        # Very frequent updates on draft day and day before
        self.scheduler.add_job(
            self.update_odds,
            trigger=CronTrigger(
                month=4,  # April
                day='24,25',  # Day before and day of draft
                minute='*/10'  # Every 10 minutes
            ),
            id='update_odds_draft_day',
            name='Update NFL Draft Odds - Draft Day',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("NFL Draft odds scheduler started") 