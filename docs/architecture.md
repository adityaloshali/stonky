# Architecture Design Document

**Project:** Stonky (AlphaGaze)
**Version:** 2.0 (FastAPI Migration)
**Last Updated:** 2025-11-18

---

## Executive Summary

This document defines the production architecture for Stonky, aligning with the "Refined Framework 2025" vision. We migrate from a Hono/Next.js monolith to a **decoupled architecture** with FastAPI backend and Next.js frontend.

**Key Principle:** *Separation of Concerns*
- **Frontend**: Pure presentation layer (React/Next.js)
- **Backend**: Business logic, data processing, AI orchestration (FastAPI/Python)
- **Data Layer**: PostgreSQL (structured) + Redis (cache) + Vector DB (RAG)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER (Browser)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────────┐
│              FRONTEND (Next.js 14 - App Router)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Presentation Components (React Server + Client)     │   │
│  │  - Stock search UI                                   │   │
│  │  - Dashboard visualizations                          │   │
│  │  - Analysis display                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │ fetch()                             │
└─────────────────────────┼─────────────────────────────────────┘
                          │ HTTP REST API
┌─────────────────────────▼─────────────────────────────────────┐
│                 BACKEND (FastAPI - Python 3.11+)               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              API LAYER (Routers)                      │    │
│  │  /api/v1/search         - Symbol search              │    │
│  │  /api/v1/analyze/{sym}  - Comprehensive analysis     │    │
│  │  /api/v1/company/{sym}  - Company details            │    │
│  │  /api/v1/prices/{sym}   - Historical OHLC            │    │
│  │  /api/v1/news/{sym}     - News aggregation           │    │
│  └──────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │           SERVICE LAYER (Business Logic)              │    │
│  │  ScreenerService    - 10yr fundamentals scraping     │    │
│  │  NSEService         - Shareholding, filings          │    │
│  │  YahooService       - Prices, technicals             │    │
│  │  RAGService         - PDF ingestion & search         │    │
│  │  NewsService        - News aggregation               │    │
│  └──────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              ENGINE LAYER (Core Logic)                │    │
│  │  AnalysisEngine     - Refined Framework Steps 2-6    │    │
│  │  ScoringEngine      - HQSF score calculation         │    │
│  │  ValuationEngine    - DCF, Graham Number, PE comp    │    │
│  │  RiskEngine         - Sector-aware risk scoring      │    │
│  └──────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │            WORKER LAYER (Async Processing)            │    │
│  │  Celery Workers  - Long-running tasks                │    │
│  │  - PDF download & OCR                                │    │
│  │  - Embedding generation                              │    │
│  │  - Quarterly scanning                                │    │
│  └──────────────────────────────────────────────────────┘    │
└────────────────────────┬──────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                      DATA LAYER                                │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   PostgreSQL    │  │    Redis     │  │   Vector DB     │  │
│  │  - Companies    │  │  - Cache     │  │  - Embeddings   │  │
│  │  - Financials   │  │  - Sessions  │  │  - PDF chunks   │  │
│  │  - Snapshots    │  │  - Celery    │  │  (pgvector)     │  │
│  └─────────────────┘  └──────────────┘  └─────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## Design Patterns & Principles

### Backend Architecture Patterns

#### 1. **Service Layer Pattern**
Each external data source gets its own service class:

```python
# services/base_service.py
class BaseService(ABC):
    """Abstract base for all services"""

    @abstractmethod
    async def fetch_data(self, symbol: str) -> Dict:
        pass

    def _handle_error(self, e: Exception) -> Dict:
        """Consistent error handling"""
        return {"status": "error", "message": str(e)}

# services/screener_service.py
class ScreenerService(BaseService):
    def __init__(self, config: Config):
        self.session = requests.Session()
        self.cookie = config.SCREENER_COOKIE

    async def fetch_data(self, symbol: str) -> Dict:
        """10-year financial data"""
        # Implementation
```

**Benefits:**
- Testable in isolation
- Swappable implementations (mock for testing)
- Consistent error handling
- Single Responsibility Principle

---

#### 2. **Repository Pattern**
Database access abstracted behind repositories:

