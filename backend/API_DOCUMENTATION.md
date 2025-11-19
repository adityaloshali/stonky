# Stonky API v1 Documentation

**Base URL:** `http://localhost:8000/api/v1`

**Production URL:** `https://your-domain.com/api/v1`

---

## Overview

The Stonky API provides comprehensive stock market data for Indian stocks (NSE/BSE) including:
- Real-time quotes and prices
- Historical OHLC data
- Technical indicators
- Company fundamentals (10-year data)
- News aggregation
- Shareholding patterns

**Interactive Docs:** http://localhost:8000/docs (when running locally)

---

## Authentication

Currently, the API is **open** (no authentication required).

**Note:** The `/fundamentals` endpoint requires `SCREENER_COOKIE` to be configured in the backend `.env` file.

---

## Endpoints

### 1. Search

#### `GET /search`

Search for stock symbols by company name or symbol.

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional): Max results (1-50, default: 10)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/search?q=RELIANCE&limit=5"
```

**Example Response:**
```json
{
  "query": "RELIANCE",
  "results": [
    {
      "symbol": "RELIANCE.NS",
      "name": "Reliance Industries Limited",
      "exchange": "NSE",
      "sector": "Energy",
      "industry": "Oil & Gas Refining & Marketing"
    }
  ],
  "count": 1
}
```

---

### 2. Company Information

#### `GET /company/{symbol}/quote`

Get current quote and market data for a stock.

**Path Parameters:**
- `symbol`: Stock symbol (without .NS suffix)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/company/RELIANCE/quote"
```

**Example Response:**
```json
{
  "symbol": "RELIANCE.NS",
  "name": "Reliance Industries Limited",
  "current_price": 1515.90,
  "previous_close": 1519.40,
  "open": 1517.40,
  "day_high": 1520.80,
  "day_low": 1512.00,
  "volume": 1618283,
  "change": -3.50,
  "percent_change": -0.23,
  "market_cap": 20514630270976,
  "pe_ratio": 24.70,
  "week_52_high": 1551.00,
  "week_52_low": 1114.85,
  "timestamp": "2025-11-19T12:00:00"
}
```

---

#### `GET /company/{symbol}/info`

Get basic company information.

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/company/TCS/info"
```

**Example Response:**
```json
{
  "symbol": "TCS.NS",
  "name": "Tata Consultancy Services Limited",
  "sector": "Technology",
  "industry": "Information Technology Services",
  "market_cap": 1234567890000
}
```

---

#### `GET /company/{symbol}/shareholding`

Get shareholding pattern from NSE (Promoter, FII, DII, pledging).

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/company/RELIANCE/shareholding"
```

**Example Response:**
```json
{
  "promoter_percentage": 50.39,
  "fii_percentage": 24.56,
  "dii_percentage": 15.23,
  "public_percentage": 9.82,
  "promoter_pledged_percentage": 0.00,
  "date": "2025-Q2"
}
```

**Note:** NSE data may not always be available due to rate limiting or API restrictions.

---

### 3. Price Data

#### `GET /prices/{symbol}`

Get historical OHLC price data.

**Query Parameters:**
- `period` (optional): 1d, 5d, 1mo, 3mo, 6mo, 1y (default), 2y, 5y, 10y, ytd, max
- `interval` (optional): 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d (default), 5d, 1wk, 1mo, 3mo

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/prices/RELIANCE?period=1mo&interval=1d"
```

**Example Response:**
```json
{
  "symbol": "RELIANCE.NS",
  "period": "1mo",
  "interval": "1d",
  "count": 21,
  "prices": [
    {
      "date": "2025-10-20",
      "timestamp": 1729382400,
      "open": 1500.25,
      "high": 1520.00,
      "low": 1495.50,
      "close": 1515.90,
      "volume": 5234567
    },
    ...
  ]
}
```

---

#### `GET /prices/{symbol}/technicals`

Get technical indicators (SMA, RSI, trend analysis).

**Query Parameters:**
- `period` (optional): Time period for calculation (default: 1y)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/prices/RELIANCE/technicals"
```

