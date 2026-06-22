#!/usr/bin/env bash
# A2Z Tools — Redis RDB backup to S3
# Usage: ./infrastructure/scripts/backup-redis.sh
# Requires: docker, aws cli (optional), REDIS_CONTAINER env

set -euo pipefail

CONTAINER="${REDIS_CONTAINER:-a2z-redis}"
BUCKET="${BACKUP_S3_BUCKET:-a2z-tools-prod-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE="redis_${TIMESTAMP}.rdb"
LOCAL="/tmp/${FILE}"

echo "Starting Redis backup: ${FILE}"

docker exec "${CONTAINER}" redis-cli BGSAVE
sleep 2

docker cp "${CONTAINER}:/data/dump.rdb" "${LOCAL}"

if command -v aws &>/dev/null && [[ -n "${BACKUP_S3_BUCKET:-}" ]]; then
  aws s3 cp "${LOCAL}" "s3://${BUCKET}/redis/daily/${FILE}"
  echo "Uploaded to s3://${BUCKET}/redis/daily/${FILE}"
else
  echo "Backup saved locally: ${LOCAL}"
fi

rm -f "${LOCAL}"
echo "Redis backup complete."