```python
# repositories/company_repository.py
class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_symbol(self, symbol: str) -> Optional[Company]:
        result = await self.db.execute(
            select(Company).where(Company.symbol == symbol)
        )
        return result.scalar_one_or_none()

    async def create(self, company: CompanyCreate) -> Company:
        db_company = Company(**company.dict())
        self.db.add(db_company)
        await self.db.commit()
        return db_company
```

**Benefits:**
- Database logic separate from business logic
- Easy to switch databases
- Testable with in-memory DB

---

#### 3. **Strategy Pattern for Analysis**
Different analysis strategies for different sectors:

```python
# engines/strategies/risk_strategy.py
class RiskStrategy(ABC):
    @abstractmethod
    def calculate_risk_score(self, metrics: FinancialMetrics) -> RiskScore:
        pass

class BankingRiskStrategy(RiskStrategy):
    """Higher D/E tolerance for banks"""
    DE_THRESHOLD = 2.0

    def calculate_risk_score(self, metrics: FinancialMetrics) -> RiskScore:
        # Banking-specific logic
        pass

class ITRiskStrategy(RiskStrategy):
    """Low D/E tolerance for IT"""
    DE_THRESHOLD = 0.3

    def calculate_risk_score(self, metrics: FinancialMetrics) -> RiskScore:
        # IT-specific logic
        pass

# Usage in engine
class RiskEngine:
    def __init__(self):
        self.strategies = {
            "Banking": BankingRiskStrategy(),
            "IT": ITRiskStrategy(),
            "Default": DefaultRiskStrategy()
        }

    def analyze(self, company: Company, metrics: FinancialMetrics) -> RiskScore:
        strategy = self.strategies.get(company.sector, self.strategies["Default"])
        return strategy.calculate_risk_score(metrics)
```

---

#### 4. **Factory Pattern for Services**
Centralized service creation with dependency injection:

```python
# core/dependencies.py
class ServiceFactory:
    def __init__(self, config: Config):
        self.config = config

    def create_screener_service(self) -> ScreenerService:
        return ScreenerService(self.config)

    def create_nse_service(self) -> NSEService:
        return NSEService(self.config)

    def create_analysis_engine(self) -> AnalysisEngine:
        return AnalysisEngine(
            screener=self.create_screener_service(),
            nse=self.create_nse_service(),
            yahoo=self.create_yahoo_service(),
            rag=self.create_rag_service()
        )

# FastAPI dependency injection
async def get_service_factory() -> ServiceFactory:
    return ServiceFactory(settings)

# In routes
@router.get("/analyze/{symbol}")
async def analyze(
    symbol: str,
    factory: ServiceFactory = Depends(get_service_factory)
):
    engine = factory.create_analysis_engine()
    result = await engine.analyze(symbol)
    return result
```

---

#### 5. **Command Pattern for Async Jobs**
Celery tasks as command objects:

```python
# workers/commands/base.py
class Command(ABC):
    @abstractmethod
    def execute(self) -> Any:
        pass

# workers/commands/pdf_analysis.py
class AnalyzePDFCommand(Command):
    def __init__(self, company_id: str, pdf_url: str):
        self.company_id = company_id
        self.pdf_url = pdf_url

    def execute(self) -> PDFAnalysis:
        # Download PDF
        # OCR/Extract text
        # Chunk text
        # Generate embeddings
        # Store in vector DB
        return PDFAnalysis(...)

# workers/tasks.py
@celery_app.task
def analyze_pdf_task(company_id: str, pdf_url: str):
    command = AnalyzePDFCommand(company_id, pdf_url)
    return command.execute()
```

---

### Frontend Architecture Patterns

#### 1. **Container/Presentational Pattern**

```typescript
// containers/CompanyAnalysisContainer.tsx (Smart Component)
export default async function CompanyAnalysisContainer({ symbol }: Props) {
  // Server Component - fetches data
  const analysis = await fetchAnalysis(symbol);

  return <CompanyAnalysisView analysis={analysis} />;
}

// components/CompanyAnalysisView.tsx (Dumb Component)
'use client'
export function CompanyAnalysisView({ analysis }: Props) {
  // Pure presentation, no data fetching
  return (
    <div>
      <MetricsCard metrics={analysis.metrics} />
      <RiskIndicator risk={analysis.risk} />
    </div>
  );
}
```

---

