.PHONY: help up down build logs shell-api shell-web migrate makemigrations test lint setup

help:
	@echo "A2Z Tools — Development Commands"
	@echo ""
	@echo "  make setup      First-time project setup"
	@echo "  make up         Start all services (Docker)"
	@echo "  make down       Stop all services"
	@echo "  make build      Rebuild Docker images"
	@echo "  make logs       Tail service logs"
	@echo "  make migrate    Run Django migrations"
	@echo "  make makemigrations  Create Django migrations"
	@echo "  make shell-api  Django shell"
	@echo "  make shell-web  Frontend shell"
	@echo "  make test       Run backend and frontend tests"
	@echo "  make lint       Run linters"

setup:
	cp -n .env.example .env 2>/dev/null || true
	cp -n frontend/.env.local.example frontend/.env.local 2>/dev/null || true
	cp -n backend/.env.example backend/.env 2>/dev/null || true
	docker compose build
	docker compose up -d db redis
	@echo "Waiting for database..."
	sleep 5
	docker compose run --rm api python manage.py migrate
	@echo "Setup complete. Run 'make up' to start all services."

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

migrate:
	docker compose exec api python manage.py migrate

makemigrations:
	docker compose exec api python manage.py makemigrations

shell-api:
	docker compose exec api python manage.py shell

shell-web:
	docker compose exec web sh

test:
	docker compose exec api pytest
	docker compose exec web npm run test --if-present

lint:
	docker compose exec api ruff check .
	docker compose exec web npm run lint --if-present