**Example Response:**
```json
{
  "current_price": 1515.90,
  "sma_20": 1510.45,
  "sma_50": 1505.20,
  "sma_200": 1480.75,
  "rsi_14": 58.32,
  "momentum_percent": 12.45,
  "trend": "uptrend",
  "rsi_signal": "neutral"
}
```

**Trend Values:**
- `strong_uptrend`: Price > SMA20 > SMA50 > SMA200
- `uptrend`: Price > SMA50 > SMA200
- `sideways`: Mixed signals
- `downtrend`: Price < SMA50 < SMA200
- `strong_downtrend`: Price < SMA20 < SMA50 < SMA200

**RSI Signals:**
- `overbought`: RSI > 70
- `oversold`: RSI < 30
- `neutral`: RSI between 30-70

---

### 4. News

#### `GET /news?q={query}`

Get news articles for a search query.

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional): Number of articles (1-50, default: 10)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/news?q=Reliance&limit=5"
```

---

#### `GET /news/{symbol}`

Get company-specific news.

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/news/RELIANCE?limit=5"
```

**Example Response:**
```json
{
  "symbol": "RELIANCE",
  "query": "RELIANCE stock India",
  "count": 5,
  "articles": [
    {
      "title": "Reliance Industries reports strong Q2 earnings",
      "link": "https://...",
      "source": "The Economic Times",
      "published": "2025-11-18T10:00:00",
      "summary": "Reliance Industries..."
    },
    ...
  ]
}
```

---

#### `GET /news/market/india`

Get general Indian stock market news.

**Query Parameters:**
- `limit` (optional): Number of articles (default: 15)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/news/market/india"
```

---

#### `GET /news/sector/{sector}`

Get sector-specific news.

**Path Parameters:**
- `sector`: Sector name (IT, Banking, Pharma, Auto, etc.)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/news/sector/IT?limit=10"
```

---

### 5. Fundamentals (10-Year Data)

#### `GET /fundamentals/{symbol}`

Get 10-year fundamental data from Screener.in.

**Path Parameters:**
- `symbol`: NSE stock symbol (without .NS suffix)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/fundamentals/RELIANCE"
```

**Example Response:**
```json
{
  "symbol": "RELIANCE",
  "years": ["Mar 2024", "Mar 2023", "Mar 2022", ...],
  "revenue": [960000, 920000, 880000, ...],
  "net_profit": [73000, 67000, 61000, ...],
  "roce": [12.5, 11.8, 10.9, ...],
  "roe": [9.8, 9.2, 8.5, ...],
  "debt_to_equity": [0.54, 0.62, 0.71, ...],
  "eps": [54.0, 49.5, 45.2, ...],
  "book_value": [550.0, 520.0, 490.0, ...],
  "pe_ratio": [28.1, 26.5, 24.8, ...],
  "market_cap": [2051463, 1950000, 1850000, ...],
  "source": "screener.in"
}
```

**Setup Required:**

This endpoint requires a Screener.in session cookie. To set it up:

1. Login to https://www.screener.in
2. Open DevTools (F12) → Application → Cookies
3. Copy the `sessionid` cookie value
4. Add to `backend/.env`:
   ```bash
   SCREENER_COOKIE=your_session_id_here
   ```

**Error Responses:**

- `503`: Cookie not configured
  ```json
  {
    "detail": "Screener service not configured. Please set SCREENER_COOKIE in .env file."
  }
  ```

- `401`: Cookie expired
  ```json
  {
    "detail": "Screener.in session expired. Please update SCREENER_COOKIE in .env file."
  }
  ```

- `404`: Symbol not found
  ```json
  {
    "detail": "Company 'INVALID' not found on Screener.in."
  }
  ```

---

## Error Handling

All endpoints return errors in a consistent format:

**Error Response:**
```json
{
  "detail": "Error message here"
}
```

**HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (expired credentials)
- `404`: Not Found (symbol/company not found)
- `500`: Internal Server Error
- `503`: Service Unavailable (external API down)

---

## Rate Limiting

Currently, there is **no rate limiting** on the API.

However, please note:
- **NSE**: May rate-limit requests (403 errors)
- **Screener.in**: Session cookie required, limited by Screener's own limits
- **Yahoo Finance**: Generally reliable, but may throttle excessive requests
- **Google News**: RSS-based, very reliable

---

## Data Sources

| Endpoint | Source | Authentication | Reliability |
|----------|--------|----------------|-------------|
| Search | Yahoo Finance | None | High |
| Quote | Yahoo Finance | None | High |
| Company Info | Yahoo Finance | None | High |
| Shareholding | NSE | None (session-based) | Medium |
| Prices | Yahoo Finance | None | High |
| Technicals | Yahoo Finance | None | High |
| News | Google News RSS | None | High |
| Fundamentals | Screener.in | Cookie required | High (if configured) |

---

## Frontend Integration Example

### React/Next.js

```typescript
// lib/api/client.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getQuote(symbol: string) {
  const response = await fetch(`${API_BASE}/api/v1/company/${symbol}/quote`);
  if (!response.ok) throw new Error('Failed to fetch quote');
  return response.json();
}

