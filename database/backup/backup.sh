#!/bin/bash
# Script de sauvegarde automatique de PostgreSQL pour HealthFlow-MS

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="healthflow"
DB_USER="healthflow"
DB_HOST="postgres"
RETENTION_DAYS=7

# Créer le dossier de backup s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Nom du fichier de backup
BACKUP_FILE="$BACKUP_DIR/healthflow_backup_$TIMESTAMP.sql"

# Effectuer la sauvegarde
echo "Starting backup at $(date)"
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -F c -f "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
    
    # Compresser le backup
    gzip "$BACKUP_FILE"
    echo "Backup compressed: ${BACKUP_FILE}.gz"
    
    # Supprimer les anciens backups (plus de 7 jours)
    find "$BACKUP_DIR" -name "healthflow_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo "Old backups cleaned (older than $RETENTION_DAYS days)"
else
    echo "Backup failed!"
    exit 1
fi

echo "Backup completed at $(date)"

