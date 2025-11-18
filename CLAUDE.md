# CLAUDE.md

**Project: Stonky - AI-Augmented Stock Analysis Platform**

This document provides comprehensive context for AI assistants working with the Stonky codebase. It covers architecture, conventions, workflows, and important patterns to follow.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Architecture & Design Patterns](#architecture--design-patterns)
5. [Database Schema](#database-schema)
6. [API Routes & Endpoints](#api-routes--endpoints)
7. [Frontend Components](#frontend-components)
8. [Core Modules & Libraries](#core-modules--libraries)
9. [Development Workflow](#development-workflow)
10. [Code Conventions](#code-conventions)
11. [Environment Variables](#environment-variables)
12. [Common Tasks](#common-tasks)
13. [Important Gotchas](#important-gotchas)
14. [Future Roadmap](#future-roadmap)

---

## Project Overview

### What is Stonky?

Stonky is an **AI-augmented investment terminal** for the Indian stock market (NSE/BSE). It solves the "synthesis problem" - while tools like Screener.in provide data and TradingView provides charts, no tool helps investors truly *understand* companies. Stonky combines:

- **Hard Data**: Official NSE/BSE filings, Yahoo Finance prices, technical indicators
- **Soft Analysis**: AI-powered reading of Annual Reports and concall transcripts (RAG)
- **Quantitative Framework**: The "Refined Framework 2025" (HQSF) - a 7-step investment checklist

**Core Value Proposition**: "The depth of a Hedge Fund Analyst, the speed of a click."

### Current Implementation Status

**Implemented:**
- ✅ Stock symbol search (NSE/BSE filtering via Yahoo Finance)
- ✅ Historical OHLC price data (1-year candles)
- ✅ Latest news aggregation (Google News RSS)
- ✅ AI text completion and structured analysis endpoints
- ✅ Bookmark/watchlist system (localStorage-based)
- ✅ Dark mode support
- ✅ Responsive UI with sticky headers
- ✅ Complete database schema (Prisma)
- ✅ Type-safe API layer (Zod validation)

**Not Yet Implemented:**
- ❌ RAG-based PDF analysis (Step 1 of framework)
- ❌ Agent-based comprehensive analysis
- ❌ Vector embedding & semantic search
- ❌ Quarterly alert system
- ❌ User authentication & subscription tiers
- ❌ Portfolio tracking

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14.2.5 (App Router)
- **Language**: TypeScript 5.6.3 (strict mode)
- **Styling**: Pure CSS with CSS variables (no Tailwind by design)
- **State**: React Hooks (useState, useEffect)
- **Routing**: Next.js file-based routing

### Backend
- **Runtime**: Node.js (Next.js Server Runtime)
- **API Framework**: Hono 4.5.7 (lightweight, composable)
- **Server Actions**: Enabled in next.config.mjs

### Database & Caching
- **Database**: PostgreSQL via Prisma ORM 5.19.0
- **Cache**: Redis (ioredis 5.3.2) - optional with graceful fallback
- **Migrations**: Prisma Migrate

### AI & LLM
- **AI SDK**: Vercel AI SDK (`ai` 3.2.35)
- **Providers**:
  - OpenAI (`@ai-sdk/openai` 0.0.36)
  - OpenRouter (fallback for model flexibility)
- **Validation**: Zod 3.23.8 for runtime schema validation

### Data Sources
- **Stock Data**: `yahoo-finance2` 2.12.2
- **News**: `rss-parser` 3.12.0 (Google News)
- **Web Scraping**: `cheerio` 1.0.0-rc.12
- **Technical Analysis**: `technicalindicators` 3.1.0

### Key Design Decisions
- **No Tailwind**: Pure CSS for simplicity and full control
- **No Heavy Test Frameworks**: Keep dependencies lean
- **Hono over Express**: Modern, composable API design
- **Graceful Degradation**: Redis and AI features are optional

---

## Project Structure

```
stonky/
├── app/                          # Next.js App Router
│   ├── page.tsx                 # Home page (search interface)
│   ├── layout.tsx               # Root layout with header
│   ├── globals.css              # Global styles & theme
│   ├── api/                     # API routes
│   │   ├── hono/[...route]/     # Hono catch-all route
│   │   ├── search/              # Stock symbol search
│   │   ├── prices/[symbol]/     # OHLC price data
│   │   ├── news/[symbol]/       # News aggregation
│   │   ├── ai/                  # AI endpoints
│   │   │   ├── complete/        # Text completion
│   │   │   └── structured/      # Structured JSON analysis
│   │   └── agent/               # Agent endpoints
│   │       └── analyze/         # Comprehensive analysis
│   ├── company/[symbol]/        # Company detail page (dynamic)
│   │   └── page.tsx            # Server-side rendered with ISR
│   └── components/              # React client components
│       ├── SearchBar.tsx        # Autocomplete search
│       ├── CompanyAI.tsx        # AI analysis UI
│       ├── NewsList.tsx         # News feed
│       ├── BookmarkButton.tsx   # Save functionality
│       ├── BookmarksBar.tsx     # Saved companies bar
│       └── ThemeToggle.tsx      # Dark mode toggle
│
├── lib/                         # Core utility libraries
│   ├── agent/                   # Agentic AI logic
│   │   └── graph.ts             # LangGraph-style agent (stub)
│   ├── ai/                      # AI model integration
│   │   └── modelRouter.ts       # OpenAI/OpenRouter client
│   ├── cache/                   # Caching layer
│   │   └── redis.ts             # Redis with fallback
│   ├── db/                      # Database access
│   │   └── prisma.ts            # Prisma singleton
│   ├── sources/                 # External data APIs
│   │   ├── yahoo.ts             # Yahoo Finance
│   │   └── nse.ts               # NSE India
│   ├── news/                    # News aggregation
│   │   └── google.ts            # Google News RSS
│   └── tech/                    # Technical analysis
│       └── indicators.ts        # RSI, MACD, SMA, Bollinger
│
├── prisma/                      # Database schema
│   └── schema.prisma            # 10 models (PostgreSQL)
│
├── types/                       # TypeScript definitions
│   └── ambient.d.ts             # Ambient type declarations
│
├── docs/                        # Planning & documentation
│   ├── plan-final.md            # Master design (AlphaGaze)
│   ├── tech-plan-brief.md       # Technical implementation
│   ├── plan1.md                 # Architecture overview
│   └── plan2.md                 # Additional notes
│
├── package.json                 # Dependencies & scripts
├── tsconfig.json                # TypeScript config (strict)
├── next.config.mjs              # Next.js config
├── next-env.d.ts                # Next.js types (auto-generated)
└── .gitignore                   # Only node_modules ignored
```

---

## Architecture & Design Patterns

### 1. Three-Layer Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (Next.js App Router)          │
│  - Server Components (RSC)              │
│  - Client Components (islands)          │
│  - ISR for company pages (5-min)        │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  API Layer (Next.js Routes + Hono)      │
│  - REST endpoints (/api/*)              │
│  - Zod validation                       │
│  - Cache-Control headers                │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  Services Layer (lib/*)                 │
│  - Data sources (yahoo, nse, google)    │
│  - AI integration (modelRouter)         │
│  - Technical indicators                 │
│  - Database access (Prisma)             │
│  - Caching (Redis)                      │
└─────────────────────────────────────────┘
```

### 2. Data Flow Pattern

**Typical Stock Analysis Request:**
1. User navigates to `/company/RELIANCE`
2. Server component fetches data:
   - Check Prisma DB for cached snapshot
   - If stale/missing, fetch from Yahoo Finance
   - Optionally check Redis cache for intermediate results
3. Client components (CompanyAI, NewsList) lazy-load additional data
4. AI analysis triggered on-demand via API calls
5. Results cached with appropriate TTLs

### 3. Caching Strategy

```
┌──────────────────────────────────────────┐
│  Cache Layer Hierarchy                   │
├──────────────────────────────────────────┤
│  1. Browser Cache (stale-while-revalidate) │
│  2. Redis (5-min TTL for prices)         │
│  3. PostgreSQL (snapshots with timestamps)│
│  4. ISR (5-min revalidation)             │
└──────────────────────────────────────────┘
```

### 4. AI Integration Pattern

```typescript
// Standard pattern for AI-powered features
const client = getOpenAI();           // Model router
const model = getDefaultModelId();     // Fallback logic
const response = await generateText({  // Vercel AI SDK
  model: client(model),
  prompt: "..."
});
```

### 5. Error Handling Philosophy

- **Graceful Degradation**: Missing Redis/AI keys don't crash the app
- **Type Safety**: Zod validation at API boundaries
- **User-Friendly Errors**: JSON responses with clear error messages
- **Logging**: Console logs for debugging (production logging TBD)

---

## Database Schema

### Entity Relationship Overview

```
User (1) ──→ (N) Subscription
     (1) ──→ (N) Watchlist
     (1) ──→ (N) AlertRule

Company (1) ──→ (N) Snapshot
        (1) ──→ (N) PriceOHLC
        (1) ──→ (N) Filing
        (1) ──→ (N) NewsItem

AlertRule (1) ──→ (N) AlertEvent
```

### Core Models

#### **User** (`id`, `email`, `name`)
- Authentication entity (auth not yet implemented)
- Relations: subscriptions, watchlists, alert rules

#### **Subscription** (`plan`, `status`)
- Plans: "free", "pro"
- Status: "active", "canceled", "past_due"

#### **Company** (`symbol`, `isin`, `name`, `sector`)
- Central entity for all stock data
- `symbol` is unique identifier (e.g., "RELIANCE.NS")
- `isin` for official NSE/BSE identification

#### **Snapshot** (`kind`, `data`, `sources`)
- Versioned analysis storage
- `kind`: "fundamentals", "technicals", "news", "filings"
- `data`: JSONB for flexible schema
- `sources`: JSONB for provenance (API sources, timestamps)

#### **PriceOHLC** (`date`, `open`, `high`, `low`, `close`, `volume`)
- Historical price data
- **Index**: `(companyId, date)` for efficient time-series queries
- Typically stores 1-year of daily candles

#### **Filing** (`title`, `url`, `publishedAt`, `kind`, `meta`)
- Corporate filings from NSE/BSE
- `kind`: "results", "presentation", "concall", "other"
- `meta`: JSONB for additional metadata

#### **NewsItem** (`title`, `url`, `source`, `publishedAt`)
- News aggregation from Google News RSS
- `companyId` optional (some news affects multiple stocks)

#### **Watchlist** (`name`, `symbols[]`)
- User's saved stocks
- `symbols` is array of strings (e.g., ["RELIANCE.NS", "TCS.NS"])

#### **AlertRule** (`kind`, `params`, `active`)
- User-defined alerts
- `kind`: "price", "rsi", "breakout"
- `params`: JSONB for alert conditions

#### **AlertEvent** (`triggeredAt`, `payload`)
- Alert trigger history
- `payload`: JSONB with alert details

### Schema Notes

**IMPORTANT**: There are missing back-relations in the current schema:
- `Company` needs `filings Filing[]` and `news NewsItem[]`
- `User` needs `alertRules AlertRule[]`
- `AlertRule` needs `events AlertEvent[]`

When modifying the schema, add these relations for bidirectional navigation.

---

## API Routes & Endpoints

### Public REST Endpoints

| Endpoint | Method | Purpose | Cache |
|----------|--------|---------|-------|
| `/api/search?q=...` | GET | Search stock symbols (NSE/BSE) | No |
| `/api/prices/[symbol]` | GET | Get 1-year OHLC data | 5 min |
| `/api/news/[symbol]` | GET | Get latest news (top 5) | No |
| `/api/ai/complete` | POST | Free-form text completion | No |
| `/api/ai/structured` | POST | Structured JSON analysis | No |
| `/api/agent/analyze` | POST | Comprehensive company analysis | No |
| `/api/hono/health` | GET | Health check | No |
| `/api/hono/v1/company/:symbol/summary` | GET | Agent summary (placeholder) | No |

### Request/Response Patterns

#### Search Endpoint
```typescript
// GET /api/search?q=RELIANCE
Response: {
  items: [
    { symbol: "RELIANCE.NS", name: "Reliance Industries", exchange: "NSE" }
  ]
}
```

#### Prices Endpoint
```typescript
// GET /api/prices/RELIANCE.NS
Response: {
  symbol: "RELIANCE.NS",
  prices: [
    { date: "2024-01-01", open: 2500, high: 2550, low: 2480, close: 2520, volume: 1000000 }
  ]
}
```

#### AI Structured Analysis
```typescript
// POST /api/ai/structured
Request: {
  symbol: "RELIANCE.NS",
  context: "Recent financial data..."
}

Response: {
  headline: "Strong fundamentals with debt concerns",
  segments: [
    { title: "Revenue", content: "...", sentiment: "positive" }
  ],
  risks: ["High debt levels", "..."],
  opportunities: ["Telecom growth", "..."]
}
```

### Hono Integration

The `/api/hono/[...route]` catch-all route uses Hono for composable API design:

```typescript
// In app/api/hono/[...route]/route.ts
import { Hono } from 'hono';
import { handle } from 'hono/vercel';

const app = new Hono().basePath('/api/hono');

app.get('/health', (c) => c.json({ status: 'ok' }));
app.get('/v1/company/:symbol/summary', async (c) => {
  // Agent-based analysis (placeholder)
});

export const GET = handle(app);
export const POST = handle(app);
```

### Cache Headers

Price data endpoints use aggressive caching:
```
cache-control: public, s-maxage=300, stale-while-revalidate=60
```

---

## Frontend Components

### Server Components (RSC)

#### **app/page.tsx** (Home Page)
- Hero section with title and description
- Dynamic imports for SearchBar and BookmarksBar
- Static content, minimal client-side JS

#### **app/company/[symbol]/page.tsx** (Company Detail)
- Async server component
- ISR with 5-minute revalidation: `export const revalidate = 300`
- Fetches price data and renders statistics
- Two-column layout: AI analysis (left) + news (right)

### Client Components

#### **SearchBar.tsx**
```typescript
'use client'
// Features:
// - Debounced search (300ms)
// - Autocomplete dropdown
// - Keyboard navigation
// - Focus management
// - NSE/BSE filtering

State:
- q: string (query)
- items: SearchResult[]
- open: boolean
- loading: boolean
```

#### **CompanyAI.tsx**
```typescript
'use client'
// Features:
// - Tabbed interface (Text vs Structured)
// - Loading states with abort controllers
// - Error handling with retry
// - Scrollable content area

State:
- text: string (completion result)
- structured: StructuredAnalysis | null
- loading: boolean
```

#### **NewsList.tsx**
```typescript
'use client'
// Features:
// - Lazy loading on mount
// - Link preview hover states
// - Source attribution
// - Published date formatting

State:
- items: NewsItem[]
- loading: boolean
```

#### **BookmarkButton.tsx**
```typescript
'use client'
// Features:
// - localStorage persistence
// - Star icon animation
// - Cross-tab sync (storage events)

State:
- saved: boolean
```

#### **BookmarksBar.tsx**
```typescript
'use client'
// Features:
// - Display recent bookmarks
// - Remove functionality
// - Horizontal scroll
// - Empty state

State:
- items: string[] (symbols)
```

#### **ThemeToggle.tsx**
```typescript
'use client'
// Features:
// - localStorage persistence
// - System preference detection
// - CSS variable updates

State:
- theme: 'light' | 'dark'
```

### Styling System

**CSS Variables** (defined in `globals.css`):
```css
:root {
  --bg: #ffffff;
  --text: #111827;
  --muted: #6b7280;
  --card: #f9fafb;
  --border: #e5e7eb;
  --primary: #3b82f6;
  --accent-1: #8b5cf6;
  --accent-2: #ec4899;
  --header-h: 56px;
}

[data-theme='dark'] {
  --bg: #0f172a;
  --text: #f1f5f9;
  --muted: #94a3b8;
  --card: #1e293b;
  --border: #334155;
}
```

**Utility Classes**:
- `.card` - Frosted glass effect with backdrop blur
- `.btn` - Gradient button with hover states
- `.input` - Styled input with focus ring
- `.hero` - Centered landing section
- `.grid`, `.stack` - Layout utilities
- `.clamp-2` - Text truncation to 2 lines

---

## Core Modules & Libraries

### Data Sources (lib/sources/)

#### **yahoo.ts**
```typescript
import yahooFinance from 'yahoo-finance2';

// Get 1-year OHLC data
export async function getDailyOHLC(symbol: string, period = '1y'): Promise<Candle[]>

// Get latest price
export async function getLastPrice(symbol: string): Promise<number>

// Search symbols with NSE/BSE filtering
export async function searchSymbols(query: string, count = 10): Promise<SearchResult[]>
```

#### **nse.ts**
```typescript
// Get NSE quote with session management
export async function getQuote(symbol: string): Promise<NSEQuote>

// Features:
// - Session-based authentication
// - User-agent spoofing
// - 5-min Redis caching
// - Graceful error handling
```

### News Aggregation (lib/news/)

#### **google.ts**
```typescript
import Parser from 'rss-parser';

// Fetch top N news items from Google News RSS
export async function getTopNews(query: string, count = 5): Promise<NewsItem[]>

// Returns: { title, link, source, pubDate }
```

### AI Integration (lib/ai/)

#### **modelRouter.ts**
```typescript
import { openai } from '@ai-sdk/openai';
import { createOpenAI } from '@ai-sdk/openai';

// Get OpenAI or OpenRouter client based on env vars
export function getOpenAI()

// Get default model ID with fallback
export function getDefaultModelId(): string

// Environment-based routing:
// 1. Check OPENROUTER_API_KEY → use OpenRouter
// 2. Check OPENAI_API_KEY → use OpenAI
// 3. Fallback to 'gpt-4o-mini'
```

### Technical Analysis (lib/tech/)

#### **indicators.ts**
```typescript
import { RSI, MACD, SMA, BollingerBands } from 'technicalindicators';

// Compute all indicators at once
export function computeBasicSignals(candles: Candle[]): TechnicalSignals

// Returns:
// - rsi: number (14-period)
// - macd: { macd, signal, histogram }
// - sma50, sma200: number
// - bollingerBands: { upper, middle, lower }
```

### Caching (lib/cache/)

#### **redis.ts**
```typescript
import Redis from 'ioredis';

// Generic cache wrapper with TTL
export async function cacheJson<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttlSec = 300
): Promise<T>

// Features:
// - Graceful fallback if Redis unavailable
// - JSON serialization
// - Configurable TTL
```

### Database (lib/db/)

#### **prisma.ts**
```typescript
import { PrismaClient } from '@prisma/client';

// Singleton pattern
declare global {
  var prisma: PrismaClient | undefined;
}

const prisma = globalThis.prisma ?? new PrismaClient();
if (process.env.NODE_ENV !== 'production') globalThis.prisma = prisma;

export default prisma;
```

### Agent (lib/agent/)

#### **graph.ts**
```typescript
import { z } from 'zod';

// Zod schemas for validation
export const AnalyzeRequestSchema = z.object({
  symbol: z.string(),
  userId: z.string().optional()
});

export const AnalyzeResponseSchema = z.object({
  symbol: z.string(),
  analysis: z.string(),
  confidence: z.number().min(0).max(1)
});

// Main agent function (currently stub)
export async function analyzeCompany(input: AnalyzeRequest): Promise<AnalyzeResponse>
```

---

## Development Workflow

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd stonky

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env  # Create this if missing
# Edit .env with your keys

# Generate Prisma client
npm run prisma:generate

# Run database migrations
npm run prisma:migrate

# Start development server
npm run dev
```

### Environment Variables

Create `.env` in project root:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/stonky

# Redis (optional)
REDIS_URL=redis://localhost:6379
REDIS_TOKEN=  # For Upstash/Vercel

# AI (choose one or both for fallback)
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=openai/gpt-4o-mini

# Future: Screener.in session
SCREENER_COOKIE=...
```

### Development Scripts

```bash
# Development server with hot reload
npm run dev

# Type checking without build
npm run typecheck

# Production build
npm run build

# Start production server
npm run start

# Database operations
npm run prisma:generate   # Regenerate Prisma client
npm run prisma:migrate    # Create/apply migrations
npx prisma studio         # GUI for database
```

### Git Workflow

Current branch: `claude/claude-md-mi53xef8fs1t1v4e-01SyyyA6FaBwWuAjdnGhd3HM`

```bash
# Always develop on designated Claude branches
git checkout claude/[branch-name]

# Commit with clear messages
git add .
git commit -m "feat: add comprehensive CLAUDE.md documentation"

# Push to remote (use -u for first push)
git push -u origin claude/[branch-name]
```

### Testing Strategy

**Current State**: No formal test framework yet

**Recommended Approach**:
1. Manual testing via `/api/*` endpoints
2. Type checking with `npm run typecheck`
3. Browser DevTools for UI components
4. Future: Add Vitest for unit tests

---

## Code Conventions

### TypeScript

- **Strict Mode**: Enabled in tsconfig.json
- **No Implicit Any**: All types must be explicit
- **Import Aliases**: Use `@/` for absolute imports
  ```typescript
  import prisma from '@/lib/db/prisma';  // ✅ Good
  import prisma from '../../../lib/db/prisma';  // ❌ Bad
  ```

### Naming Conventions

- **Files**:
  - Routes: `route.ts` for API, `page.tsx` for pages
  - Components: PascalCase (e.g., `SearchBar.tsx`)
  - Utilities: camelCase (e.g., `modelRouter.ts`)

- **Variables**:
  - Constants: UPPER_SNAKE_CASE
  - Functions: camelCase
  - Components: PascalCase
  - Types/Interfaces: PascalCase

### Component Structure

```typescript
'use client'  // Only for client components

import { useState, useEffect } from 'react';

interface Props {
  symbol: string;
  onComplete?: (data: any) => void;
}

export default function ComponentName({ symbol, onComplete }: Props) {
  const [state, setState] = useState<Type>(initialValue);

  useEffect(() => {
    // Side effects
  }, [dependencies]);

  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

### API Route Structure

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const RequestSchema = z.object({
  symbol: z.string(),
  // ...
});

export async function GET(request: NextRequest) {
  try {
    // Parse query params
    const { searchParams } = new URL(request.url);
    const symbol = searchParams.get('symbol');

    // Validate
    const validated = RequestSchema.parse({ symbol });

    // Process
    const result = await fetchData(validated.symbol);

    // Return
    return NextResponse.json(result, {
      headers: {
        'cache-control': 'public, s-maxage=300, stale-while-revalidate=60'
      }
    });
  } catch (error) {
    return NextResponse.json(
      { error: error.message },
      { status: 400 }
    );
  }
}
```

### Error Handling

```typescript
// Graceful degradation pattern
let result;
try {
  result = await riskyOperation();
} catch (error) {
  console.error('Operation failed, using fallback:', error);
  result = fallbackValue;
}

// Zod validation pattern
const parsed = RequestSchema.safeParse(input);
if (!parsed.success) {
  return NextResponse.json(
    { error: 'Invalid input', details: parsed.error },
    { status: 400 }
  );
}
```

### Async Patterns

```typescript
// Prefer async/await over .then()
const data = await fetchData();  // ✅ Good
fetchData().then(data => ...);    // ❌ Bad

// Use Promise.all for parallel requests
const [prices, news] = await Promise.all([
  fetchPrices(symbol),
  fetchNews(symbol)
]);

// Use AbortController for cancellable requests
const controller = new AbortController();
fetch(url, { signal: controller.signal });
// ... later
controller.abort();
```

---

## Environment Variables

### Required

```bash
# Database connection string
DATABASE_URL=postgresql://user:pass@localhost:5432/stonky
```

### Optional (with graceful fallbacks)

```bash
# Redis caching (falls back to direct fetching)
REDIS_URL=redis://localhost:6379
REDIS_TOKEN=  # For managed Redis

# AI/LLM (falls back to mock responses or errors)
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=openai/gpt-4o-mini

# Future features
SCREENER_COOKIE=  # For Screener.in data scraping
NSE_SESSION=      # For NSE advanced APIs
```

### Environment Detection

```typescript
// The app detects available services:
const hasRedis = !!process.env.REDIS_URL;
const hasOpenAI = !!process.env.OPENAI_API_KEY;
const hasOpenRouter = !!process.env.OPENROUTER_API_KEY;

// And degrades gracefully when unavailable
```

---

## Common Tasks

### Adding a New Data Source

1. **Create service file**: `lib/sources/newSource.ts`
   ```typescript
   export async function fetchData(symbol: string) {
     // Implementation
   }
   ```

2. **Add Zod schema** for validation:
   ```typescript
   import { z } from 'zod';
   const ResponseSchema = z.object({
     // Define structure
   });
   ```

3. **Create API route**: `app/api/newsource/route.ts`
   ```typescript
   import { fetchData } from '@/lib/sources/newSource';
   export async function GET(request: NextRequest) {
     // Handle request
   }
   ```

4. **Add caching** if appropriate:
   ```typescript
   import { cacheJson } from '@/lib/cache/redis';
   const result = await cacheJson(
     `newsource:${symbol}`,
     () => fetchData(symbol),
     300  // 5-min TTL
   );
   ```

### Adding a New Component

1. **Create component file**: `app/components/NewComponent.tsx`
   ```typescript
   'use client'  // If needs interactivity

   interface Props {
     // Define props
   }

   export default function NewComponent({ }: Props) {
     return <div>...</div>;
   }
   ```

2. **Add to page**:
   ```typescript
   import NewComponent from '@/app/components/NewComponent';
   <NewComponent {...props} />
   ```

3. **Update globals.css** if new styles needed

### Extending the Database Schema

1. **Update schema**: `prisma/schema.prisma`
   ```prisma
   model NewModel {
     id        String   @id @default(cuid())
     // fields
     createdAt DateTime @default(now())
   }
   ```

2. **Create migration**:
   ```bash
   npm run prisma:migrate
   # Enter migration name when prompted
   ```

3. **Regenerate client**:
   ```bash
   npm run prisma:generate
   ```

4. **Use in code**:
   ```typescript
   import prisma from '@/lib/db/prisma';
   const items = await prisma.newModel.findMany();
   ```

### Adding a New AI Feature

1. **Define Zod schemas**:
   ```typescript
   const RequestSchema = z.object({
     prompt: z.string(),
     context: z.string().optional()
   });
   ```

2. **Create AI endpoint**: `app/api/ai/newfeature/route.ts`
   ```typescript
   import { getOpenAI, getDefaultModelId } from '@/lib/ai/modelRouter';
   import { generateText } from 'ai';

   const client = getOpenAI();
   const model = getDefaultModelId();

   const response = await generateText({
     model: client(model),
     prompt: validated.prompt
   });
   ```

3. **Add UI component** to trigger the feature

### Adding Technical Indicators

1. **Update lib/tech/indicators.ts**:
   ```typescript
   import { NewIndicator } from 'technicalindicators';

   export function computeNewSignal(candles: Candle[]) {
     return NewIndicator.calculate({
       values: candles.map(c => c.close),
       period: 14
     });
   }
   ```

2. **Use in analysis**:
   ```typescript
   const signals = computeBasicSignals(candles);
   const newSignal = computeNewSignal(candles);
   ```

---

## Important Gotchas

### 1. Symbol Format Inconsistencies

Yahoo Finance uses `.NS` or `.BO` suffixes:
```typescript
// Correct:
"RELIANCE.NS"  // NSE
"RELIANCE.BO"  // BSE

// Incorrect:
"RELIANCE"  // Won't work with Yahoo Finance API
```

Always append exchange suffix when calling Yahoo APIs.

### 2. Missing Schema Relations

The Prisma schema is missing back-relations:
```prisma
// TODO: Add to Company model
model Company {
  // ... existing fields
  filings Filing[]    // ← Missing
  news    NewsItem[]  // ← Missing
}

// TODO: Add to User model
model User {
  // ... existing fields
  alertRules AlertRule[]  // ← Missing
}

// TODO: Add to AlertRule model
model AlertRule {
  // ... existing fields
  events AlertEvent[]  // ← Missing
}
```

When doing Prisma queries with relations, you'll encounter errors until these are added.

### 3. Redis is Optional

Don't assume Redis is available:
```typescript
// Good: Graceful fallback
const data = await cacheJson(key, fetcher, ttl);

// Bad: Direct Redis access
const cached = await redis.get(key);  // Will fail if no Redis
```

The `cacheJson` helper handles fallback automatically.

### 4. AI Keys May Be Missing

Always check for AI availability:
```typescript
const client = getOpenAI();
if (!client) {
  return NextResponse.json(
    { error: 'AI service not configured' },
    { status: 503 }
  );
}
```

### 5. ISR Caching Behavior

Company pages use ISR with 5-minute revalidation:
```typescript
export const revalidate = 300;  // 5 minutes
```

During development, stale data may appear. Clear `.next` cache if needed:
```bash
rm -rf .next
npm run dev
```

### 6. Client Component Hydration

Dynamic imports are used to prevent hydration mismatches:
```typescript
// Good: Dynamic import for client components with localStorage
const SearchBar = dynamic(() => import('./components/SearchBar'), {
  ssr: false
});

// Bad: Direct import
import SearchBar from './components/SearchBar';  // May cause hydration errors
```

### 7. NSE API Rate Limiting

NSE APIs have aggressive rate limiting and require:
- Valid user-agent headers
- Session cookies
- Retry logic with backoff

The `nse.ts` module handles this, but be aware of rate limits during testing.

### 8. TypeScript Strict Mode

The project uses strict TypeScript. Common issues:
```typescript
// Error: Type 'string | undefined' is not assignable
const symbol = searchParams.get('symbol');  // string | null
if (!symbol) {
  return error;  // ✅ Check before using
}

// Error: Object is possibly 'null'
const result = await prisma.company.findUnique({
  where: { symbol }
});
if (!result) return error;  // ✅ Check before accessing
```

Always handle null/undefined cases explicitly.

---

## Future Roadmap

### Phase 1: MVP (Screener Plus) - Current State
- ✅ Stock search and price data
- ✅ News aggregation
- ✅ Basic AI analysis
- ⚠️ Bookmarks (localStorage, needs DB migration)

### Phase 2: AI Analyst (Next Steps)
- ❌ RAG implementation with vector DB (Pinecone/pgvector)
- ❌ PDF downloading from NSE (Annual Reports, Concalls)
- ❌ OCR/text extraction pipeline
- ❌ Embedding generation (OpenAI Embeddings)
- ❌ Semantic search over documents
- ❌ "Chat with PDF" feature
- ❌ Complete agent implementation (`lib/agent/graph.ts`)

### Phase 3: Portfolio & Alerts
- ❌ User authentication (NextAuth.js or Clerk)
- ❌ Subscription tier gating
- ❌ Portfolio tracking with auto-updates
- ❌ Alert rule execution engine
- ❌ Email notifications (SendGrid/Resend)
- ❌ Quarterly result scanner

### Phase 4: Advanced Features
- ❌ Real-time WebSocket price updates
- ❌ Advanced charting (TradingView widgets)
- ❌ Screener.in integration (10-year fundamentals)
- ❌ Multi-stock comparison
- ❌ API access tier for developers
- ❌ Mobile app (React Native)

### Technical Debt & Improvements
- ❌ Add ESLint and Prettier
- ❌ Set up test framework (Vitest)
- ❌ Add E2E tests (Playwright)
- ❌ Implement proper logging (Pino/Winston)
- ❌ Add monitoring (Sentry)
- ❌ Performance optimization (React Compiler)
- ❌ SEO optimization (meta tags, sitemap)
- ❌ Accessibility audit (WCAG compliance)

---

## Working with This Codebase

### As an AI Assistant

When working on this project:

1. **Read the docs**: Check `/docs/plan-final.md` for product vision
2. **Understand the framework**: The "Refined Framework 2025" is the business logic
3. **Follow patterns**: Use existing code as templates
4. **Validate inputs**: Always use Zod for external data
5. **Type safety first**: No `any` types unless absolutely necessary
6. **Graceful degradation**: Optional services should fail gracefully
7. **Keep it simple**: No unnecessary abstractions or frameworks

### Key Files to Reference

- **Architecture**: `docs/plan-final.md`
- **Schema**: `prisma/schema.prisma`
- **API patterns**: `app/api/prices/[symbol]/route.ts`
- **Component patterns**: `app/components/CompanyAI.tsx`
- **Data source patterns**: `lib/sources/yahoo.ts`

### Testing Your Changes

```bash
# Type check
npm run typecheck

# Test API endpoint
curl http://localhost:3000/api/search?q=RELIANCE

# Test component in browser
npm run dev
# Navigate to http://localhost:3000
```

### Getting Help

- **Docs**: `/docs` folder has comprehensive planning docs
- **Code examples**: Every module has clear patterns to follow
- **Type definitions**: Hover in VSCode for inline documentation
- **Prisma Studio**: `npx prisma studio` for database inspection

---

## Conclusion

Stonky is a well-architected, type-safe platform with clear patterns and conventions. The codebase prioritizes simplicity, modularity, and graceful degradation. By following the patterns established in existing code and understanding the product vision in `/docs/plan-final.md`, you can confidently extend and improve the platform.

**Remember**: The goal is to build "The depth of a Hedge Fund Analyst, the speed of a click." Every feature should serve this vision.

---

**Last Updated**: 2025-11-18
**Version**: 0.1.0
**Maintained By**: Stonky Development Team