export async function getPrices(symbol: string, period = '1y') {
  const response = await fetch(
    `${API_BASE}/api/v1/prices/${symbol}?period=${period}`
  );
  if (!response.ok) throw new Error('Failed to fetch prices');
  return response.json();
}

export async function getNews(symbol: string, limit = 5) {
  const response = await fetch(
    `${API_BASE}/api/v1/news/${symbol}?limit=${limit}`
  );
  if (!response.ok) throw new Error('Failed to fetch news');
  return response.json();
}

export async function getFundamentals(symbol: string) {
  const response = await fetch(`${API_BASE}/api/v1/fundamentals/${symbol}`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch fundamentals');
  }
  return response.json();
}
```

### Usage in Component

```typescript
'use client';
import { useEffect, useState } from 'react';
import { getQuote, getPrices, getNews } from '@/lib/api/client';

export function StockDashboard({ symbol }: { symbol: string }) {
  const [quote, setQuote] = useState(null);
  const [prices, setPrices] = useState(null);
  const [news, setNews] = useState([]);

  useEffect(() => {
    async function loadData() {
      const [quoteData, pricesData, newsData] = await Promise.all([
        getQuote(symbol),
        getPrices(symbol, '1y'),
        getNews(symbol, 5)
      ]);

      setQuote(quoteData);
      setPrices(pricesData);
      setNews(newsData.articles);
    }

    loadData();
  }, [symbol]);

  return (
    <div>
      {quote && (
        <div>
          <h1>{quote.name}</h1>
          <p>₹{quote.current_price.toFixed(2)}</p>
          <p className={quote.change >= 0 ? 'text-green' : 'text-red'}>
            {quote.change >= 0 ? '+' : ''}{quote.percent_change.toFixed(2)}%
          </p>
        </div>
      )}

      {/* Render prices chart */}
      {/* Render news list */}
    </div>
  );
}
```

---

## Testing

### With curl

```bash
# Test search
curl "http://localhost:8000/api/v1/search?q=TCS"

# Test quote
curl "http://localhost:8000/api/v1/company/RELIANCE/quote"

# Test prices
curl "http://localhost:8000/api/v1/prices/INFY?period=1mo"

# Test news
curl "http://localhost:8000/api/v1/news/TCS?limit=3"

# Test fundamentals (requires cookie)
curl "http://localhost:8000/api/v1/fundamentals/RELIANCE"
```

### With Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Get quote
response = requests.get(f"{BASE_URL}/company/RELIANCE/quote")
quote = response.json()
print(f"{quote['name']}: ₹{quote['current_price']}")

# Get prices
response = requests.get(f"{BASE_URL}/prices/TCS", params={"period": "1mo"})
prices = response.json()
print(f"Retrieved {prices['count']} days of data")

# Get news
response = requests.get(f"{BASE_URL}/news/INFY", params={"limit": 5})
news = response.json()
for article in news['articles']:
    print(f"- {article['title']} ({article['source']})")
```

---

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/adityaloshali/stonky/issues
- **Documentation**: http://localhost:8000/docs (when running locally)

---

**Last Updated:** November 19, 2025
**API Version:** v1
**Backend Version:** 2.0.0
