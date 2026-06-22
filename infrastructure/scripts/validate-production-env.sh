#!/usr/bin/env bash
# A2Z Tools — Validate production .env before deploy or go-live
# Usage: ./infrastructure/scripts/validate-production-env.sh [.env-file]

set -euo pipefail

ENV_FILE="${1:-.env}"
ERRORS=0
WARNINGS=0

fail() {
  echo "ERROR: $1" >&2
  ERRORS=$((ERRORS + 1))
}

warn() {
  echo "WARN:  $1" >&2
  WARNINGS=$((WARNINGS + 1))
}

require_var() {
  local name="$1"
  local value="${!name:-}"
  if [[ -z "${value}" ]]; then
    fail "${name} is required but empty"
  fi
}

require_not_placeholder() {
  local name="$1"
  local value="${!name:-}"
  if [[ -z "${value}" || "${value}" == change-me* || "${value}" == *change-me* ]]; then
    fail "${name} must be set to a production value (not placeholder)"
  fi
}

if [[ ! -f "${ENV_FILE}" ]]; then
  fail "Environment file not found: ${ENV_FILE}"
  exit 1
fi

echo "==> Validating ${ENV_FILE}"

# shellcheck disable=SC1090
set -a
source "${ENV_FILE}"
set +a

# Core Django
require_not_placeholder DJANGO_SECRET_KEY
require_var DJANGO_ALLOWED_HOSTS
require_var DJANGO_CORS_ALLOWED_ORIGINS
require_var CSRF_TRUSTED_ORIGINS

if [[ "${DJANGO_DEBUG:-False}" == "True" || "${DJANGO_DEBUG:-false}" == "true" ]]; then
  fail "DJANGO_DEBUG must be False in production"
fi

if [[ "${NEXT_PUBLIC_ADMIN_DEMO:-false}" == "true" ]]; then
  fail "NEXT_PUBLIC_ADMIN_DEMO must be false in production"
fi

# Database
require_not_placeholder POSTGRES_PASSWORD
require_var POSTGRES_DB
require_var POSTGRES_USER

# Redis / Celery
require_var REDIS_URL

# Public URLs
require_var NEXT_PUBLIC_API_URL
require_var NEXT_PUBLIC_SITE_URL
require_var NEXT_PUBLIC_ADMIN_URL

if [[ "${NEXT_PUBLIC_API_URL}" != https://* ]]; then
  warn "NEXT_PUBLIC_API_URL should use HTTPS in production"
fi

# Backups
if [[ -z "${BACKUP_S3_BUCKET:-}" ]]; then
  warn "BACKUP_S3_BUCKET not set — offsite backups disabled"
fi
if [[ -n "${BACKUP_S3_BUCKET:-}" && -z "${AWS_ACCESS_KEY_ID:-}" ]]; then
  warn "BACKUP_S3_BUCKET set but AWS credentials missing"
fi

# Observability
if [[ -z "${SENTRY_DSN:-}" ]]; then
  warn "SENTRY_DSN not set — error tracking disabled"
fi

# Email
if [[ -z "${EMAIL_HOST:-}" ]]; then
  warn "EMAIL_HOST not set — transactional email disabled"
fi

# Stripe (if ecommerce live)
if [[ -z "${STRIPE_SECRET_KEY:-}" ]]; then
  warn "STRIPE_SECRET_KEY not set — payments disabled"
fi

# JWT
if [[ -z "${JWT_COOKIE_DOMAIN:-}" ]]; then
  warn "JWT_COOKIE_DOMAIN not set — cross-subdomain auth may fail"
fi

echo ""
echo "Validation complete: ${ERRORS} error(s), ${WARNINGS} warning(s)"

if [[ "${ERRORS}" -gt 0 ]]; then
  exit 1
fi

exit 0
