"""
Response schemas for API endpoints.

These Pydantic models define the structure of API responses.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class StockSearchResult(BaseModel):
    """Single stock search result."""
    symbol: str = Field(..., description="Stock symbol (e.g., 'RELIANCE.NS')")
    name: str = Field(..., description="Company name")
    exchange: str = Field(..., description="Exchange (NSE/BSE)")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")


class SearchResponse(BaseModel):
    """Response for symbol search."""
    query: str = Field(..., description="Search query")
    results: List[StockSearchResult] = Field(default_factory=list, description="Search results")
    count: int = Field(..., description="Number of results")


class CompanyInfo(BaseModel):
    """Basic company information."""
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None


class PriceData(BaseModel):
    """Single OHLC price data point."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    timestamp: int = Field(..., description="Unix timestamp")
    open: float
    high: float
    low: float
    close: float
    volume: int


class PricesResponse(BaseModel):
    """Response for historical prices."""
    symbol: str
    period: str = Field(..., description="Time period (1d, 1mo, 1y, etc.)")
    interval: str = Field(..., description="Data interval (1d, 1h, etc.)")
    prices: List[PriceData] = Field(default_factory=list)
    count: int = Field(..., description="Number of data points")


class QuoteResponse(BaseModel):
    """Response for current stock quote."""
    symbol: str
    name: Optional[str] = None
    current_price: float = Field(..., description="Current/last price")
    previous_close: Optional[float] = None
    open: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    volume: Optional[int] = None
    change: Optional[float] = Field(None, description="Absolute change")
    percent_change: Optional[float] = Field(None, description="Percentage change")
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ShareholdingPattern(BaseModel):
    """Shareholding pattern data."""
    promoter_percentage: Optional[float] = Field(None, description="Promoter holding %")
    fii_percentage: Optional[float] = Field(None, description="FII holding %")
    dii_percentage: Optional[float] = Field(None, description="DII holding %")
    public_percentage: Optional[float] = Field(None, description="Public holding %")
    promoter_pledged_percentage: Optional[float] = Field(None, description="Promoter pledging %")
    date: Optional[str] = Field(None, description="Data date")


class NewsArticle(BaseModel):
    """Single news article."""
    title: str
    link: str
    source: str
    published: str = Field(..., description="ISO format datetime")
    summary: Optional[str] = None


class NewsResponse(BaseModel):
    """Response for news feed."""
    symbol: Optional[str] = None
    query: str
    articles: List[NewsArticle] = Field(default_factory=list)
    count: int


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators."""
    current_price: float
    sma_20: Optional[float] = Field(None, description="20-day Simple Moving Average")
    sma_50: Optional[float] = Field(None, description="50-day Simple Moving Average")
    sma_200: Optional[float] = Field(None, description="200-day Simple Moving Average")
    rsi_14: Optional[float] = Field(None, description="14-day RSI")
    momentum_percent: Optional[float] = Field(None, description="Price momentum %")
    trend: Optional[str] = Field(None, description="Trend description")
    rsi_signal: Optional[str] = Field(None, description="RSI signal (overbought/oversold/neutral)")


class FundamentalsResponse(BaseModel):
    """Response for fundamental data (10-year)."""
    symbol: str
    years: List[str] = Field(default_factory=list, description="Year labels")
    revenue: List[Optional[float]] = Field(default_factory=list)
    net_profit: List[Optional[float]] = Field(default_factory=list)
    roce: List[Optional[float]] = Field(default_factory=list, description="ROCE %")
    roe: List[Optional[float]] = Field(default_factory=list, description="ROE %")
    debt_to_equity: List[Optional[float]] = Field(default_factory=list)
    eps: List[Optional[float]] = Field(default_factory=list)
    book_value: List[Optional[float]] = Field(default_factory=list)
    pe_ratio: List[Optional[float]] = Field(default_factory=list)
    market_cap: List[Optional[float]] = Field(default_factory=list)
    source: str = Field(default="screener.in")


class ErrorResponse(BaseModel):
    """Error response."""
    status: str = Field(default="error")
    message: str
    error_type: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
