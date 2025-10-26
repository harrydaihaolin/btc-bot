# GitHub Actions Configuration for Tennis Bot

## Workflows Overview

### 1. CI Tests (`ci.yml`)
- **Triggers**: Push to main/develop, Pull Requests
- **Python Versions**: 3.11, 3.12
- **Features**:
  - Unit tests with coverage reporting
  - Docker image building and testing
  - Integration tests with Docker Compose
  - Code linting (Black, isort, flake8, mypy)
  - Coverage upload to Codecov

### 2. Periodic Court Monitoring (`periodic-monitoring.yml`)
- **Triggers**: Every 2 hours (9 AM - 9 PM PST), Manual dispatch
- **Features**:
  - Automated court monitoring using Docker containers
  - Health checks for both BTC and UBC bots
  - Log artifact upload for debugging
  - Uses GitHub Secrets for credentials

### 3. Docker Build and Push (`docker-release.yml`)
- **Triggers**: Version tags, Manual dispatch
- **Features**:
  - Multi-platform Docker builds
  - Automated Docker Hub publishing
  - GitHub Release creation
  - Docker layer caching for faster builds

### 4. Security and Code Quality (`security.yml`)
- **Triggers**: Push to main, Pull Requests, Weekly schedule
- **Features**:
  - Trivy vulnerability scanning
  - Bandit security linting
  - Dependency vulnerability checks (Safety, pip-audit)
  - Code quality analysis (Pylint, Radon, Xenon)
  - Docker image security scanning

## Required GitHub Secrets

### For Periodic Monitoring:
```
BTC_USERNAME=your_btc_email@example.com
BTC_PASSWORD=your_btc_password
BTC_NOTIFICATION_EMAIL=your_notification_email@gmail.com
BTC_GMAIL_APP_PASSWORD=your_gmail_app_password
BTC_SMS_PHONE=+1234567890

UBC_USERNAME=your_ubc_email@ubc.ca
UBC_PASSWORD=your_ubc_password
UBC_NOTIFICATION_EMAIL=your_notification_email@gmail.com
UBC_GMAIL_APP_PASSWORD=your_gmail_app_password
UBC_SMS_PHONE=+1234567890

TWILIO_SID=your_twilio_sid
TWILIO_TOKEN=your_twilio_token
TWILIO_PHONE=+1234567890
```

### For Docker Publishing:
```
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_token
```

## Usage Examples

### Manual Court Monitoring
```bash
# Trigger periodic monitoring manually
gh workflow run periodic-monitoring.yml
```

### Release New Version
```bash
# Create and push a version tag
git tag v1.4.0
git push origin v1.4.0
# This will automatically build and publish Docker images
```

### Check Security Status
- Go to GitHub repository → Security tab
- View Code scanning alerts
- Review dependency vulnerabilities

## Monitoring Dashboard

### Workflow Status
- **CI Tests**: ✅ All tests passing
- **Security Scan**: ✅ No critical vulnerabilities
- **Docker Build**: ✅ Images published successfully
- **Periodic Monitoring**: ✅ Running every 2 hours

### Coverage Reports
- **Overall Coverage**: 84%
- **UBC Modules**: 56%
- **BTC Modules**: 100%
- **Common Modules**: 100%

## Troubleshooting

### Failed Tests
1. Check the Actions tab for detailed logs
2. Run tests locally: `pytest tests/ -v`
3. Check Docker build locally: `./docker-manage.sh build`

### Security Issues
1. Review Security tab alerts
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Fix security warnings in code

### Monitoring Failures
1. Check GitHub Secrets are properly set
2. Verify credentials are valid
3. Review monitoring logs in artifacts
