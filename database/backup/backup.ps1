# Script de sauvegarde automatique de PostgreSQL pour HealthFlow-MS (Windows PowerShell)

# Configuration
$BackupDir = "C:\backups\healthflow"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DbName = "healthflow"
$DbUser = "healthflow"
$DbHost = "localhost"
$DbPort = "5432"
$RetentionDays = 7

# Créer le dossier de backup s'il n'existe pas
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force
}

# Nom du fichier de backup
$BackupFile = Join-Path $BackupDir "healthflow_backup_$Timestamp.sql"

# Effectuer la sauvegarde avec pg_dump
Write-Host "Starting backup at $(Get-Date)" -ForegroundColor Green

$env:PGPASSWORD = "healthflow123"
& pg_dump -h $DbHost -p $DbPort -U $DbUser -d $DbName -F c -f $BackupFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup successful: $BackupFile" -ForegroundColor Green
    
    # Compresser le backup avec 7-Zip ou PowerShell
    $CompressedFile = "$BackupFile.gz"
    $content = [System.IO.File]::ReadAllBytes($BackupFile)
    $compressed = [System.IO.Compression.GZipStream]::new(
        [System.IO.File]::Create($CompressedFile),
        [System.IO.Compression.CompressionLevel]::Optimal
    )
    $compressed.Write($content, 0, $content.Length)
    $compressed.Close()
    Remove-Item $BackupFile
    Write-Host "Backup compressed: $CompressedFile" -ForegroundColor Green
    
    # Supprimer les anciens backups (plus de 7 jours)
    $CutoffDate = (Get-Date).AddDays(-$RetentionDays)
    Get-ChildItem -Path $BackupDir -Filter "healthflow_backup_*.sql.gz" | 
        Where-Object { $_.LastWriteTime -lt $CutoffDate } | 
        Remove-Item -Force
    Write-Host "Old backups cleaned (older than $RetentionDays days)" -ForegroundColor Yellow
} else {
    Write-Host "Backup failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Backup completed at $(Get-Date)" -ForegroundColor Green

