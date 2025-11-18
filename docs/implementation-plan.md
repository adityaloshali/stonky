# Implementation Plan: FastAPI Migration

**Project:** Stonky Backend Migration
**Timeline:** 5 weeks (incremental delivery)
**Approach:** Build new, migrate incrementally, remove old

---

## Phase 1: Foundation & Setup (Week 1)

### 1.1 Project Scaffolding
- [ ] Create `backend/` directory at project root
- [ ] Initialize Poetry: `poetry init`
- [ ] Add dependencies (see architecture.md)
- [ ] Create directory structure per architecture.md
- [ ] Set up `.env.example` with all required vars
- [ ] Configure `pyproject.toml` with dev dependencies

**Deliverable:** Empty FastAPI app that starts successfully

---

### 1.2 Core Infrastructure
- [ ] **`app/core/config.py`**: Pydantic Settings
  ```python
  class Settings(BaseSettings):
      DATABASE_URL: str
      REDIS_URL: str
      SCREENER_COOKIE: str
      OPENAI_API_KEY: str | None
      LOG_LEVEL: str = "INFO"
  ```

- [ ] **`app/core/database.py`**: SQLAlchemy async setup
  - AsyncEngine creation
  - AsyncSession factory
  - Base declarative class

- [ ] **`app/core/logging.py`**: Loguru configuration
  - JSON logging for production
  - Pretty console logging for dev
  - Request ID tracking

- [ ] **`app/main.py`**: FastAPI app initialization
  - CORS middleware (Next.js origin)
  - Logging middleware
  - Exception handlers
  - Health check endpoint

**Test:** `uvicorn app.main:app --reload` runs without errors

---

### 1.3 Database Models
Migrate Prisma schema to SQLAlchemy:

- [ ] **`app/models/company.py`**
  - Company model (id, symbol, isin, name, sector)
  - Relationships to other models

- [ ] **`app/models/financials.py`**
  - FinancialsAnnual (10 years of data)
  - FinancialsQuarterly (optional for now)
  - JSON columns for flexibility

- [ ] **`app/models/snapshot.py`**
  - Snapshot model (analysis cache)
  - JSONB for analysis results

- [ ] **`app/models/price.py`**
  - PriceOHLC model
  - Index on (company_id, date)

- [ ] Create Alembic migrations
- [ ] Run migrations on dev database

**Test:** Models can be imported, migrations apply cleanly

---

### 1.4 Base Repository Pattern
- [ ] **`app/repositories/base.py`**
  ```python
  class BaseRepository[T]:
      def __init__(self, model: Type[T], db: AsyncSession):
          self.model = model
          self.db = db

      async def get(self, id: str) -> T | None
      async def get_by(self, **filters) -> T | None
      async def create(self, data: dict) -> T
      async def update(self, id: str, data: dict) -> T
      async def delete(self, id: str) -> bool
  ```

- [ ] **`app/repositories/company.py`**
  - Extends BaseRepository
  - Custom method: `get_by_symbol(symbol: str)`

**Test:** Write unit test for repository CRUD operations

---

## Phase 2: Data Services Layer (Week 2)

### 2.1 Base Service Architecture
- [ ] **`app/services/base.py`**
  ```python
  class BaseService(ABC):
      @abstractmethod
      async def fetch_data(self, symbol: str) -> dict:
          pass

      def _handle_error(self, e: Exception) -> dict:
          logger.error(f"Service error: {e}")
          return {"status": "error", "message": str(e)}
  ```

---

### 2.2 Screener.in Service (Critical)
- [ ] **`app/services/screener.py`**
  - Session management with cookie
  - `fetch_fundamentals(ticker: str)` → 10-year data
  - Parse Excel response into pandas DataFrame
  - Transform to dict with keys: ROCE, ROE, D/E, Revenue, etc.
  - Cache results in Redis (24hr TTL)
  - Graceful fallback if cookie expired

**Implementation Reference:** `tech-plan-brief.md` lines 48-93

**Test Cases:**
- Valid ticker returns 10 years of data
- Invalid ticker returns error
- Expired cookie triggers warning log

---

### 2.3 NSE Service
- [ ] **`app/services/nse.py`**
  - Session initialization (visit homepage for cookies)
  - `get_shareholding(symbol: str)` → Promoter/FII/DII data
  - `get_quote(symbol: str)` → Live quote
  - `search_filings(symbol: str)` → Latest PDFs (future)
  - Handle 401 errors with session refresh
  - Redis cache (5min TTL)

