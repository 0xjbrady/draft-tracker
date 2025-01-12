# NFL Draft Odds Tracker - CI/CD Setup Guide

This guide details how to set up Continuous Integration and Continuous Deployment for the NFL Draft Odds Tracker using GitHub Actions.

## Table of Contents
- [Prerequisites](#prerequisites)
- [CI Setup](#ci-setup)
- [CD Setup](#cd-setup)
- [GitHub Secrets Configuration](#github-secrets-configuration)
- [Docker Hub Setup](#docker-hub-setup)
- [Production Server Setup](#production-server-setup)
- [Deployment Process](#deployment-process)

## Prerequisites

Before setting up CI/CD, ensure you have:
- A GitHub repository for the NFL Draft Odds Tracker
- A Docker Hub account
- A production server with SSH access
- Docker and Docker Compose installed on the production server

## CI Setup

The CI workflow (`ci.yml`) runs on every push to main and pull requests:

1. **Testing**: 
   ```yaml
   name: CI
   
   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
             
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt
             
         - name: Run tests
           run: |
             pytest tests/ -v --cov=app
             
         - name: Upload coverage
           uses: codecov/codecov-action@v3
   ```

2. **Frontend Tests**:
   ```yaml
   frontend-test:
     runs-on: ubuntu-latest
     steps:
       - uses: actions/checkout@v3
       
       - name: Set up Node.js
         uses: actions/setup-node@v3
         with:
           node-version: '18'
           
       - name: Install dependencies
         working-directory: ./draft-tracker-frontend
         run: npm install
         
       - name: Run tests
         working-directory: ./draft-tracker-frontend
         run: npm test
   ```

## CD Setup

The CD workflow (`cd.yml`) runs when a version tag is pushed:

```yaml
name: CD

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}
          
      - name: Build and push images
        run: |
          docker-compose build
          docker-compose push
          
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USERNAME }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/draft-tracker
            docker-compose down
            docker-compose pull
            docker-compose up -d
```

## GitHub Secrets Configuration

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add the following secrets:

   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_TOKEN`: Docker Hub access token
   - `PROD_HOST`: Production server hostname or IP
   - `PROD_USERNAME`: SSH username for the production server
   - `PROD_SSH_KEY`: SSH private key for authentication
   - `ENV_PRODUCTION`: Complete contents of your production .env file
   - `ODDS_API_KEY`: Your API key for The Odds API

## Docker Hub Setup

1. Create a Docker Hub account
2. Create an access token:
   - Go to Account Settings > Security
   - Click "New Access Token"
   - Name it "GitHub Actions"
   - Copy the token and save it as `DOCKER_TOKEN` in GitHub secrets

3. Create repositories:
   - Create `nfl-draft-odds-backend`
   - Create `nfl-draft-odds-frontend`

## Production Server Setup

1. Create the application directory:
   ```bash
   mkdir -p /opt/draft-tracker
   cd /opt/draft-tracker
   ```

2. Set up SSH key authentication:
   ```bash
   # On your local machine
   ssh-keygen -t ed25519 -C "github-actions"
   # Add public key to production server
   ssh-copy-id -i ~/.ssh/id_ed25519.pub user@your-server
   # Add private key to GitHub secrets as PROD_SSH_KEY
   ```

3. Install Docker and Docker Compose:
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com | sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

4. Create required directories:
   ```bash
   mkdir -p data logs
   chmod 755 data logs
   ```

## Deployment Process

1. Create and push a new version tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. Monitor the deployment:
   ```bash
   # Check container status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   
   # Test endpoints
   curl http://localhost/health
   ```

## Automated Testing

The CI workflow includes:
1. Python unit tests with coverage reporting
2. Frontend React component tests
3. Integration tests
4. Linting and type checking

## Security Considerations

1. Secrets Management:
   - Use GitHub Secrets for sensitive data
   - Rotate access tokens regularly
   - Use environment-specific variables

2. Docker Security:
   - Scan images for vulnerabilities
   - Use minimal base images
   - Implement resource limits

3. Server Security:
   - Use SSH key authentication only
   - Configure firewall rules
   - Keep software updated

## Troubleshooting

1. **CI Failures**:
   - Check the GitHub Actions logs
   - Verify all dependencies are in requirements.txt
   - Ensure tests are passing locally

2. **CD Failures**:
   - Verify Docker Hub credentials
   - Check SSH access to production server
   - Verify environment variables

3. **Deployment Issues**:
   - Check application logs
   - Verify container health
   - Test endpoints manually

## Best Practices

1. Version Control:
   - Use semantic versioning
   - Create release notes
   - Tag releases appropriately

2. Testing:
   - Write comprehensive tests
   - Maintain high coverage
   - Test in isolation

3. Monitoring:
   - Set up alerts
   - Monitor resource usage
   - Track deployment success rates

## Support

For issues or questions:
1. Check the GitHub Actions logs
2. Review the troubleshooting section
3. Submit an issue on GitHub
4. Contact the development team 