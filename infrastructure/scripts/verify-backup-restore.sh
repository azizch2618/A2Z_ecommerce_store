#!/usr/bin/env bash
# A2Z Tools — Backup verification / restore drill (non-destructive by default)
# Usage:
#   ./infrastructure/scripts/verify-backup-restore.sh --check-latest
#   ./infrastructure/scripts/verify-backup-restore.sh --restore-test s3://bucket/postgres/daily/file.dump
#
# --check-latest: download latest S3 dump and validate pg_restore --list
# --restore-test:   restore to temporary database a2z_tools_dr_test then drop it

set -euo pipefail

MODE="${1:-}"
SOURCE="${2:-}"
CONTAINER="${POSTGRES_CONTAINER:-a2z-postgres}"
POSTGRES_USER="${POSTGRES_USER:-a2z}"
TEST_DB="a2z_tools_dr_test"
BUCKET="${BACKUP_S3_BUCKET:-a2z-tools-prod-backups}"

usage() {
  echo "Usage:"
  echo "  $0 --check-latest"
  echo "  $0 --restore-test <s3-uri-or-local-path>"
  exit 1
}

[[ -n "${MODE}" ]] || usage

if [[ "${MODE}" == "--check-latest" ]]; then
  if ! command -v aws &>/dev/null; then
    echo "ERROR: aws CLI required for --check-latest" >&2
    exit 1
  fi
  LATEST=$(aws s3 ls "s3://${BUCKET}/postgres/daily/" | sort | tail -1 | awk '{print $4}')
  if [[ -z "${LATEST}" ]]; then
    echo "ERROR: no backups found in s3://${BUCKET}/postgres/daily/" >&2
    exit 1
  fi
  LOCAL="/tmp/${LATEST}"
  aws s3 cp "s3://${BUCKET}/postgres/daily/${LATEST}" "${LOCAL}"
  docker exec -i "${CONTAINER}" pg_restore --list < "${LOCAL}" | head -20
  rm -f "${LOCAL}"
  echo "OK: backup ${LATEST} is readable"
  exit 0
fi

if [[ "${MODE}" == "--restore-test" ]]; then
  [[ -n "${SOURCE}" ]] || usage
  LOCAL="/tmp/a2z_dr_test_$(date +%s).dump"
  if [[ "${SOURCE}" == s3://* ]]; then
    aws s3 cp "${SOURCE}" "${LOCAL}"
  else
    cp "${SOURCE}" "${LOCAL}"
  fi

  docker exec -i "${CONTAINER}" dropdb -U "${POSTGRES_USER}" --if-exists "${TEST_DB}" 2>/dev/null || true
  docker exec -i "${CONTAINER}" createdb -U "${POSTGRES_USER}" "${TEST_DB}"
  docker exec -i "${CONTAINER}" pg_restore -U "${POSTGRES_USER}" -d "${TEST_DB}" --no-owner --role="${POSTGRES_USER}" < "${LOCAL}"

  ROWS=$(docker exec "${CONTAINER}" psql -U "${POSTGRES_USER}" -d "${TEST_DB}" -tAc "SELECT COUNT(*) FROM django_migrations" 2>/dev/null || echo "0")
  docker exec -i "${CONTAINER}" dropdb -U "${POSTGRES_USER}" --if-exists "${TEST_DB}"

  rm -f "${LOCAL}"
  echo "OK: restore test passed (django_migrations rows: ${ROWS})"
  exit 0
fi

usage
