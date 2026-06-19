#!/usr/bin/env bash
# Daily PostgreSQL backup — add to cron:
#   0 3 * * * /home/miabot/mia-snow-bot/deploy/backup.sh >> /var/log/miabot-backup.log 2>&1

set -euo pipefail

BACKUP_DIR="/home/miabot/backups"
DB_NAME="miasnow"
DB_USER="miabot"
KEEP_DAYS=14

mkdir -p "$BACKUP_DIR"

FILENAME="${BACKUP_DIR}/${DB_NAME}_$(date +%Y%m%d_%H%M%S).dump"
pg_dump -U "$DB_USER" -Fc "$DB_NAME" > "$FILENAME"

echo "$(date) — backup written to $FILENAME ($(du -sh "$FILENAME" | cut -f1))"

# Remove backups older than KEEP_DAYS
find "$BACKUP_DIR" -name "${DB_NAME}_*.dump" -mtime "+${KEEP_DAYS}" -delete
echo "$(date) — pruned backups older than ${KEEP_DAYS} days"
