#!/usr/bin/env bash
# A2Z Tools backend test runner — PostgreSQL (CI) or SQLite (fast local).
#
# Usage:
#   ./scripts/run-tests.sh smoke              # fast local (SQLite)
#   ./scripts/run-tests.sh integration        # single group
#   ./scripts/run-tests.sh all                # full suite
#   TEST_DB=postgres ./scripts/run-tests.sh all   # PostgreSQL mode
#   ./scripts/run-tests.sh ci                 # CI sequence with JUnit + coverage
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
REPORTS="$BACKEND/reports"
GROUP="${1:-all}"

cd "$BACKEND"
mkdir -p "$REPORTS"

if [[ "${TEST_DB:-sqlite}" == "postgres" ]]; then
  export USE_SQLITE_FOR_TESTS=0
  export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
  export POSTGRES_DB="${POSTGRES_DB:-a2z_tools_test}"
  export POSTGRES_USER="${POSTGRES_USER:-a2z}"
  export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-changeme}"
  export POSTGRES_TEST_DB="${POSTGRES_TEST_DB:-test_a2z_tools}"
  echo "==> Waiting for PostgreSQL (${POSTGRES_HOST})..."
  python scripts/wait_for_postgres.py
  REUSE_DB_FLAG="--reuse-db"
else
  export USE_SQLITE_FOR_TESTS=1
  REUSE_DB_FLAG=""
  echo "==> SQLite in-memory mode (set TEST_DB=postgres for PostgreSQL)"
fi

export DJANGO_SETTINGS_MODULE=config.settings.test

run_group() {
  local marker="$1"
  local junit="$2"
  echo ""
  echo "==> Running ${marker} tests..."
  pytest -m "$marker" $REUSE_DB_FLAG --junitxml="$junit" -q
}

run_ci() {
  echo "==> Django system check"
  python manage.py check

  run_group smoke "$REPORTS/junit-smoke.xml"
  run_group security "$REPORTS/junit-security.xml"
  run_group regression "$REPORTS/junit-regression.xml"
  run_group integration "$REPORTS/junit-integration.xml"

  echo ""
  echo "==> Full suite with coverage (excluding slow)..."
  pytest -m "not slow" $REUSE_DB_FLAG \
    --cov=apps --cov=api --cov=config \
    --cov-report=term-missing:skip-covered \
    --cov-report=xml:"$REPORTS/coverage.xml" \
    --cov-report=html:"$REPORTS/htmlcov" \
    --junitxml="$REPORTS/junit-full.xml" \
    -q

  echo ""
  echo "Reports: $REPORTS/"
}

case "$GROUP" in
  smoke|integration|regression|security)
    run_group "$GROUP" "$REPORTS/junit-${GROUP}.xml"
    ;;
  slow)
    pytest -m slow $REUSE_DB_FLAG --junitxml="$REPORTS/junit-slow.xml" -q
    ;;
  all)
    pytest -m "not slow" $REUSE_DB_FLAG \
      --cov=apps --cov=api --cov=config \
      --cov-report=term-missing:skip-covered \
      --cov-report=xml:"$REPORTS/coverage.xml" \
      -q
    ;;
  ci)
    run_ci
    ;;
  *)
    echo "Unknown group: $GROUP" >&2
    echo "Valid: smoke | integration | regression | security | slow | all | ci" >&2
    exit 1
    ;;
esac