#### 2. **Custom Hooks Pattern**

```typescript
// hooks/useStockData.ts
export function useStockData(symbol: string) {
  const [data, setData] = useState<StockData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchData() {
      setLoading(true);
      try {
        const response = await fetch(
          `${API_BASE}/api/v1/company/${symbol}`,
          { signal: controller.signal }
        );
        const data = await response.json();
        setData(data);
      } catch (e) {
        if (e.name !== 'AbortError') setError(e);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    return () => controller.abort();
  }, [symbol]);

  return { data, loading, error };
}
```

---

#### 3. **Composition Pattern**

```typescript
// components/Dashboard.tsx
export function Dashboard({ symbol }: Props) {
  return (
    <DashboardLayout>
      <Header>
        <StockTitle symbol={symbol} />
        <BookmarkButton symbol={symbol} />
      </Header>

      <Grid>
        <Column>
          <Card>
            <MetricsSection symbol={symbol} />
          </Card>
          <Card>
            <FinancialCharts symbol={symbol} />
          </Card>
        </Column>

        <Column>
          <Card>
            <AIAnalysis symbol={symbol} />
          </Card>
          <Card>
            <NewsFeed symbol={symbol} />
          </Card>
        </Column>
      </Grid>
    </DashboardLayout>
  );
}
```

---

## Data Flow Architecture

### Read Path (User requests analysis)

```
User clicks "Analyze RELIANCE"
    ↓
Next.js Page Component (Server)
    ↓ fetch()
FastAPI: GET /api/v1/analyze/RELIANCE
    ↓
1. Check Cache (Redis): analysis:RELIANCE:v1
    ├─ HIT → Return cached JSON
    └─ MISS → Continue
    ↓
2. Check Database: SELECT * FROM snapshots WHERE symbol='RELIANCE'
    ├─ EXISTS & FRESH (< 24hrs) → Return from DB
    └─ STALE/MISSING → Continue
    ↓
3. Trigger Async Analysis (Celery Task)
    ├─ Enqueue job: analyze_company.delay('RELIANCE')
    └─ Return job_id to client
    ↓
Client polls: GET /api/v1/jobs/{job_id}
    ↓
Worker completes analysis
    ├─ Save to Database
    ├─ Cache in Redis
    └─ Update job status
    ↓
Client receives complete analysis
```

---

### Write Path (Background processing)

```
Celery Worker: analyze_company('RELIANCE')
    ↓
1. ServiceFactory.create_analysis_engine()
    ↓
2. Parallel Data Fetch (asyncio.gather)
    ├─ ScreenerService.fetch_data() → 10yr financials
    ├─ NSEService.get_shareholding() → Ownership data
    ├─ YahooService.get_prices() → Current price
    └─ NewsService.get_news() → Latest headlines
    ↓
3. AnalysisEngine.run_analysis()
    ├─ GrowthEngine.calculate_cagr()
    ├─ QualityEngine.check_roce_roe()
    ├─ RiskEngine.assess_debt()
    ├─ ValuationEngine.compare_pe()
    └─ OwnershipEngine.check_pledging()
    ↓
4. ScoringEngine.calculate_hqsf()
    ↓
5. RAGService.get_business_context()
    ├─ Check if PDF already embedded
    ├─ If not: Download → OCR → Embed → Store
    └─ Query vector DB for moat/risks
    ↓
6. LLM Synthesis (Step 7)
    ├─ Assemble prompt with all metrics
    ├─ Call OpenAI/Gemini
    └─ Generate verdict narrative
    ↓
7. Save Results
    ├─ CompanyRepository.save_snapshot()
    ├─ Cache in Redis (24hr TTL)
    └─ Return complete analysis
```

---

## Technology Stack (Updated)

### Backend (FastAPI)
```python
# Core
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
python = "^3.11"

# Data Processing
pandas = "^2.1.0"
numpy = "^1.25.0"
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"  # Migrations

# Async & Workers
celery = "^5.3.0"
redis = "^5.0.0"
aiohttp = "^3.9.0"

# Data Sources
requests = "^2.31.0"
beautifulsoup4 = "^4.12.0"
yfinance = "^0.2.31"
selenium = "^4.15.0"  # For NSE session

# AI & RAG
langchain = "^0.1.0"
openai = "^1.3.0"
sentence-transformers = "^2.2.0"
chromadb = "^0.4.0"  # or pgvector

# Validation
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
```

