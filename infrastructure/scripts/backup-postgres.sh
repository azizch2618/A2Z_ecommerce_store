#!/bin/bash
# A2Z Tools — PostgreSQL backup to S3
# Usage: ./infrastructure/scripts/backup-postgres.sh
# Requires: docker, aws cli, env POSTGRES_USER POSTGRES_DB

set -euo pipefail

CONTAINER="${POSTGRES_CONTAINER:-a2z-postgres}"
BUCKET="${BACKUP_S3_BUCKET:-a2z-tools-prod-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE="a2z_tools_${TIMESTAMP}.dump"

echo "Starting backup: ${FILE}"

docker exec "${CONTAINER}" pg_dump -U "${POSTGRES_USER}" -Fc "${POSTGRES_DB}" > "/tmp/${FILE}"

if command -v aws &>/dev/null; then
  aws s3 cp "/tmp/${FILE}" "s3://${BUCKET}/postgres/daily/${FILE}"
  echo "Uploaded to s3://${BUCKET}/postgres/daily/${FILE}"
else
  echo "aws CLI not found — backup saved locally: /tmp/${FILE}"
fi

rm -f "/tmp/${FILE}"
echo "Backup complete."
