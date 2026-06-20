# A2Z Tools

Australian Hardware & Networking Ecommerce Platform for trade professionals, contractors, businesses, and DIY customers.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, TypeScript, TailwindCSS, ShadCN UI |
| Backend | Django 5, Django REST Framework |
| Database | PostgreSQL 16 |
| Cache / Queue | Redis, Celery |
| Containers | Docker, Docker Compose |

## Project Structure

```
a2z-tools/
├── docs/                  # Architecture & planning documentation
├── frontend/              # Next.js 15 application
├── backend/               # Django + DRF API
├── infrastructure/        # Nginx, Terraform, Kubernetes (future)
├── scripts/               # Dev & ops helper scripts
├── docker-compose.yml     # Local development stack
└── Makefile               # Common dev commands
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 24+
- [Docker Compose](https://docs.docker.com/compose/) v2+
- [Make](https://gnuwin32.sourceforge.net/packages/make.htm) (optional, Windows: use Git Bash or WSL)

For local development without Docker:

- Node.js 20+
- Python 3.12+
- PostgreSQL 16+
- Redis 7+

## Quick Start (Docker)

```bash
# 1. Clone and configure
git clone <repository-url> a2z-tools
cd a2z-tools
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
cp backend/.env.example backend/.env

# 2. First-time setup
make setup

# 3. Start all services
make up
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000/api/v1 |
| API Health | http://localhost:8000/api/v1/health/ |
| Django Admin | http://localhost:8000/admin/ |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## Development Commands

```bash
make up              # Start services
make down            # Stop services
make logs            # Tail logs
make migrate         # Run Django migrations
make makemigrations  # Create migrations
make shell-api       # Django shell
make test            # Run tests
make lint            # Run linters
```

## Documentation

| Document | Description |
|----------|-------------|
| [Project Master Plan](docs/PROJECT_MASTER_PLAN.md) | Architecture, features, roadmap |
| [Database Plan](docs/DATABASE_PLAN.md) | PostgreSQL schema design |
| [UI Design System](docs/UI_DESIGN_SYSTEM.md) | Brand, components, accessibility |
| [API Specification](docs/API_SPECIFICATION.md) | REST API endpoints |
| [Project Structure](docs/PROJECT_STRUCTURE.md) | Folder layout reference |

## Environment Variables

Copy `.env.example` to `.env` at the project root. Service-specific overrides:

- `frontend/.env.local` — Next.js public env vars
- `backend/.env` — Django settings overrides

Never commit `.env` files containing secrets.

## Australian Market

- Currency: AUD (integer cents in API)
- Tax: GST 10%
- Business IDs: ABN support for trade accounts
- Addresses: Australian state/postcode format

## License

Proprietary — All rights reserved.