### Frontend (Next.js)
```json
{
  "next": "^14.2.5",
  "react": "^18.3.1",
  "typescript": "^5.6.3",
  "recharts": "^2.10.0",  // Charts
  "date-fns": "^3.0.0",   // Date utilities
  "zod": "^3.23.8"        // API validation
}
```

### Database
```yaml
PostgreSQL: 15+
  - Main data store
  - pgvector extension for embeddings

Redis: 7+
  - Cache layer
  - Celery message broker
```

---

## Project Structure (FastAPI Backend)

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry
│   ├── core/
│   │   ├── config.py              # Settings (Pydantic)
│   │   ├── database.py            # SQLAlchemy setup
│   │   ├── dependencies.py        # DI containers
│   │   ├── security.py            # Auth (future)
│   │   └── logging.py             # Structured logging
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   ├── router.py          # Main router
│   │   │   ├── endpoints/
│   │   │   │   ├── search.py      # Symbol search
│   │   │   │   ├── analyze.py     # Comprehensive analysis
│   │   │   │   ├── company.py     # Company details
│   │   │   │   ├── prices.py      # Historical prices
│   │   │   │   └── news.py        # News feed
│   │   │   └── schemas/           # Pydantic models
│   │   │       ├── requests.py
│   │   │       └── responses.py
│   │
│   ├── services/
│   │   ├── base.py                # Abstract service
│   │   ├── screener.py            # Screener.in scraper
│   │   ├── nse.py                 # NSE APIs
│   │   ├── yahoo.py               # Yahoo Finance
│   │   ├── news.py                # News aggregation
│   │   └── rag.py                 # RAG service
│   │
│   ├── engines/
│   │   ├── analysis.py            # Main analysis orchestrator
│   │   ├── scoring.py             # HQSF calculation
│   │   ├── growth.py              # Step 2: CAGR, trends
│   │   ├── quality.py             # Step 3: ROCE/ROE
│   │   ├── risk.py                # Step 4: Debt analysis
│   │   ├── valuation.py           # Step 5: PE, DCF, Graham
│   │   ├── ownership.py           # Step 6: Pledging, FII/DII
│   │   └── strategies/            # Sector-specific strategies
│   │       ├── banking.py
│   │       ├── it.py
│   │       └── default.py
│   │
│   ├── repositories/
│   │   ├── base.py                # Generic CRUD
│   │   ├── company.py             # Company operations
│   │   ├── financials.py          # Historical data
│   │   └── snapshot.py            # Analysis cache
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── company.py
│   │   ├── financials.py
│   │   ├── snapshot.py
│   │   ├── user.py                # Future
│   │   └── alert.py               # Future
│   │
│   ├── workers/
│   │   ├── celery_app.py          # Celery config
│   │   ├── tasks/
│   │   │   ├── analysis.py        # Analysis jobs
│   │   │   ├── pdf_processing.py  # PDF ingestion
│   │   │   └── alerts.py          # Alert scanning
│   │   └── commands/              # Command pattern
│   │       ├── base.py
│   │       └── analyze_pdf.py
│   │
│   └── utils/
│       ├── cache.py               # Redis helpers
│       ├── http.py                # HTTP client utils
│       ├── date.py                # Date helpers
│       └── validators.py          # Custom validators
│
├── migrations/                    # Alembic
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/
│   ├── seed_db.py
│   └── test_scrapers.py
├── pyproject.toml                 # Poetry config
├── alembic.ini
└── .env.example
```

---

## Project Structure (Next.js Frontend)

```
frontend/  (or keep in current app/)
├── app/
│   ├── layout.tsx
│   ├── page.tsx                   # Home/Search
│   ├── globals.css
│   ├── company/[symbol]/
│   │   └── page.tsx               # Company dashboard (Server Component)
│   │
│   └── components/
│       ├── ui/                    # Reusable UI primitives
│       │   ├── Card.tsx
│       │   ├── Button.tsx
│       │   ├── Input.tsx
│       │   └── Badge.tsx
│       │
│       ├── features/              # Feature-specific components
│       │   ├── search/
│       │   │   ├── SearchBar.tsx
│       │   │   └── SearchResults.tsx
│       │   ├── analysis/
│       │   │   ├── MetricsCard.tsx
│       │   │   ├── HQSFScore.tsx
│       │   │   ├── RiskIndicator.tsx
│       │   │   └── AIAnalysis.tsx
│       │   ├── charts/
│       │   │   ├── FinancialChart.tsx
│       │   │   ├── OwnershipChart.tsx
│       │   │   └── PriceChart.tsx
│       │   └── news/
│       │       └── NewsList.tsx
│       │
│       └── layout/
│           ├── Header.tsx
│           ├── Footer.tsx
│           └── Sidebar.tsx
│
├── lib/
│   ├── api/                       # API client layer
│   │   ├── client.ts              # Base fetch wrapper
│   │   ├── endpoints.ts           # API endpoints
│   │   └── types.ts               # Response types
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useStockData.ts
│   │   ├── useAnalysis.ts
│   │   └── useBookmarks.ts
│   │
│   └── utils/
│       ├── format.ts              # Number/date formatting
│       └── constants.ts           # App constants
│
└── types/
    └── index.ts                   # Shared TypeScript types