**Implementation Reference:** `tech-plan-brief.md` lines 95-148

**Test:** Fetch RELIANCE shareholding, verify promoter % returned

---

### 2.4 Yahoo Finance Service
- [ ] **`app/services/yahoo.py`**
  - Migrate from TypeScript yahoo.ts
  - Use `yfinance` library (Python)
  - `get_prices(symbol: str, period: str)` → OHLC data
  - `get_current_price(symbol: str)` → Latest price
  - `search_symbols(query: str)` → Search results

**Migration Note:** Port logic from `lib/sources/yahoo.ts`

---

### 2.5 News Service
- [ ] **`app/services/news.py`**
  - Use `feedparser` for Google News RSS
  - `get_news(query: str, limit: int)` → News items
  - Parse source, title, published date

**Migration Note:** Port from `lib/news/google.ts`

---

### 2.6 Service Factory
- [ ] **`app/core/dependencies.py`**
  ```python
  class ServiceFactory:
      def __init__(self, config: Settings):
          self.config = config

      def screener(self) -> ScreenerService:
          return ScreenerService(self.config.SCREENER_COOKIE)

      def nse(self) -> NSEService:
          return NSEService()

      # ... etc
  ```

- [ ] FastAPI dependency injection setup

---

## Phase 3: Analysis Engines (Week 2-3)

### 3.1 Growth Engine (Step 2)
- [ ] **`app/engines/growth.py`**
  ```python
  class GrowthEngine:
      def calculate_cagr(self, values: list[float], years: int) -> float:
          """CAGR = (Ending/Beginning)^(1/years) - 1"""

      def analyze(self, financials: dict) -> GrowthMetrics:
          revenue_cagr_3y = self.calculate_cagr(financials['Revenue'][-3:], 3)
          profit_cagr_3y = self.calculate_cagr(financials['Profit'][-3:], 3)

          return GrowthMetrics(
              revenue_cagr_3y=revenue_cagr_3y,
              profit_cagr_3y=profit_cagr_3y,
              flag="GREEN" if revenue_cagr_3y > 0.10 else "RED"
          )
  ```

**Tests:**
- CAGR calculation matches expected values
- Flag logic correct for different scenarios

---

### 3.2 Quality Engine (Step 3)
- [ ] **`app/engines/quality.py`**
  ```python
  class QualityEngine:
      def analyze(self, financials: dict) -> QualityMetrics:
          roce_3yr_avg = mean(financials['ROCE'][-3:])
          roe_3yr_avg = mean(financials['ROE'][-3:])

          if roce_3yr_avg > 15 and roe_3yr_avg > 15:
              flag = "GREEN"
          elif roce_3yr_avg < 15 and roe_3yr_avg > 15:
              flag = "RED"  # Debt-fueled
          else:
              flag = "YELLOW"

          return QualityMetrics(
              roce_3yr_avg=roce_3yr_avg,
              roe_3yr_avg=roe_3yr_avg,
              flag=flag
          )
  ```

---

### 3.3 Risk Engine (Step 4) - Strategy Pattern
- [ ] **`app/engines/strategies/risk_strategy.py`**
  - Abstract base: `RiskStrategy`
  - `BankingRiskStrategy` (D/E threshold = 2.0)
  - `ITRiskStrategy` (D/E threshold = 0.3)
  - `DefaultRiskStrategy` (D/E threshold = 1.0)

- [ ] **`app/engines/risk.py`**
  ```python
  class RiskEngine:
      def __init__(self):
          self.strategies = {
              "Banking": BankingRiskStrategy(),
              "IT": ITRiskStrategy(),
              # ... etc
          }

      def analyze(self, company: Company, financials: dict) -> RiskMetrics:
          strategy = self.strategies.get(
              company.sector,
              self.strategies["Default"]
          )
          return strategy.calculate_risk(financials)
  ```

**Test:** Verify different thresholds applied for Banking vs IT

---

### 3.4 Valuation Engine (Step 5)
- [ ] **`app/engines/valuation.py`**
  - `calculate_dcf()` - Discounted Cash Flow
  - `calculate_graham_number()` - √(22.5 × EPS × BVPS)
  - `compare_pe()` - Current vs Historical vs Sector
  - `classify_valuation()` - "Undervalued", "Fair", "Overvalued"

