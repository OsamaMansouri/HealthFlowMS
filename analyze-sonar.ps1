# HealthFlow-MS SonarQube Analysis Script for Windows PowerShell

Write-Host "================================================" -ForegroundColor Blue
Write-Host "  HealthFlow-MS SonarQube Analysis" -ForegroundColor Blue
Write-Host "================================================" -ForegroundColor Blue
Write-Host ""

# Check if SonarQube is running
Write-Host "Checking if SonarQube is running..." -ForegroundColor Yellow
$sonarRunning = docker-compose ps sonarqube | Select-String "Up"

if (-not $sonarRunning) {
    Write-Host "❌ SonarQube is not running!" -ForegroundColor Red
    Write-Host "Starting SonarQube..." -ForegroundColor Yellow
    docker-compose up -d sonarqube
    Write-Host "Waiting for SonarQube to start (this may take 2-3 minutes)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 120
}

# Check SonarQube status
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9000/api/system/status" -UseBasicParsing
    $status = ($response.Content | ConvertFrom-Json).status
    
    if ($status -ne "UP") {
        Write-Host "❌ SonarQube is not ready yet. Please wait and try again." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ SonarQube is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Cannot connect to SonarQube. Please check if it's running." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Prompt for SonarQube token
Write-Host "Enter your SonarQube token:" -ForegroundColor Yellow
Write-Host "(Generate at: http://localhost:9000 → My Account → Security → Tokens)" -ForegroundColor Yellow
$SONAR_TOKEN = Read-Host

if ([string]::IsNullOrWhiteSpace($SONAR_TOKEN)) {
    Write-Host "❌ Token is required!" -ForegroundColor Red
    exit 1
}

# Function to analyze a service
function Analyze-Service {
    param(
        [string]$ServiceName,
        [string]$ServiceDir
    )
    
    Write-Host ""
    Write-Host "🔍 Analyzing $ServiceName..." -ForegroundColor Blue
    
    $currentPath = (Get-Location).Path
    $servicePath = Join-Path $currentPath $ServiceDir
    
    docker run --rm `
        --network="healthflowms_default" `
        -v "${servicePath}:/usr/src" `
        sonarsource/sonar-scanner-cli `
        -Dsonar.login="$SONAR_TOKEN" `
        -Dsonar.host.url="http://sonarqube:9000"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $ServiceName analysis complete" -ForegroundColor Green
    } else {
        Write-Host "❌ $ServiceName analysis failed" -ForegroundColor Red
    }
}

# Analyze all Python services
Analyze-Service -ServiceName "Score API" -ServiceDir "score-api"
Analyze-Service -ServiceName "DeID Service" -ServiceDir "deid"
Analyze-Service -ServiceName "Featurizer" -ServiceDir "featurizer"
Analyze-Service -ServiceName "Model Risque" -ServiceDir "model-risque"
Analyze-Service -ServiceName "Audit Fairness" -ServiceDir "audit-fairness"

# Analyze Java service (optional - requires Maven)
Write-Host ""
Write-Host "🔍 Analyzing Proxy FHIR (Java)..." -ForegroundColor Blue
Write-Host "Note: This requires Maven. Skip if not needed (Ctrl+C)" -ForegroundColor Yellow
Start-Sleep -Seconds 3

Set-Location proxy-fhir
docker run --rm `
    --network="healthflowms_default" `
    -v "${PWD}:/usr/src" `
    maven:3.9-eclipse-temurin-17 `
    mvn clean verify sonar:sonar `
    -Dsonar.login="$SONAR_TOKEN" `
    -Dsonar.host.url="http://sonarqube:9000"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Proxy FHIR analysis complete" -ForegroundColor Green
} else {
    Write-Host "❌ Proxy FHIR analysis failed" -ForegroundColor Red
}
Set-Location ..

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  ✅ Analysis Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "View results at: " -ForegroundColor Blue -NoNewline
Write-Host "http://localhost:9000" -ForegroundColor Yellow
Write-Host ""
