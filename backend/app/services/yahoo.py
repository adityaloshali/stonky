"""
Yahoo Finance service for stock prices and market data.

Uses the yfinance library to fetch:
- Historical OHLC (Open, High, Low, Close) data
- Current prices
- Technical indicators
- Company information
- Symbol search

Note: Yahoo Finance data has a 15-minute delay for free tier.
"""

from typing import Dict, Any, List, Optional
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger

from app.services.base import BaseService, ServiceError


class YahooFinanceService(BaseService):
    """
    Service for fetching market data from Yahoo Finance.

    Uses the yfinance library which provides a reliable interface
    to Yahoo Finance's unofficial API.
    """

    # Valid period values for yfinance
    VALID_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

    # Valid interval values
    VALID_INTERVALS = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']

    def __init__(self, timeout: int = 30):
        """
        Initialize Yahoo Finance service.

        Args:
            timeout: Request timeout in seconds
        """
        super().__init__(timeout=timeout)

    async def fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch comprehensive data for a stock from Yahoo Finance.

        Args:
            symbol: Yahoo Finance symbol (e.g., 'RELIANCE.NS', 'TCS.BO')

        Returns:
            Dictionary with price data, info, and financials

        Raises:
            ServiceError: If fetch fails
        """
        symbol = self._validate_symbol(symbol)
        symbol = self._ensure_suffix(symbol)

        self.logger.info(f"Fetching data from Yahoo Finance for {symbol}")

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            # Run yfinance operations in executor (they are synchronous)
            result = await loop.run_in_executor(
                None, self._fetch_data_sync, symbol
            )
            return result

        except Exception as e:
            return self._handle_error(e, f"Failed to fetch Yahoo Finance data for {symbol}")

    def _fetch_data_sync(self, symbol: str) -> Dict[str, Any]:
        """
        Synchronous fetch of Yahoo Finance data.

        Args:
            symbol: Yahoo Finance symbol

        Returns:
            Dictionary with comprehensive stock data
        """
        try:
            ticker = yf.Ticker(symbol)

            # Get basic info
            info = ticker.info

            # Get latest price
            hist = ticker.history(period='5d')

            if hist.empty:
                raise ServiceError(f"No data found for symbol '{symbol}'")

            latest = hist.iloc[-1]

            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', None),
                'industry': info.get('industry', None),
                'current_price': latest['Close'],
                'previous_close': info.get('previousClose', latest['Close']),
                'open': latest['Open'],
                'day_high': latest['High'],
                'day_low': latest['Low'],
                'volume': latest['Volume'],
                'market_cap': info.get('marketCap', None),
                'pe_ratio': info.get('trailingPE', None),
                'dividend_yield': info.get('dividendYield', None),
                'week_52_high': info.get('fiftyTwoWeekHigh', None),
                'week_52_low': info.get('fiftyTwoWeekLow', None),
                'source': 'yahoo_finance',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            raise ServiceError(f"Failed to fetch data from Yahoo Finance: {e}")

    async def get_prices(
        self,
        symbol: str,
        period: str = '1y',
        interval: str = '1d'
    ) -> Dict[str, Any]:
        """
        Get historical OHLC price data.

        Args:
            symbol: Yahoo Finance symbol (e.g., 'RELIANCE.NS')
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            Dictionary with OHLC data
        """
        symbol = self._validate_symbol(symbol)
        symbol = self._ensure_suffix(symbol)

        if period not in self.VALID_PERIODS:
            raise ValueError(f"Invalid period. Must be one of: {', '.join(self.VALID_PERIODS)}")

        if interval not in self.VALID_INTERVALS:
            raise ValueError(f"Invalid interval. Must be one of: {', '.join(self.VALID_INTERVALS)}")

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            result = await loop.run_in_executor(
                None, self._get_prices_sync, symbol, period, interval
            )
            return result

        except Exception as e:
            return self._handle_error(e, f"Failed to get prices for {symbol}")

    def _get_prices_sync(self, symbol: str, period: str, interval: str) -> Dict[str, Any]:
        """
        Synchronous fetch of historical prices.

        Args:
            symbol: Yahoo Finance symbol
            period: Time period
            interval: Data interval

        Returns:
            Dictionary with OHLC data
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                raise ServiceError(f"No price data found for {symbol}")

            # Convert DataFrame to list of dictionaries
            prices = []
            for index, row in hist.iterrows():
                prices.append({
                    'date': index.strftime('%Y-%m-%d'),
                    'timestamp': int(index.timestamp()),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })

            return {
                'symbol': symbol,
                'period': period,
                'interval': interval,
                'prices': prices,
                'count': len(prices)
            }

        except Exception as e:
            raise ServiceError(f"Failed to fetch price data: {e}")

    async def get_current_price(self, symbol: str) -> float:
        """
        Get the current/latest price for a stock.

        Args:
            symbol: Yahoo Finance symbol

        Returns:
            Current price as float

        Raises:
            ServiceError: If fetch fails
        """
        symbol = self._validate_symbol(symbol)
        symbol = self._ensure_suffix(symbol)

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            price = await loop.run_in_executor(
                None, self._get_current_price_sync, symbol
            )
            return price

        except Exception as e:
            raise ServiceError(f"Failed to get current price for {symbol}: {e}")

    def _get_current_price_sync(self, symbol: str) -> float:
        """
        Synchronous fetch of current price.

        Args:
            symbol: Yahoo Finance symbol

        Returns:
            Current price
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')

            if hist.empty:
                raise ServiceError(f"No data found for {symbol}")

            return float(hist['Close'].iloc[-1])

        except Exception as e:
            raise ServiceError(f"Failed to get current price: {e}")

    async def search_symbols(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for stock symbols by company name or symbol.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching stocks
        """
        if not query or len(query) < 2:
            return []

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            results = await loop.run_in_executor(
                None, self._search_symbols_sync, query, limit
            )
            return results

        except Exception as e:
            self.logger.error(f"Search failed for '{query}': {e}")
            return []

    def _search_symbols_sync(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Synchronous symbol search using yfinance.

        Note: yfinance doesn't have a native search API, so we try to
        construct NSE/BSE symbols and validate them.

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of matching symbols
        """
        results = []
        query_upper = query.upper()

        # For Indian stocks, try both NSE and BSE
        symbols_to_try = [
            f"{query_upper}.NS",  # NSE
            f"{query_upper}.BO",  # BSE
        ]

        for symbol in symbols_to_try:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                # Check if valid (has basic data)
                if info.get('longName') or info.get('shortName'):
                    results.append({
                        'symbol': symbol,
                        'name': info.get('longName', info.get('shortName', symbol)),
                        'type': 'NSE' if '.NS' in symbol else 'BSE',
                        'sector': info.get('sector', None),
                        'industry': info.get('industry', None),
                        'market_cap': info.get('marketCap', None)
                    })

                if len(results) >= limit:
                    break

            except Exception:
                # Symbol doesn't exist, skip
                continue

        return results

    async def get_technicals(self, symbol: str, period: str = '1y') -> Dict[str, Any]:
        """
        Get technical indicators for a stock.

        Calculates:
        - Moving averages (SMA 20, 50, 200)
        - Relative Strength Index (RSI)
        - Price momentum

        Args:
            symbol: Yahoo Finance symbol
            period: Period for calculation

        Returns:
            Dictionary with technical indicators
        """
        symbol = self._validate_symbol(symbol)
        symbol = self._ensure_suffix(symbol)

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            result = await loop.run_in_executor(
                None, self._get_technicals_sync, symbol, period
            )
            return result

        except Exception as e:
            return self._handle_error(e, f"Failed to get technicals for {symbol}")

    def _get_technicals_sync(self, symbol: str, period: str) -> Dict[str, Any]:
        """
        Synchronous calculation of technical indicators.

        Args:
            symbol: Yahoo Finance symbol
            period: Time period

        Returns:
            Dictionary with technical indicators
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty or len(hist) < 200:
                raise ServiceError(f"Insufficient data for technical analysis: {symbol}")

            close_prices = hist['Close']

            # Calculate moving averages
            sma_20 = close_prices.rolling(window=20).mean().iloc[-1]
            sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
            sma_200 = close_prices.rolling(window=200).mean().iloc[-1]

            current_price = close_prices.iloc[-1]

            # Simple RSI calculation (14-day)
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]

            # Price momentum (% change over period)
            momentum = ((current_price - close_prices.iloc[0]) / close_prices.iloc[0]) * 100

            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                'sma_200': float(sma_200),
                'rsi_14': float(current_rsi),
                'momentum_percent': float(momentum),
                'trend': self._determine_trend(current_price, sma_20, sma_50, sma_200),
                'rsi_signal': self._rsi_signal(current_rsi)
            }

        except Exception as e:
            raise ServiceError(f"Failed to calculate technicals: {e}")

    def _determine_trend(
        self,
        price: float,
        sma_20: float,
        sma_50: float,
        sma_200: float
    ) -> str:
        """
        Determine price trend based on moving averages.

        Args:
            price: Current price
            sma_20: 20-day SMA
            sma_50: 50-day SMA
            sma_200: 200-day SMA

        Returns:
            Trend description
        """
        if price > sma_20 > sma_50 > sma_200:
            return 'strong_uptrend'
        elif price > sma_50 > sma_200:
            return 'uptrend'
        elif price < sma_20 < sma_50 < sma_200:
            return 'strong_downtrend'
        elif price < sma_50 < sma_200:
            return 'downtrend'
        else:
            return 'sideways'

    def _rsi_signal(self, rsi: float) -> str:
        """
        Determine RSI signal.

        Args:
            rsi: RSI value

        Returns:
            Signal description
        """
        if rsi > 70:
            return 'overbought'
        elif rsi < 30:
            return 'oversold'
        else:
            return 'neutral'

    def _ensure_suffix(self, symbol: str) -> str:
        """
        Ensure symbol has .NS or .BO suffix for Indian stocks.

        Args:
            symbol: Raw symbol

        Returns:
            Symbol with suffix
        """
        # If already has suffix, return as is
        if '.NS' in symbol or '.BO' in symbol or '.NSE' in symbol or '.BSE' in symbol:
            return symbol

        # Default to NSE (.NS)
        return f"{symbol}.NS"