---

### 3.5 Ownership Engine (Step 6)
- [ ] **`app/engines/ownership.py`**
  - Check promoter pledging > 0
  - Calculate FII/DII trend (slope over quarters)
  - Flag if promoter holding decreased QoQ

---

### 3.6 Scoring Engine (HQSF)
- [ ] **`app/engines/scoring.py`**
  ```python
  class ScoringEngine:
      def calculate_hqsf(
          self,
          growth: GrowthMetrics,
          quality: QualityMetrics,
          risk: RiskMetrics,
          valuation: ValuationMetrics,
          ownership: OwnershipMetrics
      ) -> HQSFScore:
          """
          HQSF = Weighted average of all metrics
          - Quality: 30%
          - Safety (Risk): 25%
          - Valuation: 25%
          - Growth: 15%
          - Ownership: 5%
          """
          # Normalize each to 0-100 scale
          # Apply weights
          # Return total score
  ```

---

### 3.7 Main Analysis Engine (Orchestrator)
- [ ] **`app/engines/analysis.py`**
  ```python
  class AnalysisEngine:
      def __init__(
          self,
          screener: ScreenerService,
          nse: NSEService,
          yahoo: YahooService
      ):
          self.screener = screener
          self.nse = nse
          self.yahoo = yahoo

          # Initialize sub-engines
          self.growth = GrowthEngine()
          self.quality = QualityEngine()
          self.risk = RiskEngine()
          self.valuation = ValuationEngine()
          self.ownership = OwnershipEngine()
          self.scoring = ScoringEngine()

      async def analyze(self, symbol: str) -> CompleteAnalysis:
          # 1. Fetch data in parallel
          fundamentals, shareholding, price = await asyncio.gather(
              self.screener.fetch_fundamentals(symbol),
              self.nse.get_shareholding(symbol),
              self.yahoo.get_current_price(symbol)
          )

          # 2. Get company from DB
          company = await company_repo.get_by_symbol(symbol)

          # 3. Run all analysis steps
          growth = self.growth.analyze(fundamentals)
          quality = self.quality.analyze(fundamentals)
          risk = self.risk.analyze(company, fundamentals)
          valuation = self.valuation.analyze(fundamentals, price)
          ownership = self.ownership.analyze(shareholding)

          # 4. Calculate final score
          score = self.scoring.calculate_hqsf(
              growth, quality, risk, valuation, ownership
          )

          # 5. Generate verdict
          verdict = self._generate_verdict(score, growth, quality, risk)

          return CompleteAnalysis(
              symbol=symbol,
              score=score,
              growth=growth,
              quality=quality,
              risk=risk,
              valuation=valuation,
              ownership=ownership,
              verdict=verdict,
              timestamp=datetime.now()
          )

      def _generate_verdict(self, ...) -> str:
          # Logic from plan1.md lines 100-104
  ```

---

## Phase 4: API Endpoints (Week 3)

### 4.1 API Schemas (Pydantic)
- [ ] **`app/api/v1/schemas/requests.py`**
  - `SearchRequest`
  - `AnalyzeRequest`
  - `PricesRequest`

- [ ] **`app/api/v1/schemas/responses.py`**
  - `SearchResponse`
  - `CompanyResponse`
  - `AnalysisResponse`
  - `PricesResponse`
  - `NewsResponse`

---

### 4.2 Endpoint: Search
- [ ] **`app/api/v1/endpoints/search.py`**
  ```python
  @router.get("/search", response_model=SearchResponse)
  async def search_symbols(
      q: str = Query(..., min_length=1),
      limit: int = Query(10, le=50),
      yahoo: YahooService = Depends(get_yahoo_service)
  ):
      results = await yahoo.search_symbols(q, limit)
      return SearchResponse(items=results)
  ```

**Test:** `/api/v1/search?q=RELIANCE` returns NSE/BSE symbols

---

### 4.3 Endpoint: Company Details
- [ ] **`app/api/v1/endpoints/company.py`**
  ```python
  @router.get("/company/{symbol}", response_model=CompanyResponse)
  async def get_company(
      symbol: str,
      repo: CompanyRepository = Depends(get_company_repo)
  ):
      company = await repo.get_by_symbol(symbol)
      if not company:
          raise HTTPException(404, "Company not found")
      return company
  ```

