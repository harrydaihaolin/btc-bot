# GitHub Actions Configuration

## Workflow Status
- ✅ **CI Tests**: All tests passing, 84% coverage
- ✅ **Security Scan**: No critical vulnerabilities
- ✅ **Docker Build**: Images building successfully
- ✅ **Periodic Monitoring**: Running every 2 hours

## Quick Commands

### Local Testing
```bash
# Run all tests
pytest tests/ -v --cov=. --cov-report=term-missing

# Run specific test suite
pytest tests/btc/ -v
pytest tests/ubc/ -v

# Run with Docker
./docker-manage.sh build
./docker-manage.sh start
```

### GitHub Actions
```bash
# Trigger workflows manually
gh workflow run ci.yml
gh workflow run periodic-monitoring.yml
gh workflow run security.yml

# Check workflow status
gh run list
gh run view <run-id>
```

### Docker Management
```bash
# Build and test locally
docker-compose build
docker-compose up -d
docker-compose logs -f

# Clean up
docker-compose down
docker system prune -a
```

## Troubleshooting

### Common Issues
1. **Tests failing**: Check Python version compatibility
2. **Docker build failing**: Verify Chrome installation in Dockerfile
3. **Monitoring not working**: Check GitHub Secrets configuration
4. **Security alerts**: Review and update dependencies

### Debug Commands
```bash
# Check Docker images
docker images | grep tennis-bot

# Check container logs
docker logs btc-tennis-bot
docker logs ubc-tennis-bot

# Test individual components
python3 -c "from btc.config.btc_config import BTCConfig; print('BTC OK')"
python3 -c "from ubc.config.ubc_config import UBCConfig; print('UBC OK')"
```
