"""
Services package for external data sources.

This package contains services for fetching data from:
- Screener.in (10-year fundamentals)
- NSE (shareholding, quotes)
- Yahoo Finance (prices, technicals)
- News aggregators

All services follow the BaseService pattern for consistent
error handling, logging, and timeout management.
"""

from app.services.base import (
    BaseService,
    ServiceError,
    ServiceTimeoutError,
    ServiceUnavailableError
)
from app.services.screener import ScreenerService
from app.services.nse import NSEService
from app.services.yahoo import YahooFinanceService
from app.services.news import NewsService

__all__ = [
    # Base classes
    'BaseService',
    'ServiceError',
    'ServiceTimeoutError',
    'ServiceUnavailableError',
    # Services
    'ScreenerService',
    'NSEService',
    'YahooFinanceService',
    'NewsService',
]