---

### 4.4 Endpoint: Prices
- [ ] **`app/api/v1/endpoints/prices.py`**
  ```python
  @router.get("/prices/{symbol}", response_model=PricesResponse)
  async def get_prices(
      symbol: str,
      period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$"),
      yahoo: YahooService = Depends(get_yahoo_service),
      cache: Redis = Depends(get_redis)
  ):
      # Try cache first
      cached = await cache.get(f"prices:{symbol}:{period}")
      if cached:
          return json.loads(cached)

      # Fetch fresh data
      prices = await yahoo.get_prices(symbol, period)

      # Cache for 5 minutes
      await cache.setex(
          f"prices:{symbol}:{period}",
          300,
          json.dumps(prices)
      )

      return PricesResponse(symbol=symbol, prices=prices)
  ```

---

### 4.5 Endpoint: News
- [ ] **`app/api/v1/endpoints/news.py`**
  ```python
  @router.get("/news/{symbol}", response_model=NewsResponse)
  async def get_news(
      symbol: str,
      limit: int = Query(5, le=20),
      news_service: NewsService = Depends(get_news_service)
  ):
      items = await news_service.get_news(symbol, limit)
      return NewsResponse(items=items)
  ```

---

### 4.6 Endpoint: Analyze (Key Endpoint)
- [ ] **`app/api/v1/endpoints/analyze.py`**
  ```python
  @router.get("/analyze/{symbol}")
  async def analyze_stock(
      symbol: str,
      force: bool = Query(False),  # Force fresh analysis
      background_tasks: BackgroundTasks,
      cache: Redis = Depends(get_redis),
      repo: SnapshotRepository = Depends(get_snapshot_repo),
      factory: ServiceFactory = Depends(get_service_factory)
  ):
      # 1. Check cache
      if not force:
          cached = await cache.get(f"analysis:{symbol}")
          if cached:
              return json.loads(cached)

      # 2. Check database (last 24 hours)
      if not force:
          snapshot = await repo.get_latest(symbol, max_age_hours=24)
          if snapshot:
              return snapshot.data

      # 3. Trigger async analysis (Celery)
      # For now, do it synchronously
      engine = factory.create_analysis_engine()
      result = await engine.analyze(symbol)

      # 4. Save to DB
      await repo.create(symbol=symbol, data=result.dict())

      # 5. Cache for 24 hours
      await cache.setex(
          f"analysis:{symbol}",
          86400,
          json.dumps(result.dict())
      )

      return result
  ```

**Note:** Phase 5 will convert this to async (Celery)

---

### 4.7 Main Router
- [ ] **`app/api/v1/router.py`**
  ```python
  api_router = APIRouter()
  api_router.include_router(search.router, prefix="/search", tags=["search"])
  api_router.include_router(company.router, prefix="/company", tags=["company"])
  api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
  api_router.include_router(news.router, prefix="/news", tags=["news"])
  api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
  ```

- [ ] Mount in `app/main.py`: `app.include_router(api_router, prefix="/api/v1")`

---

## Phase 5: Frontend Integration (Week 4)

### 5.1 API Client Layer
- [ ] **`lib/api/client.ts`**
  ```typescript
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  export async function apiClient<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  }
  ```

- [ ] **`lib/api/endpoints.ts`**
  ```typescript
  export const endpoints = {
    search: (q: string) => `/api/v1/search?q=${encodeURIComponent(q)}`,
    company: (symbol: string) => `/api/v1/company/${symbol}`,
    analyze: (symbol: string) => `/api/v1/analyze/${symbol}`,
    prices: (symbol: string, period = '1y') =>
      `/api/v1/prices/${symbol}?period=${period}`,
    news: (symbol: string) => `/api/v1/news/${symbol}`,
  };
  ```

---

### 5.2 Update Components
- [ ] **SearchBar**: Call new `/api/v1/search` endpoint
- [ ] **CompanyPage**: Fetch from `/api/v1/company/{symbol}`
- [ ] **CompanyAI**: Call `/api/v1/analyze/{symbol}`
- [ ] **PriceChart**: Use `/api/v1/prices/{symbol}`
- [ ] **NewsList**: Use `/api/v1/news/{symbol}`

---

