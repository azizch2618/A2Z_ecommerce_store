#!/usr/bin/env bash
set -euo pipefail

echo "==> A2Z Tools — First-time setup"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

if [ ! -f frontend/.env.local ]; then
  cp frontend/.env.local.example frontend/.env.local
  echo "Created frontend/.env.local"
fi

if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "Created backend/.env"
fi

docker compose build
docker compose up -d db redis
echo "Waiting for PostgreSQL..."
sleep 5
docker compose run --rm api python manage.py migrate
echo "==> Setup complete. Run: docker compose up -d"
