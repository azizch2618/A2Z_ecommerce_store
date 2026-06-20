#!/usr/bin/env bash
# Seed demo data for client presentations
set -euo pipefail
cd "$(dirname "$0")/../backend"
python manage.py seed_demo "$@"
