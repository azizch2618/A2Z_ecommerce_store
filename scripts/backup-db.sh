#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

source .env 2>/dev/null || true

docker compose exec -T db pg_dump \
  -U "${POSTGRES_USER:-a2z}" \
  -d "${POSTGRES_DB:-a2z_tools}" \
  > "$BACKUP_DIR/a2z_tools_${TIMESTAMP}.sql"

echo "Backup saved to $BACKUP_DIR/a2z_tools_${TIMESTAMP}.sql"
