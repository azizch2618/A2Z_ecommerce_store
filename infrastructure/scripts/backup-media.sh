#!/usr/bin/env bash
# A2Z Tools — Media volume backup to S3
# Usage: ./infrastructure/scripts/backup-media.sh
# Backs up Django media files from the backend_media Docker volume.

set -euo pipefail

BUCKET="${BACKUP_S3_BUCKET:-a2z-tools-prod-backups}"
VOLUME="${MEDIA_VOLUME:-a2z-tools_backend_media}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE="/tmp/a2z_media_${TIMESTAMP}.tar.gz"

echo "Starting media backup: ${ARCHIVE}"

docker run --rm \
  -v "${VOLUME}:/media:ro" \
  -v "/tmp:/backup" \
  alpine:3.20 \
  tar czf "/backup/a2z_media_${TIMESTAMP}.tar.gz" -C /media .

if command -v aws &>/dev/null && [[ -n "${BACKUP_S3_BUCKET:-}" ]]; then
  aws s3 cp "${ARCHIVE}" "s3://${BUCKET}/media/daily/a2z_media_${TIMESTAMP}.tar.gz"
  echo "Uploaded to s3://${BUCKET}/media/daily/"
  rm -f "${ARCHIVE}"
else
  echo "Archive saved locally: ${ARCHIVE}"
fi

echo "Media backup complete."
