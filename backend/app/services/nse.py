"""
NSE (National Stock Exchange) service for shareholding and live data.

NSE provides official data on:
- Shareholding patterns (Promoter, FII, DII, Public)
- Live quotes and prices
- Corporate filings
- Historical data

Note: NSE requires session cookies. This service automatically handles
session initialization by visiting the homepage first.
"""

from typing import Dict, Any, Optional, List
import requests
from datetime import datetime
from loguru import logger

from app.services.base import BaseService, ServiceError, ServiceUnavailableError


class NSEService(BaseService):
    """
    Service for fetching data from NSE India.

    NSE API requires:
    1. Valid cookies (obtained by visiting homepage)
    2. Proper headers (User-Agent, Referer)
    3. Session management
    """

    BASE_URL = "https://www.nseindia.com"
    API_BASE = f"{BASE_URL}/api"

    def __init__(self, timeout: int = 30):
        """
        Initialize NSE service.

        Args:
            timeout: Request timeout in seconds
        """
        super().__init__(timeout=timeout)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        # Session for maintaining cookies
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._session_initialized = False

    async def fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch comprehensive data for a stock from NSE.

        Args:
            symbol: NSE symbol (without .NS suffix, e.g., 'RELIANCE')

        Returns:
            Dictionary with shareholding, quote, and other data

        Raises:
            ServiceError: If fetch fails
        """
        symbol = self._validate_symbol(symbol)

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            # Ensure session is initialized
            if not self._session_initialized:
                await loop.run_in_executor(None, self._init_session)

            # Fetch all data in parallel (using executor for sync requests)
            shareholding_task = loop.run_in_executor(None, self._get_shareholding_sync, symbol)
            quote_task = loop.run_in_executor(None, self._get_quote_sync, symbol)

            shareholding, quote = await asyncio.gather(
                shareholding_task, quote_task, return_exceptions=True
            )

            # Handle errors
            if isinstance(shareholding, Exception):
                self.logger.warning(f"Shareholding fetch failed: {shareholding}")
                shareholding = {}

            if isinstance(quote, Exception):
                self.logger.warning(f"Quote fetch failed: {quote}")
                quote = {}

            return {
                'symbol': symbol,
                'shareholding': shareholding,
                'quote': quote,
                'source': 'nse',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return self._handle_error(e, f"Failed to fetch NSE data for {symbol}")

    def _init_session(self) -> None:
        """
        Initialize NSE session by visiting homepage to get cookies.

        NSE requires cookies that are only set when you visit the homepage.
        """
        try:
            self.logger.info("Initializing NSE session...")
            response = self.session.get(
                self.BASE_URL,
                timeout=self.timeout
            )

            if response.status_code == 200:
                self._session_initialized = True
                self.logger.info("NSE session initialized successfully")
            else:
                raise ServiceError(f"Failed to initialize NSE session: {response.status_code}")

        except requests.RequestException as e:
            raise ServiceUnavailableError(f"NSE is unreachable: {e}")

    async def get_shareholding(self, symbol: str) -> Dict[str, Any]:
        """
        Get detailed shareholding pattern for a stock.

        Returns:
        - Promoter holding percentage
        - FII (Foreign Institutional Investors) holding
        - DII (Domestic Institutional Investors) holding
        - Public holding
        - Promoter pledging information

        Args:
            symbol: NSE symbol

        Returns:
            Dictionary with shareholding data
        """
        symbol = self._validate_symbol(symbol)

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            if not self._session_initialized:
                await loop.run_in_executor(None, self._init_session)

            result = await loop.run_in_executor(None, self._get_shareholding_sync, symbol)
            return result

        except Exception as e:
            return self._handle_error(e, f"Failed to get shareholding for {symbol}")

    def _get_shareholding_sync(self, symbol: str) -> Dict[str, Any]:
        """
        Synchronous fetch of shareholding data.

        Args:
            symbol: NSE symbol

        Returns:
            Dictionary with shareholding information
        """
        # NSE shareholding API endpoint
        url = f"{self.API_BASE}/quote-equity"
        params = {'symbol': symbol}

        # Update referer for this specific request
        headers = self.session.headers.copy()
        headers['Referer'] = f"{self.BASE_URL}/get-quotes/equity?symbol={symbol}"

        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )

            # Handle session expiry
            if response.status_code == 401:
                self.logger.warning("NSE session expired, reinitializing...")
                self._session_initialized = False
                self._init_session()
                # Retry once
                response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)

            if response.status_code == 404:
                raise ServiceError(f"Symbol '{symbol}' not found on NSE")

            if response.status_code != 200:
                raise ServiceError(f"NSE API returned status {response.status_code}")

            data = response.json()

            # Extract shareholding pattern
            shareholding = self._parse_shareholding(data)

            return shareholding

        except requests.Timeout:
            raise ServiceError(f"Timeout fetching shareholding for {symbol}")
        except requests.RequestException as e:
            raise ServiceUnavailableError(f"Network error: {e}")
        except ValueError as e:
            raise ServiceError(f"Invalid JSON response: {e}")

    def _parse_shareholding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse NSE API response to extract shareholding information.

        Args:
            data: Raw API response

        Returns:
            Parsed shareholding data
        """
        result = {}

        # Security-wise delivery positions
        security_wise = data.get('securityWiseDP', {})

        # Shareholding patterns (array of quarterly data)
        patterns = security_wise.get('shareholdingPatterns', [])

        if patterns:
            # Get the latest quarter (first item)
            latest = patterns[0] if isinstance(patterns, list) else patterns

            result['promoter'] = {
                'percentage': latest.get('promoterAndPromoterGroup', 0),
                'shares': latest.get('promoterAndPromoterGroupShares', 0)
            }

            result['fii'] = {
                'percentage': latest.get('fii', 0),
                'shares': latest.get('fiiShares', 0)
            }

            result['dii'] = {
                'percentage': latest.get('dii', 0),
                'shares': latest.get('diiShares', 0)
            }

            result['public'] = {
                'percentage': latest.get('public', 0),
                'shares': latest.get('publicShares', 0)
            }

            result['date'] = latest.get('date', None)

        # Promoter pledging/encumbrance
        encumbrance = security_wise.get('promoterEncumbrance', {})
        if encumbrance:
            result['pledging'] = {
                'promoter_pledged_percentage': encumbrance.get('promoterPledgePercentage', 0),
                'promoter_pledged_shares': encumbrance.get('promoterPledgeShares', 0)
            }

        return result

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get live quote for a stock.

        Args:
            symbol: NSE symbol

        Returns:
            Dictionary with price, volume, and other quote data
        """
        symbol = self._validate_symbol(symbol)

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            if not self._session_initialized:
                await loop.run_in_executor(None, self._init_session)

            result = await loop.run_in_executor(None, self._get_quote_sync, symbol)
            return result

        except Exception as e:
            return self._handle_error(e, f"Failed to get quote for {symbol}")

    def _get_quote_sync(self, symbol: str) -> Dict[str, Any]:
        """
        Synchronous fetch of live quote.

        Args:
            symbol: NSE symbol

        Returns:
            Dictionary with quote information
        """
        url = f"{self.API_BASE}/quote-equity"
        params = {'symbol': symbol}

        headers = self.session.headers.copy()
        headers['Referer'] = f"{self.BASE_URL}/get-quotes/equity?symbol={symbol}"

        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 401:
                self._session_initialized = False
                self._init_session()
                response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)

            if response.status_code != 200:
                raise ServiceError(f"NSE API returned status {response.status_code}")

            data = response.json()

            # Extract price information
            price_info = data.get('priceInfo', {})

            return {
                'last_price': price_info.get('lastPrice', 0),
                'change': price_info.get('change', 0),
                'percent_change': price_info.get('pChange', 0),
                'previous_close': price_info.get('previousClose', 0),
                'open': price_info.get('open', 0),
                'close': price_info.get('close', 0),
                'day_high': price_info.get('intraDayHighLow', {}).get('max', 0),
                'day_low': price_info.get('intraDayHighLow', {}).get('min', 0),
                'week_52_high': price_info.get('weekHighLow', {}).get('max', 0),
                'week_52_low': price_info.get('weekHighLow', {}).get('min', 0),
                'volume': data.get('preOpenMarket', {}).get('totalTradedVolume', 0),
                'timestamp': datetime.now().isoformat()
            }

        except requests.Timeout:
            raise ServiceError(f"Timeout fetching quote for {symbol}")
        except requests.RequestException as e:
            raise ServiceUnavailableError(f"Network error: {e}")
        except ValueError as e:
            raise ServiceError(f"Invalid JSON response: {e}")

    async def search_symbol(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for stocks by name or symbol.

        Args:
            query: Search query (company name or symbol)

        Returns:
            List of matching stocks
        """
        if not query or len(query) < 2:
            return []

        try:
            import asyncio
            loop = asyncio.get_event_loop()

            if not self._session_initialized:
                await loop.run_in_executor(None, self._init_session)

            result = await loop.run_in_executor(None, self._search_symbol_sync, query)
            return result

        except Exception as e:
            self.logger.error(f"Search failed for '{query}': {e}")
            return []

    def _search_symbol_sync(self, query: str) -> List[Dict[str, Any]]:
        """
        Synchronous symbol search.

        Args:
            query: Search query

        Returns:
            List of matching symbols
        """
        url = f"{self.API_BASE}/search/autocomplete"
        params = {'q': query}

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )

            if response.status_code != 200:
                return []

            data = response.json()
            symbols = data.get('symbols', [])

            # Format results
            results = []
            for item in symbols:
                results.append({
                    'symbol': item.get('symbol', ''),
                    'name': item.get('symbol_info', ''),
                    'series': item.get('series', ''),
                    'type': 'NSE'
                })

            return results

        except Exception as e:
            self.logger.error(f"Error in symbol search: {e}")
            return []
