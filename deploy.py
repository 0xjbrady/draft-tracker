"""Deployment script for the NFL Draft Odds Tracker."""
import os
import sys
import subprocess
import logging
from pathlib import Path

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        "ENV",
        "ODDS_API_KEY",
        "DATABASE_URL",
        "LOG_LEVEL"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

def setup_environment():
    """Set up the production environment."""
    # Create necessary directories
    dirs = ["logs", "data"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    # Install production dependencies
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Set up environment variables if .env.production exists
    env_file = ".env.production"
    if os.path.exists(env_file):
        print(f"Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def run_migrations():
    """Run database migrations."""
    try:
        from app.models.database import init_db
        init_db()
        print("Database migrations completed successfully")
    except Exception as e:
        print(f"Error running migrations: {str(e)}")
        sys.exit(1)

def start_application():
    """Start the application using uvicorn."""
    import uvicorn
    from app.config import get_settings
    
    settings = get_settings()
    
    # Configure uvicorn logging
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = '%(asctime)s - %(levelname)s - %(message)s'
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENV == "development",
        workers=4 if settings.ENV == "production" else 1,
        log_config=log_config
    )

def main():
    """Main deployment function."""
    try:
        print("Starting deployment process...")
        
        # Check environment
        check_environment()
        print("Environment variables verified")
        
        # Set up environment
        setup_environment()
        print("Environment setup completed")
        
        # Run database migrations
        run_migrations()
        print("Database migrations completed")
        
        # Start application
        print("Starting application...")
        start_application()
        
    except Exception as e:
        print(f"Deployment failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 