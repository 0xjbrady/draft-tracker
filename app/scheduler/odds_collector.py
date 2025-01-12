import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from ..scrapers.odds_scraper import OddsScraper
from ..models.database import DraftOdds, get_db

logger = logging.getLogger(__name__)

class OddsCollector:
    def __init__(self):
        self.scraper = OddsScraper()

    async def collect_odds(self):
        """
        Collect odds from all configured sportsbooks and store in database.
        """
        try:
            # Collect odds from different sportsbooks
            fanduel_odds = await self.scraper.get_fanduel_odds()
            draftkings_odds = await self.scraper.get_draftkings_odds()

            # Combine all odds
            all_odds = fanduel_odds + draftkings_odds

            # Store in database
            self._store_odds(all_odds)
            
            logger.info(f"Successfully collected odds at {datetime.now()}")
        except Exception as e:
            logger.error(f"Error collecting odds: {str(e)}")

    def _store_odds(self, odds_data: list):
        """
        Store collected odds in the database.
        """
        db = next(get_db())
        try:
            for odds in odds_data:
                db_odds = DraftOdds(
                    player_name=odds["player_name"],
                    draft_position=odds["draft_position"],
                    odds=odds["odds"],
                    sportsbook=odds["sportsbook"],
                    draft_year=odds["draft_year"],
                    market_type=odds["market_type"]
                )
                db.add(db_odds)
            db.commit()
        except Exception as e:
            logger.error(f"Error storing odds in database: {str(e)}")
            db.rollback()
        finally:
            db.close()

def schedule_odds_collection(scheduler):
    """
    Schedule regular odds collection.
    """
    collector = OddsCollector()
    
    # Schedule collection every 6 hours
    scheduler.add_job(
        lambda: asyncio.run(collector.collect_odds()),
        'interval',
        hours=6,
        id='collect_odds',
        replace_existing=True
    )
    
    logger.info("Scheduled odds collection job") 