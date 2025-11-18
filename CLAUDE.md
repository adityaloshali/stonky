# CLAUDE.md

**Project:** Stonky (AlphaGaze) - AI-Augmented Stock Analysis Platform
**Version:** 2.0 (FastAPI Migration)
**Last Updated:** 2025-11-18

---

## Quick Reference

**📋 Detailed Documentation:**
- [Architecture Design](./docs/architecture.md) - System design, patterns, tech stack
- [Implementation Plan](./docs/implementation-plan.md) - Week-by-week migration tasks
- [Product Vision](./docs/plan-final.md) - AlphaGaze master plan
- [Technical Approach](./docs/tech-plan-brief.md) - Free data scraping methods

---

## Project Overview

**Mission:** Build "The depth of a Hedge Fund Analyst, the speed of a click"

Stonky analyzes Indian stocks (NSE/BSE) using the **Refined Framework 2025** - a 7-step investment checklist combining:
- **Hard Data**: 10-year financials, shareholding patterns, live prices
- **Soft Analysis**: AI-powered reading of Annual Reports and concall transcripts (RAG)
- **Quantitative Scoring**: HQSF (High Quality, Safe, Fairly Priced) rating

---

## Current State vs. Target

### ✅ Implemented (MVP)
- Stock symbol search (Yahoo Finance)
- 1-year historical prices
- News aggregation (Google RSS)
- Basic AI endpoints (OpenAI/OpenRouter)
- Dark mode UI
- Bookmark system (localStorage)

### 🚧 In Progress (Migration)
**We are migrating from Next.js + Hono to Next.js + FastAPI**

**Reason:** The "Refined Framework" requires:
- 10-year financial analysis (pandas/numpy)
- Screener.in scraping (Python)
- RAG pipeline (LangChain, vector embeddings)
- Sector-specific strategies (Python design patterns)

### 🎯 Target Architecture

```
Next.js Frontend (Pure UI)
       ↓ HTTP REST
FastAPI Backend (Python)
  ├── Services: Screener.in, NSE, Yahoo, RAG
  ├── Engines: Growth, Quality, Risk, Valuation, Ownership
  └── Workers: Celery (PDF processing, alerts)
       ↓
PostgreSQL + Redis + Vector DB (pgvector)
```

**See:** [Architecture Design](./docs/architecture.md) for full details

---

## Technology Stack

### Backend (NEW - FastAPI/Python)
```python
fastapi        # Web framework
pandas/numpy   # Financial calculations
sqlalchemy     # ORM (PostgreSQL)
celery/redis   # Async job queue
langchain      # RAG orchestration
yfinance       # Yahoo Finance API
requests/bs4   # Web scraping
```

### Frontend (KEEP - Next.js/React)
```json
{
  "next": "^14.2.5",
  "react": "^18.3.1",
  "typescript": "^5.6.3",
  "recharts": "^2.10.0"
}
```

### Database
- **PostgreSQL 15+**: Main data store + pgvector extension
- **Redis 7+**: Cache + Celery message broker

---

## Project Structure

### Backend (NEW - To Be Built)
```
backend/
├── app/
│   ├── main.py              # FastAPI entry
│   ├── core/                # Config, DB, logging
│   ├── api/v1/              # REST endpoints
│   ├── services/            # Data sources
│   │   ├── screener.py      # 10yr fundamentals
│   │   ├── nse.py           # Shareholding, filings
│   │   ├── yahoo.py         # Prices, technicals
│   │   └── rag.py           # PDF analysis
│   ├── engines/             # Analysis logic
│   │   ├── analysis.py      # Main orchestrator
│   │   ├── growth.py        # Step 2: CAGR
│   │   ├── quality.py       # Step 3: ROCE/ROE
│   │   ├── risk.py          # Step 4: Debt
│   │   ├── valuation.py     # Step 5: PE, DCF
│   │   └── ownership.py     # Step 6: Pledging
│   ├── repositories/        # Database access
│   ├── models/              # SQLAlchemy models
│   └── workers/             # Celery tasks
├── tests/
└── pyproject.toml
```

### Frontend (REFACTOR - Clean UI Layer)
```
app/
├── page.tsx                 # Home/Search
├── company/[symbol]/        # Company dashboard
├── components/
│   ├── ui/                  # Primitives (Card, Button)
│   ├── features/            # Domain components
│   │   ├── search/
│   │   ├── analysis/        # HQSFScore, MetricsGrid
│   │   └── charts/          # Financial, Ownership charts
│   └── layout/
└── lib/
    ├── api/                 # FastAPI client
    │   ├── client.ts
    │   └── endpoints.ts
    └── hooks/               # useStockData, useAnalysis
```

**See:** [Architecture Design](./docs/architecture.md) for full structure

---

## The "Refined Framework" (7 Steps)

This is the **business logic core** of Stonky:

