import asyncio
import logging
from app.scrapers.odds_scraper import OddsScraper

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    logger = logging.getLogger(__name__)
    logger.info("Starting odds collection...")
    
    scraper = OddsScraper()
    odds_entries = await scraper.get_draftkings_odds()
    
    if odds_entries:
        logger.info(f"Successfully collected {len(odds_entries)} odds entries")
        # Print first few entries as sample
        for entry in odds_entries[:3]:
            logger.info(f"Sample odds entry: {entry}")
    else:
        logger.warning("No odds were collected")

if __name__ == "__main__":
    asyncio.run(main()) 