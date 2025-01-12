# NFL Draft Odds Tracker

A full-stack application for tracking and analyzing NFL Draft odds from various sportsbooks. The application provides real-time odds updates, consensus rankings, and visualizations of draft positions and odds movement.

## Features

- Real-time odds tracking from multiple sportsbooks
- Consensus draft rankings based on aggregated odds data
- Interactive visualizations of draft positions and odds movement
- Automated odds updates at regular intervals and peak hours
- RESTful API for accessing odds data and analytics
- Modern React frontend with Material-UI components
- Docker containerization for easy deployment
- Nginx reverse proxy for production deployment
- Comprehensive error handling and user feedback
- Prometheus metrics for monitoring
- Health checks for system status
- Mock data support for development

## Project Structure

```
├── app/                    # Backend application
│   ├── models/            # Database models and CRUD operations
│   ├── scrapers/          # Odds scraping functionality
│   ├── scheduler/         # Automated odds update scheduling
│   ├── monitoring/        # Metrics and monitoring
│   ├── cache/            # Caching functionality
│   └── analysis/          # Odds analysis and visualization
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── data/             # Mock data for testing
├── draft-tracker-frontend/ # React frontend application
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   ├── hooks/        # Custom React hooks
│   │   └── types/        # TypeScript type definitions
│   └── nginx.conf        # Nginx configuration for frontend
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile            # Backend Dockerfile
└── requirements.txt      # Python dependencies

## Development Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd draft-tracker-frontend
npm install
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
DATABASE_URL=sqlite:///./odds_tracker.db
ODDS_API_KEY=your_api_key_here
ENVIRONMENT=development
USE_MOCK_DATA=true
```

## Docker Deployment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/draft-tracker.git
cd draft-tracker
```

2. Create production environment file:
```bash
cp .env.production.template .env.production
```

3. Edit `.env.production` with your values

4. Create required directories:
```bash
mkdir -p data logs
chmod 755 data logs
```

5. Build and start the containers:
```bash
docker-compose up -d --build
```

The application will be available at:
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

## API Endpoints

### Data Endpoints
- `GET /odds/rankings` - Get consensus rankings for all players
- `GET /odds/player/{player_name}` - Get historical odds for a specific player
- `GET /odds/player/{player_name}/chart` - Get odds movement chart data
- `GET /odds/draft-board` - Get current draft board visualization
- `GET /odds/latest` - Get latest odds for all players
- `POST /odds/update` - Trigger manual odds update

### System Endpoints
- `GET /health` - Check application health status
- `GET /metrics` - Get application metrics (Prometheus format)

## Development Mode

1. Start the backend server:
```bash
python -m uvicorn app.main:app --reload
```

2. Start the frontend development server:
```bash
cd draft-tracker-frontend
npm run dev
```

The development server will use mock data by default to avoid API rate limits.

## Testing

Run the test suite with:
```bash
pytest tests/ -v --cov=app
```

For frontend tests:
```bash
cd draft-tracker-frontend
npm test
```

## Automated Updates

The application automatically updates odds:
- Every 30 minutes during regular hours
- Every 15 minutes during peak hours (9am, 1pm, 5pm, 9pm)
- Every 5 minutes on NFL Draft day

Mock data is used in development mode for testing and development purposes.

## Monitoring

### Application Metrics
Available at `/metrics` in Prometheus format:
- HTTP request counts and durations
- Database query performance
- Cache hit/miss rates
- Odds scraping statistics
- Resource usage metrics

### Health Checks
Available at `/health`:
- Database connectivity
- Cache status
- API rate limits
- Overall application health

### Logs
- Application logs in `logs/app.log`
- Docker container logs via `docker-compose logs`
- Frontend error tracking and reporting

## Error Handling

The application includes comprehensive error handling:
- Network connectivity issues
- API rate limits and timeouts
- Database connection errors
- Cache failures
- User-friendly error messages
- Detailed logging for debugging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - See LICENSE file for details 