"""
Screener.in service for fetching 10-year fundamental data.

This service scrapes Screener.in's export functionality to get comprehensive
10-year financial data including ROCE, ROE, Debt/Equity, Revenue, Profit, etc.

Authentication: Requires a valid session cookie (sessionid).
To get the cookie:
1. Login to Screener.in in your browser
2. Open DevTools -> Application -> Cookies
3. Copy the 'sessionid' value
4. Set SCREENER_COOKIE in .env file
"""

from typing import Dict, Any, Optional
import pandas as pd
import requests
from io import BytesIO
from loguru import logger

from app.services.base import BaseService, ServiceError, ServiceUnavailableError


class ScreenerService(BaseService):
    """
    Service for fetching fundamental data from Screener.in.

    Uses the Excel export endpoint to get 10 years of consolidated financial data.
    """

    BASE_URL = "https://www.screener.in"

    def __init__(self, session_cookie: str, timeout: int = 30):
        """
        Initialize Screener service.

        Args:
            session_cookie: Screener.in session cookie (from browser)
            timeout: Request timeout in seconds
        """
        super().__init__(timeout=timeout)
        self.session_cookie = session_cookie

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/120.0.0.0 Safari/537.36',
            'Referer': f'{self.BASE_URL}/',
            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        self.cookies = {'sessionid': session_cookie}

    async def fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch 10-year fundamental data for a stock.

        Args:
            symbol: NSE symbol (e.g., 'RELIANCE', 'TCS')

        Returns:
            Dictionary with financial metrics over 10 years

        Raises:
            ServiceError: If fetch fails
        """
        symbol = self._validate_symbol(symbol)
        self.logger.info(f"Fetching fundamentals for {symbol}")

        try:
            # Use asyncio to run synchronous requests in executor
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._fetch_fundamentals_sync, symbol
            )
            return result

        except ServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Error fetching Screener data for {symbol}: {e}")
            raise ServiceError(f"Failed to fetch data from Screener.in: {e}")

    def _fetch_fundamentals_sync(self, symbol: str) -> Dict[str, Any]:
        """
        Synchronous fetch of fundamentals (runs in executor).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with parsed financial data
        """
        # Construct the Excel export URL
        # Screener.in Excel export endpoint: /api/company/{SYMBOL}/export/
        export_url = f"{self.BASE_URL}/api/company/{symbol}/export/"

        try:
            # First, check if company exists
            company_url = f"{self.BASE_URL}/company/{symbol}/consolidated/"
            check_response = requests.get(
                company_url,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout,
                allow_redirects=True
            )

            if check_response.status_code == 404:
                raise ServiceError(f"Company '{symbol}' not found on Screener.in")

            if check_response.status_code == 403:
                raise ServiceError(
                    "Screener.in session expired. Please update SCREENER_COOKIE"
                )

            # Now fetch the Excel export
            response = requests.get(
                export_url,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout
            )

            if response.status_code == 403:
                raise ServiceError(
                    "Screener.in session expired or invalid. "
                    "Please update SCREENER_COOKIE in .env"
                )

            if response.status_code == 404:
                raise ServiceError(f"No consolidated data found for {symbol}")

            if response.status_code != 200:
                raise ServiceUnavailableError(
                    f"Screener.in returned status {response.status_code}"
                )

            # Check if response is actually Excel (not HTML error page)
            content_type = response.headers.get('Content-Type', '')
            if 'spreadsheet' not in content_type and 'excel' not in content_type:
                raise ServiceError(
                    "Invalid response from Screener.in. "
                    "Cookie may be expired or symbol invalid."
                )

            # Parse Excel data
            data = self._parse_excel(response.content, symbol)

            self.logger.info(f"Successfully fetched data for {symbol}")
            return data

        except ServiceError:
            raise
        except requests.Timeout:
            raise ServiceError(f"Timeout while fetching data for {symbol}")
        except requests.RequestException as e:
            raise ServiceUnavailableError(f"Network error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error parsing Screener data: {e}")
            raise ServiceError(f"Failed to parse Screener data: {e}")

    def _parse_excel(self, content: bytes, symbol: str) -> Dict[str, Any]:
        """
        Parse Excel content from Screener.in export.

        The Excel file has two sheets:
        - 'Data Sheet': Contains all financial metrics
        - Structure: Metrics as rows, Years as columns

        Args:
            content: Raw Excel file bytes
            symbol: Stock symbol (for logging)

        Returns:
            Dictionary with parsed metrics
        """
        try:
            # Read Excel file
            excel_file = BytesIO(content)
            df = pd.read_excel(excel_file, sheet_name='Data Sheet', engine='openpyxl')

            # Screener format: First column is metric name, rest are years
            # Example:
            # Metric Name | Mar 2024 | Mar 2023 | Mar 2022 | ...
            # Sales       | 1000     | 900      | 850      | ...
            # ROCE        | 15.5     | 14.2     | 13.8     | ...

            # Set first column as index
            df.set_index(df.columns[0], inplace=True)

            # Extract key metrics
            metrics = {}

            # Revenue metrics
            metrics['revenue'] = self._extract_metric(df, ['Sales', 'Revenue'])
            metrics['expenses'] = self._extract_metric(df, ['Expenses', 'Operating Expenses'])
            metrics['operating_profit'] = self._extract_metric(
                df, ['Operating Profit', 'EBIT', 'OPM']
            )
            metrics['net_profit'] = self._extract_metric(df, ['Net Profit', 'Profit'])

            # Quality metrics
            metrics['roce'] = self._extract_metric(df, ['ROCE %', 'ROCE'])
            metrics['roe'] = self._extract_metric(df, ['ROE %', 'ROE'])

            # Debt metrics
            metrics['debt'] = self._extract_metric(df, ['Debt', 'Borrowings'])
            metrics['debt_to_equity'] = self._extract_metric(
                df, ['Debt to equity', 'D/E', 'Debt/Equity']
            )

            # Asset metrics
            metrics['assets'] = self._extract_metric(df, ['Total Assets', 'Assets'])
            metrics['equity'] = self._extract_metric(df, ['Equity', 'Shareholders Equity'])

            # Per share metrics
            metrics['eps'] = self._extract_metric(df, ['EPS in Rs', 'EPS'])
            metrics['book_value'] = self._extract_metric(
                df, ['Book Value', 'BVPS', 'Book Value Per Share']
            )

            # Valuation metrics
            metrics['pe_ratio'] = self._extract_metric(df, ['PE Ratio', 'P/E', 'Stock P/E'])
            metrics['market_cap'] = self._extract_metric(df, ['Market Cap', 'Market Capitalization'])

            # Get years (column names)
            years = [col for col in df.columns if col != df.index.name]
            metrics['years'] = years

            # Metadata
            metrics['symbol'] = symbol
            metrics['source'] = 'screener.in'
            metrics['data_type'] = 'consolidated'

            return metrics

        except Exception as e:
            self.logger.error(f"Error parsing Excel for {symbol}: {e}")
            raise ServiceError(f"Failed to parse Excel data: {e}")

    def _extract_metric(self, df: pd.DataFrame, possible_names: list) -> list:
        """
        Extract a metric from dataframe with multiple possible row names.

        Args:
            df: DataFrame with metrics as index
            possible_names: List of possible metric names to search for

        Returns:
            List of values across years, or empty list if not found
        """
        for name in possible_names:
            # Try exact match
            if name in df.index:
                values = df.loc[name].tolist()
                # Convert to float, handle NaN
                return [float(v) if pd.notna(v) else None for v in values]

            # Try case-insensitive partial match
            matching = [idx for idx in df.index if name.lower() in str(idx).lower()]
            if matching:
                values = df.loc[matching[0]].tolist()
                return [float(v) if pd.notna(v) else None for v in values]

        # Not found
        self.logger.warning(f"Metric not found in data: {possible_names}")
        return []

    async def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get basic company information (name, sector, etc.).

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with company info
        """
        symbol = self._validate_symbol(symbol)

        try:
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._get_company_info_sync, symbol
            )
            return result

        except Exception as e:
            return self._handle_error(e, f"Failed to get company info for {symbol}")

    def _get_company_info_sync(self, symbol: str) -> Dict[str, Any]:
        """
        Synchronous fetch of company info.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with company information
        """
        url = f"{self.BASE_URL}/company/{symbol}/consolidated/"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout
            )

            if response.status_code != 200:
                raise ServiceError(f"Failed to fetch company info: {response.status_code}")

            # Parse HTML to extract basic info
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract company name
            name_elem = soup.find('h1')
            name = name_elem.text.strip() if name_elem else symbol

            # Extract sector (usually in a specific div)
            sector_elem = soup.find('a', {'class': 'sub'})
            sector = sector_elem.text.strip() if sector_elem else None

            return {
                'symbol': symbol,
                'name': name,
                'sector': sector,
                'source': 'screener.in'
            }

        except Exception as e:
            raise ServiceError(f"Failed to parse company info: {e}")