```

---

## API Contract (OpenAPI/Swagger)

FastAPI auto-generates OpenAPI docs at `/docs`.

### Key Endpoints

```yaml
GET /api/v1/search?q={query}
  Response: { items: SearchResult[] }

GET /api/v1/company/{symbol}
  Response: CompanyDetails

GET /api/v1/analyze/{symbol}
  Response: { job_id: string } | CompleteAnalysis (if cached)

GET /api/v1/jobs/{job_id}
  Response: { status: 'pending' | 'complete' | 'failed', result?: Analysis }

GET /api/v1/prices/{symbol}?period=1y
  Response: { prices: OHLC[] }

GET /api/v1/news/{symbol}?limit=5
  Response: { items: NewsItem[] }
```

---

## Deployment Architecture

### Development
```
localhost:3000  → Next.js dev server
localhost:8000  → FastAPI (uvicorn --reload)
localhost:5432  → PostgreSQL
localhost:6379  → Redis
```

### Production (Option 1: Single VPS)
```
Domain: stonky.com
  ├─ Nginx (Reverse Proxy)
  ├─ Next.js (Port 3000) → Served via Nginx
  ├─ FastAPI (Port 8000) → Proxied to /api/*
  ├─ PostgreSQL (Local)
  ├─ Redis (Local)
  └─ Celery Workers (Background)

Cost: $5-10/month (Hetzner/DigitalOcean)
```

### Production (Option 2: Hybrid)
```
Vercel → Next.js Frontend (Free tier)
Railway/Render → FastAPI Backend ($5/month)
Neon/Supabase → PostgreSQL (Free tier)
Upstash → Redis (Free tier)
```

---

## Migration Strategy

1. **Build FastAPI alongside Hono** (no breaking changes)
2. **Dual-route period**: Frontend calls FastAPI for new features
3. **Incremental migration**: Move endpoints one by one
4. **Remove Hono** when all routes migrated
5. **Update deployment** config

---

## Security Considerations

1. **API Keys**: Store in environment, never commit
2. **Rate Limiting**: Implement on scraping services
3. **CORS**: Configure for Next.js origin only
4. **Input Validation**: Zod on frontend, Pydantic on backend
5. **Session Cookies**: Rotate Screener.in cookie monthly
6. **SQL Injection**: Use SQLAlchemy ORM (never raw SQL)

---

## Performance Targets

- **Search**: < 200ms response time
- **Analysis (cached)**: < 500ms
- **Analysis (fresh)**: < 20s (async job)
- **PDF Ingestion**: < 60s (background)
- **Cache Hit Rate**: > 80% for analysis requests

---

## Monitoring & Observability

```python
# Structured logging
from loguru import logger

logger.info("Analysis started", symbol=symbol, user_id=user_id)
logger.error("Screener fetch failed", error=str(e), symbol=symbol)

# Metrics (future: Prometheus)
analysis_duration.observe(duration)
screener_requests.inc()
cache_hits.inc()
```

---

This architecture provides a solid foundation for building the full AlphaGaze vision with clean separation of concerns, testability, and scalability.
