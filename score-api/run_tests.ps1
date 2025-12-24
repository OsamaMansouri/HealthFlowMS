# Run tests inside Docker container
Write-Host "Running tests in Docker container..." -ForegroundColor Green
docker exec healthflow-score-api pytest tests/ -v
