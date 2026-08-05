#!/bin/bash
# ═══════════════════════════════════════════════════════
# HiddenYatra — Automated MySQL Backup Script
# Place at: /opt/scripts/backup_hiddenyatra.sh
# Cron:     0 2 * * * /opt/scripts/backup_hiddenyatra.sh >> /var/log/hiddenyatra/backup.log 2>&1
# ═══════════════════════════════════════════════════════

set -euo pipefail

# ── Configuration ──
DB_NAME="hiddenyatra"
DB_USER="hiddenyatra_app"
DB_PASS="${DB_PASSWORD:-}"
BACKUP_DIR="/var/backups/hiddenyatra"
UPLOAD_DIR="/var/www/hiddenyatra/static/uploads"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

# ── Create backup directory ──
mkdir -p "$BACKUP_DIR"

echo "[$DATE] Starting HiddenYatra backup..."

# ── Database Backup ──
echo "  Backing up MySQL database..."
mysqldump \
    -u "$DB_USER" \
    -p"$DB_PASS" \
    --single-transaction \
    --routines \
    --triggers \
    --quick \
    "$DB_NAME" | gzip > "$BACKUP_DIR/db_${DATE}.sql.gz"

DB_SIZE=$(du -h "$BACKUP_DIR/db_${DATE}.sql.gz" | cut -f1)
echo "  ✓ Database backup: $DB_SIZE"

# ── Upload Files Backup ──
if [ -d "$UPLOAD_DIR" ] && [ "$(ls -A $UPLOAD_DIR 2>/dev/null)" ]; then
    echo "  Backing up uploads..."
    tar czf "$BACKUP_DIR/uploads_${DATE}.tar.gz" -C "$UPLOAD_DIR" .
    UPL_SIZE=$(du -h "$BACKUP_DIR/uploads_${DATE}.tar.gz" | cut -f1)
    echo "  ✓ Uploads backup: $UPL_SIZE"
else
    echo "  ℹ No uploads to backup"
fi

# ── Cleanup Old Backups ──
DELETED=$(find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
echo "  ✓ Cleaned up $DELETED old backup(s) (>${RETENTION_DAYS} days)"

# ── Verify Latest Backup ──
LATEST=$(ls -t "$BACKUP_DIR"/db_*.sql.gz 2>/dev/null | head -1)
if [ -n "$LATEST" ] && [ -s "$LATEST" ]; then
    echo "  ✓ Backup verified: $LATEST"
else
    echo "  ✗ ERROR: Backup verification failed!"
    exit 1
fi

echo "[$DATE] Backup completed successfully."