1. **Business Understanding** (RAG) - What does the company do? What's the moat?
2. **Growth** (Python) - Revenue/Profit CAGR > 10%?
3. **Quality** (Python) - ROCE & ROE > 15%?
4. **Risk** (Python) - Debt/Equity within sector limits?
5. **Valuation** (Python) - PE vs historical/sector, DCF, Graham Number
6. **Ownership** (Python) - Promoter pledging? FII/DII trends?
7. **Verdict** (LLM) - Buy/Hold/Avoid with narrative

**Implementation:** Steps 2-6 are deterministic Python logic. Step 1 & 7 use AI.

---

## Key Design Patterns

### Backend Patterns (Python/FastAPI)

#### Service Layer Pattern
```python
class ScreenerService(BaseService):
    async def fetch_fundamentals(self, symbol: str) -> dict:
        # Scrape Screener.in with session cookie
        # Return 10 years of ROCE, ROE, D/E, Revenue, etc.
```

#### Strategy Pattern (Sector-Aware Risk)
```python
class RiskEngine:
    strategies = {
        "Banking": BankingRiskStrategy(),  # D/E < 2.0
        "IT": ITRiskStrategy(),            # D/E < 0.3
    }

    def analyze(self, company, financials):
        strategy = self.strategies.get(company.sector, DefaultStrategy())
        return strategy.calculate_risk(financials)
```

#### Repository Pattern (Database Access)
```python
class CompanyRepository:
    async def get_by_symbol(self, symbol: str) -> Company:
        result = await self.db.execute(
            select(Company).where(Company.symbol == symbol)
        )
        return result.scalar_one_or_none()
```

### Frontend Patterns (React/Next.js)

#### Container/Presentational
```tsx
// Container (Server Component - fetches data)
export default async function CompanyAnalysisContainer({ symbol }) {
  const analysis = await fetchAnalysis(symbol);
  return <CompanyAnalysisView analysis={analysis} />;
}

// Presentational (Client Component - pure UI)
'use client'
export function CompanyAnalysisView({ analysis }) {
  return <MetricsCard metrics={analysis.metrics} />;
}
```

#### Custom Hooks
```typescript
export function useStockData(symbol: string) {
  const [data, setData] = useState(null);
  // ... fetch logic with abort controller
  return { data, loading, error };
}
```

**See:** [Architecture Design](./docs/architecture.md) for all patterns

---

## Development Workflow

### Initial Setup (FastAPI Backend)

```bash
# Create backend directory
mkdir backend && cd backend

# Initialize Poetry
poetry init
poetry add fastapi uvicorn pandas sqlalchemy redis celery

# Create directory structure
mkdir -p app/{core,api/v1,services,engines,repositories,models,workers}

# Set up environment
cp .env.example .env
# Edit .env with DATABASE_URL, REDIS_URL, SCREENER_COOKIE

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Running Services

```bash
# Terminal 1: FastAPI
uvicorn app.main:app --reload

# Terminal 2: Celery Worker
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3: Next.js Frontend
cd .. && npm run dev

# Terminal 4: Redis
redis-server

# Terminal 5: PostgreSQL
# (or use Docker: docker run -p 5432:5432 postgres:15)
```

---

## Key Environment Variables

```bash
# Backend (.env in backend/)
DATABASE_URL=postgresql://user:pass@localhost:5432/stonky
REDIS_URL=redis://localhost:6379/0
SCREENER_COOKIE=<your-session-cookie>  # Get from browser after login
OPENAI_API_KEY=sk-...                  # Optional (for RAG)

# Frontend (.env.local in root/)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Getting Screener.in Cookie:**
1. Login to Screener.in in Chrome
2. Open DevTools → Application → Cookies
3. Copy `sessionid` value
4. Paste in `.env` as `SCREENER_COOKIE`
5. Cookie lasts ~1 month, update when expired

---

## Migration Status

**See:** [Implementation Plan](./docs/implementation-plan.md) for detailed tasks

### Phase 1: Foundation ⏳
- [ ] FastAPI project scaffolding
- [ ] SQLAlchemy models (migrate from Prisma)
- [ ] Base repository pattern
- [ ] Core configuration

### Phase 2: Data Services ⏳
- [ ] Screener.in scraper (10yr fundamentals)
- [ ] NSE service (shareholding, filings)
- [ ] Yahoo Finance service (prices)
- [ ] News service

### Phase 3: Analysis Engines ⏳
- [ ] Growth engine (CAGR calculations)
- [ ] Quality engine (ROCE/ROE)
- [ ] Risk engine (sector-aware D/E)
- [ ] Valuation engine (DCF, Graham, PE)
- [ ] Ownership engine (pledging, FII/DII)
- [ ] Scoring engine (HQSF)
- [ ] Main analysis orchestrator

