# Stonky

## Overview
Stonky is an AI‑augmented stock‑analysis platform built with FastAPI, PostgreSQL, and Redis. The backend provides data ingestion, analysis engines, and a clean REST API.

## Prerequisites
- **Docker** (for PostgreSQL & Redis containers)
- **Poetry** (dependency management)
- **Python 3.13**

## Setup

### 1️⃣ Clone the repository & install dependencies
```bash
git clone <your-repo-url>
cd StockAnalysisApp/backend
poetry install
```

### 2️⃣ Run Docker containers
```bash
# PostgreSQL
docker run -d --name stonky-postgres \
  -e POSTGRES_DB=stonky \
  -e POSTGRES_USER=stonky \
  -e POSTGRES_PASSWORD=stonky \
  -p 5432:5432 postgres:15

# Redis
docker run -d --name stonky-redis \
  -p 6379:6379 redis:7
```

### 3️⃣ Apply database migrations
```bash
poetry run alembic upgrade head
```

### 4️⃣ Start the FastAPI server (development mode)
```bash
poetry run uvicorn app.main:app --reload
```

## Verification

### PostgreSQL
```bash
PGPASSWORD=stonky psql -h 127.0.0.1 -U stonky -d stonky -c "\dt"
```

### Redis
```bash
redis-cli -h 127.0.0.1 -p 6379 ping
```

### API health check
```bash
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

If everything is set up correctly you should see a JSON response indicating the service is healthy.

## License
MIT