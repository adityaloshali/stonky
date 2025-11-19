"""
Base service class for all data services.

Provides common functionality for error handling, logging, and caching.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger
import asyncio
from functools import wraps


class ServiceError(Exception):
    """Base exception for service errors."""
    pass


class ServiceTimeoutError(ServiceError):
    """Raised when service operation times out."""
    pass


class ServiceUnavailableError(ServiceError):
    """Raised when external service is unavailable."""
    pass


class BaseService(ABC):
    """
    Abstract base class for all data services.

    Provides:
    - Consistent error handling
    - Logging
    - Timeout management
    - Common utilities
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize base service.

        Args:
            timeout: Default timeout for operations in seconds
        """
        self.timeout = timeout
        self.logger = logger.bind(service=self.__class__.__name__)

    @abstractmethod
    async def fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch data for a given symbol.

        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')

        Returns:
            Dictionary containing the fetched data

        Raises:
            ServiceError: If data fetch fails
        """
        pass

    def _handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Consistent error handling across services.

        Args:
            error: The exception that occurred
            context: Additional context about the error

        Returns:
            Error response dictionary
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_msg, exc_info=error)

        return {
            "status": "error",
            "message": error_msg,
            "error_type": type(error).__name__
        }

    def _validate_symbol(self, symbol: str) -> str:
        """
        Validate and normalize stock symbol.

        Args:
            symbol: Raw stock symbol

        Returns:
            Normalized symbol

        Raises:
            ValueError: If symbol is invalid
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")

        # Remove whitespace and convert to uppercase
        symbol = symbol.strip().upper()

        if len(symbol) < 1 or len(symbol) > 20:
            raise ValueError("Symbol length must be between 1 and 20 characters")

        return symbol

    async def _with_timeout(self, coro, timeout: Optional[int] = None):
        """
        Execute a coroutine with timeout.

        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds (uses self.timeout if not provided)

        Returns:
            Result of the coroutine

        Raises:
            ServiceTimeoutError: If operation times out
        """
        timeout = timeout or self.timeout
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise ServiceTimeoutError(f"Operation timed out after {timeout} seconds")

    def _extract_error_message(self, response) -> str:
        """
        Extract error message from HTTP response.

        Args:
            response: HTTP response object

        Returns:
            Error message string
        """
        try:
            if hasattr(response, 'json'):
                data = response.json()
                return data.get('message', data.get('error', 'Unknown error'))
            return f"HTTP {response.status_code}"
        except Exception:
            return f"HTTP {response.status_code}"
