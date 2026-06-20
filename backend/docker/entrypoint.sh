#!/bin/sh
set -e

wait_for_postgres() {
  echo "Waiting for PostgreSQL at ${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}..."
  python <<'PY'
import os
import sys
import time

import psycopg

host = os.environ.get("POSTGRES_HOST", "postgres")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
dbname = os.environ.get("POSTGRES_DB", "a2z_tools")
user = os.environ.get("POSTGRES_USER", "a2z")
password = os.environ.get("POSTGRES_PASSWORD", "")

for attempt in range(1, 61):
    try:
        with psycopg.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=3,
        ):
            print("PostgreSQL is ready.")
            sys.exit(0)
    except psycopg.OperationalError:
        if attempt == 60:
            print("PostgreSQL did not become ready in time.", file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
PY
}

if [ "${WAIT_FOR_POSTGRES:-true}" = "true" ]; then
  wait_for_postgres
fi

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Applying database migrations..."
  python manage.py migrate --noinput
fi

if [ "${COLLECT_STATIC:-false}" = "true" ]; then
  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi

exec "$@"
