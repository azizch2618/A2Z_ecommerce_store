#!/usr/bin/env bash
# A2Z Tools — Restore PostgreSQL from S3 dump (disaster recovery)
# Usage: ./infrastructure/scripts/restore-postgres.sh s3://bucket/postgres/daily/file.dump
# WARNING: Destructive — drops and recreates target database objects.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <s3-uri-or-local-path>" >&2
  exit 1
fi

SOURCE="$1"
CONTAINER="${POSTGRES_CONTAINER:-a2z-postgres}"
POSTGRES_USER="${POSTGRES_USER:-a2z}"
POSTGRES_DB="${POSTGRES_DB:-a2z_tools}"
LOCAL="/tmp/a2z_restore_$(date +%s).dump"

echo "==> A2Z Tools PostgreSQL restore"
echo "    Source: ${SOURCE}"
echo "    Target: ${CONTAINER}/${POSTGRES_DB}"

read -r -p "This will overwrite database ${POSTGRES_DB}. Continue? [y/N] " confirm
if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

if [[ "${SOURCE}" == s3://* ]]; then
  aws s3 cp "${SOURCE}" "${LOCAL}"
else
  cp "${SOURCE}" "${LOCAL}"
fi

echo "==> Stopping writers (backend + celery)"
docker stop a2z-backend a2z-celery a2z-celery-beat 2>/dev/null || true

echo "==> Restoring"
docker exec -i "${CONTAINER}" dropdb -U "${POSTGRES_USER}" --if-exists "${POSTGRES_DB}"
docker exec -i "${CONTAINER}" createdb -U "${POSTGRES_USER}" "${POSTGRES_DB}"
docker exec -i "${CONTAINER}" pg_restore -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --no-owner --role="${POSTGRES_USER}" < "${LOCAL}"

rm -f "${LOCAL}"

echo "==> Restarting application stack"
docker start a2z-backend 2>/dev/null || true
docker start a2z-celery a2z-celery-beat 2>/dev/null || true

echo "==> Verify: curl https://api.a2ztools.com/api/v1/ready/"
echo "Restore complete."
