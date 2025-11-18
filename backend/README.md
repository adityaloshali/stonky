# Stonky Backend (FastAPI)

AI-Augmented Stock Analysis Platform for Indian Markets (NSE/BSE)

## Architecture

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with pgvector
- **Cache**: Redis 7+
- **Task Queue**: Celery
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings (Pydantic)
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── logging.py       # Loguru config
│   │   └── dependencies.py  # DI containers
│   ├── api/v1/              # REST API endpoints
│   ├── services/            # External data sources
│   ├── engines/             # Analysis logic
│   ├── repositories/        # Database access
│   ├── models/              # SQLAlchemy models
│   ├── workers/             # Celery tasks
│   └── utils/               # Utilities
├── migrations/              # Alembic migrations
├── tests/                   # Tests
├── scripts/                 # Utility scripts
├── pyproject.toml           # Poetry dependencies
└── alembic.ini              # Alembic config
```

## Prerequisites

- Python 3.11 or higher
- Poetry (package manager)
- PostgreSQL 15+
- Redis 7+

### Install Python 3.11 (if needed)

```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv

# Windows
# Download from python.org
```

### Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
poetry install
```

### 2. Set Up Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Required Environment Variables:**

```bash
# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/stonky

# Redis
REDIS_URL=redis://localhost:6379/0

# Screener.in Cookie (REQUIRED for 10-year fundamentals)
SCREENER_COOKIE=your_session_cookie_here
```

**Getting Screener.in Cookie:**

1. Login to [Screener.in](https://www.screener.in) in your browser
2. Open DevTools (F12) → Application → Cookies
3. Find `sessionid` cookie
4. Copy the value
5. Paste in `.env` as `SCREENER_COOKIE`

### 3. Start PostgreSQL and Redis

**Using Docker:**

```bash
# PostgreSQL
docker run -d \
  --name stonky-postgres \
  -e POSTGRES_DB=stonky \
  -e POSTGRES_USER=stonky \
  -e POSTGRES_PASSWORD=stonky \
  -p 5432:5432 \
  postgres:15

# Redis
docker run -d \
  --name stonky-redis \
  -p 6379:6379 \
  redis:7
```

**Or install locally:**

```bash
# macOS
brew install postgresql@15 redis
brew services start postgresql@15
brew services start redis

# Ubuntu
sudo apt install postgresql-15 redis-server
sudo systemctl start postgresql redis
```

### 4. Run Migrations

```bash
# Create initial migration
poetry run alembic revision --autogenerate -m "Initial migration"

# Apply migrations
poetry run alembic upgrade head
```

### 5. Start FastAPI Server

```bash
# Development (with auto-reload)
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the shorthand
poetry run uvicorn app.main:app --reload
```

**Server will start at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

### 6. Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "environment": "development",
#   "version": "2.0.0",
#   "features": {
#     "screener_configured": true,
#     "ai_configured": false
#   }
# }
```

## Development Workflow

### Running Services in Parallel

You'll need multiple terminal windows:

```bash
# Terminal 1: FastAPI
poetry run uvicorn app.main:app --reload

# Terminal 2: Celery Worker (when implemented)
poetry run celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3: Redis (if not using Docker)
redis-server

# Terminal 4: PostgreSQL (if not using Docker)
postgres -D /usr/local/var/postgresql@15
```

### Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "Add new table"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history

# View current version
poetry run alembic current
```

### Code Quality

```bash
# Format code with Black
poetry run black app/

# Lint with Ruff
poetry run ruff check app/

# Type check with mypy
poetry run mypy app/

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app tests/
```

## Testing

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/unit/test_company_repository.py

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=app --cov-report=html
```

## API Documentation

### Interactive Docs

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Key Endpoints (Planned)

```
GET  /health                     - Health check
GET  /api/v1/search?q=RELIANCE   - Symbol search
GET  /api/v1/company/{symbol}    - Company details
GET  /api/v1/analyze/{symbol}    - Full analysis
GET  /api/v1/prices/{symbol}     - Historical prices
GET  /api/v1/news/{symbol}       - Latest news
```

## Configuration

All configuration is in `app/core/config.py` using Pydantic Settings.

**Key Settings:**

- `ENV`: Environment (development/staging/production)
- `DEBUG`: Enable debug mode
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SCREENER_COOKIE`: Screener.in session cookie
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `CACHE_TTL_*`: Cache TTL for different data types

## Troubleshooting

### Database Connection Errors

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check connection with psql
psql -h localhost -U stonky -d stonky
```

### Redis Connection Errors

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### Import Errors

```bash
# Ensure you're in the backend directory
cd backend

# Activate Poetry shell
poetry shell

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Migration Errors

```bash
# If migrations are out of sync, reset:
poetry run alembic downgrade base
poetry run alembic upgrade head
```

## Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install gunicorn
poetry add gunicorn

# Run with 4 workers
poetry run gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Environment Variables for Production

```bash
ENV=production
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=<generate-with-openssl-rand-hex-32>
```

### Docker Deployment (Future)

```dockerfile
# Dockerfile (to be created)
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY . .
CMD ["poetry", "run", "gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

## Next Steps

1. ✅ **Phase 1 Complete**: Foundation is set up
2. ⏳ **Phase 2**: Build data services (Screener, NSE, Yahoo)
3. ⏳ **Phase 3**: Implement analysis engines
4. ⏳ **Phase 4**: Create API endpoints
5. ⏳ **Phase 5**: Integrate with frontend

See [Implementation Plan](../docs/implementation-plan.md) for details.

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [Poetry Docs](https://python-poetry.org/docs/)
- [Architecture Design](../docs/architecture.md)

## Support

For issues or questions:
- Check [Implementation Plan](../docs/implementation-plan.md)
- Review [Architecture Design](../docs/architecture.md)
- Open an issue on GitHub