### 5.3 New Components for Enhanced Analysis
- [ ] **`components/features/analysis/HQSFScore.tsx`**
  - Display 0-100 score with color gradient
  - Show badge (High Quality, Safe, Fairly Priced)

- [ ] **`components/features/analysis/MetricsGrid.tsx`**
  - Display Growth/Quality/Risk/Valuation in grid
  - Traffic light indicators (Green/Yellow/Red)

- [ ] **`components/features/charts/FinancialChart.tsx`**
  - Use recharts to plot 10-year Revenue/Profit
  - Stacked bars for multi-metric view

- [ ] **`components/features/charts/OwnershipChart.tsx`**
  - Area chart: Promoter/FII/DII over time

---

### 5.4 Update Company Page
- [ ] Refactor `app/company/[symbol]/page.tsx`
  - Server Component fetches basic data
  - Client Components handle interactive parts
  - Use Suspense for streaming

```tsx
export default async function CompanyPage({ params }: Props) {
  const { symbol } = params;

  // Parallel data fetching
  const [company, prices] = await Promise.all([
    fetchCompany(symbol),
    fetchPrices(symbol),
  ]);

  return (
    <div>
      <Header company={company} />

      <Suspense fallback={<LoadingSpinner />}>
        <AnalysisSection symbol={symbol} />
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <ChartsSection prices={prices} />
      </Suspense>
    </div>
  );
}
```

---

### 5.5 Environment Configuration
- [ ] Update `.env.local`:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```

- [ ] For production:
  ```
  NEXT_PUBLIC_API_URL=https://api.stonky.com
  ```

---

### 5.6 Remove Hono
- [ ] Delete `app/api/hono/` directory
- [ ] Delete remaining Next.js API routes:
  - `app/api/search/route.ts`
  - `app/api/prices/[symbol]/route.ts`
  - `app/api/news/[symbol]/route.ts`
  - `app/api/ai/*/route.ts`
  - `app/api/agent/*/route.ts`

- [ ] Update all component imports to use new API client

---

## Phase 6: Async Processing with Celery (Week 5)

### 6.1 Celery Setup
- [ ] **`app/workers/celery_app.py`**
  ```python
  from celery import Celery

  celery_app = Celery(
      "stonky",
      broker="redis://localhost:6379/0",
      backend="redis://localhost:6379/0"
  )

  celery_app.conf.task_routes = {
      "app.workers.tasks.analyze.*": {"queue": "analysis"},
      "app.workers.tasks.pdf.*": {"queue": "pdf"},
  }
  ```

---

### 6.2 Analysis Task
- [ ] **`app/workers/tasks/analysis.py`**
  ```python
  from app.workers.celery_app import celery_app

  @celery_app.task(name="analyze_company")
  def analyze_company_task(symbol: str) -> dict:
      # Create service factory
      factory = ServiceFactory(settings)
      engine = factory.create_analysis_engine()

      # Run analysis (blocking in worker)
      result = asyncio.run(engine.analyze(symbol))

      # Save to DB
      # Cache in Redis

      return result.dict()
  ```

---

### 6.3 Update Analyze Endpoint
- [ ] Modify `/api/v1/analyze/{symbol}` to:
  1. Check cache/DB
  2. If miss, enqueue Celery task
  3. Return `{ job_id: "...", status: "pending" }`
  4. Client polls `/api/v1/jobs/{job_id}` until complete

---

### 6.4 Job Status Endpoint
- [ ] **`app/api/v1/endpoints/jobs.py`**
  ```python
  @router.get("/jobs/{job_id}")
  async def get_job_status(job_id: str):
      task = AsyncResult(job_id, app=celery_app)

      if task.ready():
          return {
              "status": "complete",
              "result": task.result
          }
      else:
          return {
              "status": "pending",
              "progress": task.info.get("progress", 0)
          }
  ```

---

## Phase 7: RAG Implementation (Week 5+)

### 7.1 Vector Database Setup
- [ ] Add pgvector extension to PostgreSQL
  ```sql
  CREATE EXTENSION vector;
  ```

- [ ] Create embeddings table:
  ```python
  class DocumentChunk(Base):
      __tablename__ = "document_chunks"

      id = Column(UUID, primary_key=True)
      company_id = Column(String, ForeignKey("companies.id"))
      source_type = Column(String)  # "annual_report", "concall"
      source_url = Column(String)
      chunk_text = Column(Text)
      embedding = Column(Vector(1536))  # OpenAI embedding size
      metadata = Column(JSONB)
      created_at = Column(DateTime)
  ```

---

### 7.2 PDF Processing Pipeline
- [ ] **`app/services/pdf_processor.py`**
  - Download PDF from NSE/BSE
  - Extract text (PyPDF2 or pdfplumber)
  - Chunk text (500 words with 50-word overlap)
  - Generate embeddings (OpenAI or sentence-transformers)
  - Store in database

- [ ] **Celery task**: `process_pdf_task(company_id, pdf_url)`

---

### 7.3 RAG Service
- [ ] **`app/services/rag.py`**
  ```python
  class RAGService:
      async def search_context(
          self,
          query: str,
          company_id: str,
          top_k: int = 5
      ) -> list[str]:
          # Generate query embedding
          query_embedding = self.embed(query)

          # Vector similarity search
          results = await self.db.execute(
              select(DocumentChunk)
              .where(DocumentChunk.company_id == company_id)
              .order_by(
                  DocumentChunk.embedding.cosine_distance(query_embedding)
              )
              .limit(top_k)
          )

          return [r.chunk_text for r in results.scalars()]

      async def generate_business_context(
          self,
          symbol: str
      ) -> str:
          # Search for relevant chunks
          moat_context = await self.search_context(
              "competitive advantage moat barriers to entry",
              company_id
          )

          risk_context = await self.search_context(
              "risks challenges threats headwinds",
              company_id
          )

          # Send to LLM
          prompt = f"""
          Based on the following excerpts from the annual report:

          {' '.join(moat_context)}

          Analyze the company's competitive moat.
          """

          response = await openai.chat.completions.create(
              model="gpt-4",
              messages=[{"role": "user", "content": prompt}]
          )

          return response.choices[0].message.content
  ```

---

### 7.4 Integrate RAG with Analysis
- [ ] Update `AnalysisEngine.analyze()` to call RAG service
- [ ] Add business context to final analysis response

---

## Testing Strategy

### Unit Tests
```python
# tests/unit/test_growth_engine.py
def test_cagr_calculation():
    engine = GrowthEngine()
    values = [100, 110, 121]  # 10% annual growth
    cagr = engine.calculate_cagr(values, 2)
    assert abs(cagr - 0.10) < 0.001
