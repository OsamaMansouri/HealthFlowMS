@echo off
REM Run tests inside Docker container
echo Running tests in Docker container...
docker exec healthflow-score-api pytest tests/ -v