### Phase 4: API Endpoints ⏳
- [ ] `/api/v1/search` - Symbol search
- [ ] `/api/v1/company/{symbol}` - Company details
- [ ] `/api/v1/analyze/{symbol}` - Full analysis
- [ ] `/api/v1/prices/{symbol}` - Historical OHLC
- [ ] `/api/v1/news/{symbol}` - News feed

### Phase 5: Frontend Integration ⏳
- [ ] API client layer (`lib/api/client.ts`)
- [ ] Update all components to use FastAPI
- [ ] Remove Hono routes
- [ ] New components: HQSFScore, MetricsGrid, FinancialChart

### Phase 6: Async Processing ⏳
- [ ] Celery setup
- [ ] Analysis as background job
- [ ] Job status polling endpoint

### Phase 7: RAG Pipeline 🔜
- [ ] pgvector setup
- [ ] PDF download & OCR
- [ ] Text chunking & embedding
- [ ] Vector search service
- [ ] LLM synthesis (Step 1 & 7)

---

## Code Conventions

### Python (Backend)
```python
# Use type hints everywhere
async def get_company(symbol: str) -> Company | None:
    ...

# Pydantic for validation
class AnalysisRequest(BaseModel):
    symbol: str
    force: bool = False

# Dependency injection
@router.get("/analyze/{symbol}")
async def analyze(
    symbol: str,
    engine: AnalysisEngine = Depends(get_analysis_engine)
):
    ...
```

### TypeScript (Frontend)
```typescript
// Strict mode, no any
const data: StockData = await fetchData(symbol);

// Use @/ for imports
import { apiClient } from '@/lib/api/client';

// Async/await over .then()
const result = await apiClient('/api/v1/search?q=RELIANCE');
```

**See:** [Architecture Design](./docs/architecture.md) for full conventions

---

## Common Tasks

### Add a New Analysis Metric

1. **Update Engine** (`backend/app/engines/quality.py`):
```python
def analyze(self, financials: dict) -> QualityMetrics:
    # Add new calculation
    cash_conversion = self._calculate_cash_conversion(financials)
    return QualityMetrics(..., cash_conversion=cash_conversion)
```

2. **Update Schema** (`backend/app/api/v1/schemas/responses.py`):
```python
class QualityMetrics(BaseModel):
    cash_conversion: float
```

3. **Update Frontend** (`app/components/features/analysis/MetricsCard.tsx`):
```tsx
<Metric
  label="Cash Conversion"
  value={quality.cash_conversion}
  format="percentage"
/>
```

### Add a New Data Source

1. **Create Service** (`backend/app/services/newsource.py`):
```python
class NewSourceService(BaseService):
    async def fetch_data(self, symbol: str) -> dict:
        # Implementation
```

2. **Add to Factory** (`backend/app/core/dependencies.py`):
```python
def create_newsource_service(self) -> NewSourceService:
    return NewSourceService(self.config)
```

3. **Use in Engine** (`backend/app/engines/analysis.py`):
```python
data = await self.newsource.fetch_data(symbol)
```

---

## Important Notes

### Symbol Format
- Use NSE/BSE suffixes: `RELIANCE.NS` or `RELIANCE.BO`
- NSE APIs use symbol without suffix: `RELIANCE`
- Yahoo Finance requires suffix

### Data Freshness
- **Screener.in**: 10-year data, update weekly
- **NSE**: Shareholding data, update daily
- **Yahoo**: Prices, real-time (15min delay)
- **Analysis Cache**: 24 hours

### Cost Optimization
- Run FastAPI locally: **$0**
- Use Screener.in scraping: **$0** (just cookie)
- NSE scraping: **$0** (public APIs)
- Yahoo Finance: **$0** (yfinance library)
- LLM (optional): Gemini Flash free tier or $5/month OpenAI
- **Total: $0-5/month**

---

## Testing

### Run Backend Tests
```bash
cd backend
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests
```

### Run Frontend Tests
```bash
npm run typecheck           # Type checking
npm run test               # Jest (when added)
```

---

## Getting Help

- **Architecture Questions**: See [Architecture Design](./docs/architecture.md)
- **Implementation Tasks**: See [Implementation Plan](./docs/implementation-plan.md)
- **Product Vision**: See [AlphaGaze Master Plan](./docs/plan-final.md)
- **Technical Details**: See [Tech Plan Brief](./docs/tech-plan-brief.md)

---

## Next Steps for AI Assistants

1. **Read** [Architecture Design](./docs/architecture.md) to understand system design
2. **Review** [Implementation Plan](./docs/implementation-plan.md) for current phase
3. **Follow patterns** shown in architecture doc
4. **Test** changes incrementally
5. **Update** this file when architecture changes

---

**Remember:** We're building a professional-grade financial analysis terminal, not a simple dashboard. Every decision should prioritize accuracy, modularity, and scalability.
