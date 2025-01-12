# NFL Draft Odds Tracker Deployment Guide

This guide details the process of deploying the NFL Draft Odds Tracker application to a production environment using Docker and Nginx.

## Prerequisites

- Docker and Docker Compose installed on the host machine
- Domain name configured with DNS records (optional for local deployment)
- SSL certificate for your domain (optional for local deployment)
- The Odds API key from https://the-odds-api.com
- Access to the production server

## Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/draft-tracker.git
   cd draft-tracker
   ```

2. Create production environment file:
   ```bash
   cp .env.production.template .env.production
   ```

3. Edit `.env.production` with your production values:
   ```
   # API Settings
   ODDS_API_KEY=your_api_key_here
   ODDS_API_BASE_URL=https://api.the-odds-api.com/v4
   
   # Database Configuration
   DATABASE_URL=sqlite:///./data/odds_tracker.db
   
   # Cache Settings
   CACHE_DURATION=3600
   CACHE_FILE=odds_cache.json
   
   # Scraper Settings
   SCRAPE_INTERVAL=1800
   USE_MOCK_DATA=false
   
   # Server Settings
   HOST=0.0.0.0
   PORT=8000
   ENVIRONMENT=production
   
   # CORS Configuration
   CORS_ORIGINS=["http://localhost:80"]
   
   # Logging
   LOG_LEVEL=INFO
   LOG_FILE=app.log
   ```

## Directory Setup

1. Create required directories:
   ```bash
   mkdir -p data logs
   chmod 755 data logs
   ```

2. Set proper permissions:
   ```bash
   chmod 600 .env.production
   ```

## Deployment Steps

1. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```

2. Verify the deployment:
   ```bash
   # Check container status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   ```

3. Test the endpoints:
   - Frontend: http://localhost:80
   - Backend health: http://localhost:8000/health
   - API documentation: http://localhost:8000/docs
   - Metrics: http://localhost:8000/metrics

## Monitoring Setup

1. Application Metrics:
   - Backend metrics available at `/metrics`
   - Includes:
     - HTTP request counts and durations
     - Database query performance
     - Cache hit/miss rates
     - Odds scraping statistics
     - Resource usage metrics

2. Health Checks:
   - Endpoint: `/health`
   - Monitors:
     - Database connectivity
     - Cache status
     - API rate limits
     - Overall application health

3. Logging:
   - Application logs in `logs/app.log`
   - Docker container logs:
     ```bash
     docker-compose logs -f backend
     docker-compose logs -f frontend
     ```

## Maintenance

### Database Management

1. Backup the database:
   ```bash
   docker-compose exec backend python scripts/backup.py
   ```

2. Restore from backup:
   ```bash
   docker-compose exec backend python scripts/restore.py backups/YYYYMMDD_HHMMSS
   ```

### Updating the Application

1. Pull latest changes:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Troubleshooting

1. Network Issues:
   - Check Nginx logs
   - Verify CORS settings
   - Confirm proxy configuration

2. Database Issues:
   - Check connection string
   - Verify file permissions
   - Review migration logs

3. API Issues:
   - Verify API key
   - Check rate limits
   - Review scraper logs

## Security Best Practices

1. Environment Variables:
   - Use `.env.production` for sensitive data
   - Restrict file permissions
   - Never commit secrets to version control

2. Network Security:
   - Configure firewall rules
   - Use HTTPS in production
   - Implement rate limiting

3. Container Security:
   - Keep images updated
   - Use non-root users
   - Implement resource limits

## Rollback Procedure

1. Stop current deployment:
   ```bash
   docker-compose down
   ```

2. Checkout previous version:
   ```bash
   git checkout <previous-tag>
   ```

3. Restore database if needed:
   ```bash
   docker-compose exec backend python scripts/restore.py backups/YYYYMMDD_HHMMSS
   ```

4. Rebuild and restart:
   ```bash
   docker-compose up -d --build
   ```

## Production Checklist

- [ ] Environment variables configured
- [ ] Data directories created with proper permissions
- [ ] Database initialized and migrated
- [ ] Nginx configured correctly
- [ ] SSL certificates installed (if using HTTPS)
- [ ] Monitoring and logging set up
- [ ] Backup procedure tested
- [ ] Security measures implemented
- [ ] Application health checks passing
- [ ] Documentation updated

## Support

For issues or questions:
1. Check application logs
2. Review troubleshooting section
3. Submit an issue on GitHub
4. Contact the development team 