#!/usr/bin/env python3
"""Block until PostgreSQL accepts connections (CI/local bootstrap helper)."""
from __future__ import annotations

import os
import sys
import time

try:
    import psycopg
except ImportError:  # pragma: no cover
    print("psycopg is required: pip install psycopg[binary]", file=sys.stderr)
    sys.exit(1)

HOST = os.environ.get("POSTGRES_HOST", "localhost")
PORT = os.environ.get("POSTGRES_PORT", "5432")
USER = os.environ.get("POSTGRES_USER", "a2z")
PASSWORD = os.environ.get("POSTGRES_PASSWORD", "changeme")
DB = os.environ.get("POSTGRES_DB", "a2z_tools_test")
TIMEOUT = int(os.environ.get("POSTGRES_WAIT_TIMEOUT", "60"))
INTERVAL = float(os.environ.get("POSTGRES_WAIT_INTERVAL", "1"))


def main() -> int:
    deadline = time.monotonic() + TIMEOUT
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            with psycopg.connect(
                host=HOST,
                port=PORT,
                user=USER,
                password=PASSWORD,
                dbname=DB,
                connect_timeout=5,
            ) as conn:
                conn.execute("SELECT 1")
            print(f"PostgreSQL ready at {HOST}:{PORT}/{DB}")
            return 0
        except Exception as exc:  # noqa: BLE001 — retry until timeout
            last_error = exc
            time.sleep(INTERVAL)

    print(
        f"PostgreSQL not ready after {TIMEOUT}s ({HOST}:{PORT}/{DB}): {last_error}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