```

### Integration Tests
```python
# tests/integration/test_screener_service.py
@pytest.mark.asyncio
async def test_fetch_fundamentals():
    service = ScreenerService(cookie="test_cookie")
    data = await service.fetch_fundamentals("RELIANCE")
    assert "ROCE" in data
    assert len(data["ROCE"]) == 10  # 10 years
```

### E2E Tests
```python
# tests/e2e/test_analyze_endpoint.py
@pytest.mark.asyncio
async def test_analyze_endpoint(client: AsyncClient):
    response = await client.get("/api/v1/analyze/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert data["score"]["hqsf"] > 0
```

---

## Deployment Checklist

### Pre-deployment
- [ ] All tests passing
- [ ] Environment variables documented
- [ ] Database migrations applied
- [ ] API documentation generated (Swagger)
- [ ] Performance testing completed
- [ ] Security audit (dependency scan)

### Production Setup
- [ ] FastAPI on Gunicorn/Uvicorn
- [ ] Celery workers running
- [ ] Redis configured
- [ ] PostgreSQL with pgvector
- [ ] Nginx reverse proxy
- [ ] SSL certificates (Let's Encrypt)
- [ ] Logging to file/service
- [ ] Error tracking (Sentry)
- [ ] Monitoring (uptime checks)

---

## Success Metrics

### Performance
- [ ] Search response: < 200ms
- [ ] Cached analysis: < 500ms
- [ ] Fresh analysis: < 20s
- [ ] PDF processing: < 60s

### Quality
- [ ] 100% test coverage for engines
- [ ] All linting rules passing
- [ ] Type hints on all functions
- [ ] Documentation for all services

### Business
- [ ] Analysis accuracy validated against manual checks
- [ ] HQSF scores correlate with actual stock performance
- [ ] No false positives in risk flags

---

This plan provides a clear, incremental path to migrate from Hono to FastAPI while maintaining functionality and delivering value at each phase.
