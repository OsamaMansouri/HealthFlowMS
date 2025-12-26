# HealthFlowMS Jenkins Helper Script (PowerShell)
# This script provides convenient commands for Jenkins operations

$ErrorActionPreference = "Stop"

# Jenkins configuration
$JENKINS_URL = "http://localhost:8088"
$JENKINS_CONTAINER = "healthflow-jenkins"

function Print-Header {
    param($Message)
    Write-Host "================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "================================" -ForegroundColor Blue
}

function Print-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Print-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Print-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Show-Usage {
    Write-Host @"
🚀 HealthFlowMS Jenkins Helper

Usage: .\jenkins.ps1 [COMMAND]

Commands:
    start           Start Jenkins service
    stop            Stop Jenkins service
    restart         Restart Jenkins service
    status          Show Jenkins status
    logs            View Jenkins logs
    rebuild         Rebuild Jenkins Docker image
    password        Get initial admin password
    url             Show Jenkins URL
    health          Check Jenkins health
    plugins         List installed plugins
    backup          Backup Jenkins data
    help            Show this help message

Examples:
    .\jenkins.ps1 start
    .\jenkins.ps1 logs
    .\jenkins.ps1 status

"@
}

function Start-JenkinsService {
    Print-Header "Starting Jenkins"
    docker-compose up -d jenkins
    Print-Success "Jenkins is starting..."
    Write-Host "Waiting for Jenkins to be ready..."
    Start-Sleep -Seconds 10
    Test-JenkinsHealth
    Print-Success "Jenkins URL: $JENKINS_URL"
}

function Stop-JenkinsService {
    Print-Header "Stopping Jenkins"
    docker-compose stop jenkins
    Print-Success "Jenkins stopped"
}

function Restart-JenkinsService {
    Print-Header "Restarting Jenkins"
    docker-compose restart jenkins
    Print-Success "Jenkins restarted"
    Write-Host "Waiting for Jenkins to be ready..."
    Start-Sleep -Seconds 10
    Test-JenkinsHealth
}

function Get-JenkinsStatus {
    Print-Header "Jenkins Status"
    docker-compose ps jenkins
    
    $running = docker ps --filter "name=$JENKINS_CONTAINER" --format "{{.Names}}"
    if ($running) {
        Print-Success "Jenkins is running"
        Write-Host ""
        Write-Host "📊 Container Stats:"
        docker stats --no-stream $JENKINS_CONTAINER
    }
    else {
        Print-Error "Jenkins is not running"
    }
}

function Get-JenkinsLogs {
    Print-Header "Jenkins Logs (Ctrl+C to exit)"
    docker-compose logs -f jenkins
}

function Rebuild-Jenkins {
    Print-Header "Rebuilding Jenkins Image"
    Print-Warning "This will stop Jenkins and rebuild the Docker image"
    $response = Read-Host "Continue? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        docker-compose build jenkins
        docker-compose up -d jenkins
        Print-Success "Jenkins image rebuilt and started"
    }
    else {
        Print-Warning "Rebuild cancelled"
    }
}

function Get-AdminPassword {
    Print-Header "Initial Admin Password"
    $running = docker ps --filter "name=$JENKINS_CONTAINER" --format "{{.Names}}"
    if ($running) {
        try {
            $password = docker exec $JENKINS_CONTAINER cat /var/jenkins_home/secrets/initialAdminPassword 2>$null
            if ($password) {
                Print-Success "Initial Admin Password: $password"
            }
            else {
                Print-Warning "Password file not found (Jenkins may be configured via JCasC)"
                Print-Success "Default credentials: admin / admin123"
            }
        }
        catch {
            Print-Warning "Password file not found (Jenkins may be configured via JCasC)"
            Print-Success "Default credentials: admin / admin123"
        }
    }
    else {
        Print-Error "Jenkins container is not running"
    }
}

function Show-JenkinsUrl {
    Print-Header "Jenkins URL"
    Write-Host "🌐 Jenkins UI: $JENKINS_URL"
    Write-Host "🔧 Jenkins API: $JENKINS_URL/api"
    Write-Host "📘 Blue Ocean: $JENKINS_URL/blue"
}

function Test-JenkinsHealth {
    try {
        $response = Invoke-WebRequest -Uri "$JENKINS_URL/login" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Print-Success "Jenkins is healthy (HTTP $($response.StatusCode))"
            return $true
        }
    }
    catch {
        Print-Error "Jenkins is not ready"
        return $false
    }
}

function Get-InstalledPlugins {
    Print-Header "Installed Jenkins Plugins"
    $running = docker ps --filter "name=$JENKINS_CONTAINER" --format "{{.Names}}"
    if ($running) {
        docker exec $JENKINS_CONTAINER ls /var/jenkins_home/plugins/ | ForEach-Object { $_ -replace '.jpi$', '' } | Sort-Object
    }
    else {
        Print-Error "Jenkins container is not running"
    }
}

function Backup-JenkinsData {
    Print-Header "Backing up Jenkins Data"
    $backupDir = ".\jenkins_backup"
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "jenkins_backup_$timestamp.tar.gz"
    
    if (!(Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir | Out-Null
    }
    
    Write-Host "Creating backup: $backupFile"
    docker run --rm `
        -v healthflowms_jenkins_data:/data `
        -v "${PWD}/${backupDir}:/backup" `
        alpine tar czf "/backup/$backupFile" -C /data .
    
    Print-Success "Backup created: $backupDir\$backupFile"
    $size = (Get-Item "$backupDir\$backupFile").Length / 1MB
    Write-Host "Backup size: $([math]::Round($size, 2)) MB"
}

# Main command handler
param(
    [Parameter(Position = 0)]
    [string]$Command = "help"
)

switch ($Command.ToLower()) {
    "start" { Start-JenkinsService }
    "stop" { Stop-JenkinsService }
    "restart" { Restart-JenkinsService }
    "status" { Get-JenkinsStatus }
    "logs" { Get-JenkinsLogs }
    "rebuild" { Rebuild-Jenkins }
    "password" { Get-AdminPassword }
    "url" { Show-JenkinsUrl }
    "health" { Test-JenkinsHealth }
    "plugins" { Get-InstalledPlugins }
    "backup" { Backup-JenkinsData }
    default { Show-Usage }
}
