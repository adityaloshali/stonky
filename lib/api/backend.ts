/**
 * Backend API client for Stonky.
 *
 * Provides typed interfaces to the FastAPI backend.
 */

// API Configuration
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1 = `${API_BASE}/api/v1`;

// Types
export interface StockQuote {
  symbol: string;
  name: string | null;
  current_price: number;
  previous_close: number | null;
  open: number | null;
  day_high: number | null;
  day_low: number | null;
  volume: number | null;
  change: number | null;
  percent_change: number | null;
  market_cap: number | null;
  pe_ratio: number | null;
  week_52_high: number | null;
  week_52_low: number | null;
  timestamp: string;
}

export interface PriceData {
  date: string;
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PricesResponse {
  symbol: string;
  period: string;
  interval: string;
  prices: PriceData[];
  count: number;
}

export interface NewsArticle {
  title: string;
  link: string;
  source: string;
  published: string;
  summary?: string | null;
}

export interface NewsResponse {
  symbol?: string | null;
  query: string;
  articles: NewsArticle[];
  count: number;
}

export interface FundamentalsResponse {
  symbol: string;
  years: string[];
  revenue: (number | null)[];
  net_profit: (number | null)[];
  roce: (number | null)[];
  roe: (number | null)[];
  debt_to_equity: (number | null)[];
  eps: (number | null)[];
  book_value: (number | null)[];
  pe_ratio: (number | null)[];
  market_cap: (number | null)[];
  source: string;
}

export interface TechnicalIndicators {
  current_price: number;
  sma_20: number | null;
  sma_50: number | null;
  sma_200: number | null;
  rsi_14: number | null;
  momentum_percent: number | null;
  trend: string | null;
  rsi_signal: string | null;
}

export interface SearchResult {
  symbol: string;
  name: string;
  exchange: string;
  sector: string | null;
  industry: string | null;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  count: number;
}

export interface ShareholdingPattern {
  promoter_percentage: number | null;
  fii_percentage: number | null;
  dii_percentage: number | null;
  public_percentage: number | null;
  promoter_pledged_percentage: number | null;
  date: string | null;
}

// API Client Functions

/**
 * Search for stock symbols
 */
export async function searchSymbols(query: string, limit = 10): Promise<SearchResponse> {
  const response = await fetch(
    `${API_V1}/search?q=${encodeURIComponent(query)}&limit=${limit}`
  );
  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get current quote for a symbol
 */
export async function getQuote(symbol: string): Promise<StockQuote> {
  const cleanSymbol = symbol.replace('.NS', '').replace('.BO', '');
  const response = await fetch(`${API_V1}/company/${cleanSymbol}/quote`);
  if (!response.ok) {
    throw new Error(`Failed to fetch quote: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get historical price data
 */
export async function getPrices(
  symbol: string,
  period: string = '1y',
  interval: string = '1d'
): Promise<PricesResponse> {
  const cleanSymbol = symbol.replace('.NS', '').replace('.BO', '');
  const response = await fetch(
    `${API_V1}/prices/${cleanSymbol}?period=${period}&interval=${interval}`
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch prices: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get technical indicators
 */
export async function getTechnicals(
  symbol: string,
  period: string = '1y'
): Promise<TechnicalIndicators> {
  const cleanSymbol = symbol.replace('.NS', '').replace('.BO', '');
  const response = await fetch(
    `${API_V1}/prices/${cleanSymbol}/technicals?period=${period}`
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch technicals: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get news for a symbol
 */
export async function getNews(symbol: string, limit = 10): Promise<NewsResponse> {
  const cleanSymbol = symbol.replace('.NS', '').replace('.BO', '');
  const response = await fetch(
    `${API_V1}/news/${cleanSymbol}?limit=${limit}`
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch news: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get market news
 */
export async function getMarketNews(limit = 15): Promise<NewsResponse> {
  const response = await fetch(`${API_V1}/news/market/india?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch market news: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get fundamentals (10-year data)
 */
export async function getFundamentals(symbol: string): Promise<FundamentalsResponse> {
  const cleanSymbol = symbol.replace('.NS', '').replace('.BO', '');
  const response = await fetch(`${API_V1}/fundamentals/${cleanSymbol}`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Failed to fetch fundamentals');
  }
  return response.json();
}

/**
 * Get shareholding pattern
 */
export async function getShareholding(symbol: string): Promise<ShareholdingPattern> {
  const cleanSymbol = symbol.replace('.NS', '').replace('.BO', '');
  const response = await fetch(`${API_V1}/company/${cleanSymbol}/shareholding`);
  if (!response.ok) {
    throw new Error(`Failed to fetch shareholding: ${response.statusText}`);
  }
  return response.json();
}

// Helper function to format numbers
export function formatNumber(value: number | null | undefined, decimals = 2): string {
  if (value == null) return '-';
  return value.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

// Helper function to format currency
export function formatCurrency(value: number | null | undefined, currency = '₹'): string {
  if (value == null) return '-';
  return `${currency}${formatNumber(value, 2)}`;
}

// Helper function to format large numbers (crores, lakhs)
export function formatLargeNumber(value: number | null | undefined): string {
  if (value == null) return '-';

  const abs = Math.abs(value);
  if (abs >= 10000000) {
    // Crores
    return `${(value / 10000000).toFixed(2)} Cr`;
  } else if (abs >= 100000) {
    // Lakhs
    return `${(value / 100000).toFixed(2)} L`;
  } else if (abs >= 1000) {
    // Thousands
    return `${(value / 1000).toFixed(2)} K`;
  }
  return formatNumber(value, 2);
}
