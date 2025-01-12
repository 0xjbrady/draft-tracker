"""Main application module."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
import datetime
from fastapi.responses import JSONResponse
from sqlalchemy.sql import text

from .analysis.odds_analysis import OddsAnalyzer
from .scheduler.odds_scheduler import OddsScheduler
from .models.database import init_db, SessionLocal
from .cache.odds_cache import odds_cache
from .monitoring.metrics import init_metrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NFL Draft Odds Tracker",
    description="API for tracking and analyzing NFL Draft odds from various sportsbooks",
    version="1.0.0"
)

# Initialize metrics collection
init_metrics(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer and scheduler
analyzer = OddsAnalyzer()
scheduler = OddsScheduler()

@app.on_event("startup")
async def startup_event():
    """Initialize database and start the odds scheduler when the application starts."""
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Start scheduler
    scheduler.start()
    logger.info("Application started, scheduler running")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "NFL Draft Odds Tracker",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/odds/player/{player_name}")
async def get_player_odds_history(player_name: str, days: Optional[int] = 7):
    """Get historical odds data for a player."""
    try:
        df = analyzer.get_player_odds_history(player_name, days)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No odds data found for player: {player_name}")
        
        # Convert DataFrame to list of dictionaries
        odds_data = df.to_dict(orient='records')
        for entry in odds_data:
            entry['timestamp'] = entry['timestamp'].isoformat()
        
        return odds_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/odds/player/{player_name}/chart")
async def get_player_odds_chart(player_name: str, days: Optional[int] = 7):
    """Get odds movement chart data for a player."""
    try:
        chart_data = analyzer.create_odds_movement_chart(player_name, days)
        if chart_data is None:
            raise HTTPException(status_code=404, detail=f"No odds data found for player: {player_name}")
        
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/odds/rankings")
async def get_consensus_rankings():
    """Get consensus draft rankings based on odds."""
    try:
        rankings = analyzer.get_consensus_rankings()
        if rankings.empty:
            raise HTTPException(status_code=404, detail="No odds data available for rankings")
        
        # Convert DataFrame to JSON-friendly format
        rankings_data = rankings.to_dict(orient='index')
        return rankings_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/odds/draft-board")
async def get_draft_board():
    """Get draft board data."""
    try:
        board_data = analyzer.create_draft_board_visualization()
        if board_data is None:
            raise HTTPException(status_code=404, detail="No odds data available for draft board")
        
        return board_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/odds/latest")
async def get_latest_odds():
    """Get latest odds for all players."""
    try:
        df = analyzer.get_consensus_rankings()
        if df.empty:
            raise HTTPException(status_code=404, detail="No odds data available")
        
        # Convert DataFrame to JSON-friendly format
        latest_odds = df.to_dict(orient='index')
        return latest_odds
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for container monitoring."""
    try:
        # Check database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        # Check cache status
        cache_stats = odds_cache.get_cache_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "database": "connected",
            "cache": cache_stats,
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "error": str(e)
            }
        ) 

@app.post("/odds/update")
async def trigger_odds_update():
    """Manually trigger an odds update."""
    try:
        await scheduler.update_odds()
        return {"status": "success", "message": "Odds update triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 