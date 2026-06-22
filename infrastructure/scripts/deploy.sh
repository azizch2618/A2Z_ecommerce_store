#!/usr/bin/env bash
# A2Z Tools — Production deploy on origin host
# Usage: ./infrastructure/scripts/deploy.sh [git-ref]
# Requires: docker compose, .env with production secrets

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

GIT_REF="${1:-main}"
COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"
PROFILES="--profile proxy --profile workers"

echo "==> A2Z Tools deploy (ref: ${GIT_REF})"

if [[ ! -f .env ]]; then
  echo "ERROR: .env not found. Copy .env.production.example and fill secrets." >&2
  exit 1
fi

# shellcheck disable=SC1091
set -a
source .env
set +a

if [[ -z "${DJANGO_SECRET_KEY:-}" || "${DJANGO_SECRET_KEY}" == change-me* ]]; then
  echo "ERROR: DJANGO_SECRET_KEY must be set to a strong random value." >&2
  exit 1
fi

if [[ "${NEXT_PUBLIC_ADMIN_DEMO:-false}" == "true" ]]; then
  echo "ERROR: NEXT_PUBLIC_ADMIN_DEMO must be false in production." >&2
  exit 1
fi

echo "==> Validating production environment"
chmod +x infrastructure/scripts/validate-production-env.sh
./infrastructure/scripts/validate-production-env.sh .env

echo "==> Fetching ${GIT_REF}"
git fetch origin
git checkout "${GIT_REF}"
git pull --ff-only origin "${GIT_REF}" 2>/dev/null || true

PRE_DEPLOY_DUMP="${RUN_PRE_DEPLOY_BACKUP:-true}"
if [[ "${PRE_DEPLOY_DUMP}" == "true" ]]; then
  echo "==> Pre-deploy database backup"
  POSTGRES_CONTAINER=a2z-postgres ./infrastructure/scripts/backup-postgres.sh \
    || echo "WARN: pre-deploy backup failed — continue only if intentional"
fi

if [[ -n "${BACKEND_IMAGE:-}" && -n "${FRONTEND_IMAGE:-}" ]]; then
  echo "==> Pulling images"
  docker pull "${BACKEND_IMAGE}"
  docker pull "${FRONTEND_IMAGE}"
  ${COMPOSE} ${PROFILES} up -d --no-build
else
  echo "==> Building images locally"
  ${COMPOSE} ${PROFILES} up -d --build
fi

echo "==> Waiting for API readiness"
for i in $(seq 1 30); do
  if docker exec a2z-backend curl -fsS "http://localhost:8000/api/v1/ready/" >/dev/null 2>&1; then
    echo "API ready."
    break
  fi
  if [[ "${i}" -eq 30 ]]; then
    echo "ERROR: API did not become ready in time." >&2
    ${COMPOSE} logs --tail=80 backend
    exit 1
  fi
  sleep 5
done

echo "==> Deploy complete ($(git rev-parse --short HEAD))"
