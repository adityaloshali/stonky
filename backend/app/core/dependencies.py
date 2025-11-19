"""
FastAPI dependency injection utilities.
Service factories and shared dependencies.
"""

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db


# Type alias for database session dependency
DBSession = Annotated[AsyncSession, Depends(get_db)]


class ServiceFactory:
    """
    Factory for creating service instances with proper dependency injection.
    Follows the Factory pattern for clean service instantiation.
    """

    def __init__(self, config: settings.__class__ = settings):
        """
        Initialize factory with configuration.

        Args:
            config: Application settings instance
        """
        self.config = config

    def create_screener_service(self):
        """
        Create Screener.in service instance.

        Returns:
            ScreenerService instance

        Raises:
            ValueError: If SCREENER_COOKIE is not configured
        """
        from app.services.screener import ScreenerService

        if not self.config.has_screener_cookie:
            raise ValueError(
                "SCREENER_COOKIE is not configured. "
                "Please set it in .env file. "
                "See backend/README.md for instructions."
            )

        return ScreenerService(
            session_cookie=self.config.SCREENER_COOKIE,
            timeout=30
        )

    def create_nse_service(self):
        """
        Create NSE service instance.

        Returns:
            NSEService instance
        """
        from app.services.nse import NSEService
        return NSEService(timeout=30)

    def create_yahoo_service(self):
        """
        Create Yahoo Finance service instance.

        Returns:
            YahooFinanceService instance
        """
        from app.services.yahoo import YahooFinanceService
        return YahooFinanceService(timeout=30)

    def create_news_service(self):
        """
        Create News service instance.

        Returns:
            NewsService instance
        """
        from app.services.news import NewsService
        return NewsService(timeout=30)

    def create_all_services(self) -> dict:
        """
        Create all services at once.

        Useful for endpoints that need multiple services.

        Returns:
            Dictionary with all service instances

        Note: Screener service will only be included if cookie is configured
        """
        services = {
            'nse': self.create_nse_service(),
            'yahoo': self.create_yahoo_service(),
            'news': self.create_news_service()
        }

        # Only add screener if cookie is configured
        if self.config.has_screener_cookie:
            services['screener'] = self.create_screener_service()

        return services


def get_service_factory() -> ServiceFactory:
    """
    FastAPI dependency to get service factory.

    Usage:
        @router.get("/analyze/{symbol}")
        async def analyze(
            symbol: str,
            factory: ServiceFactory = Depends(get_service_factory)
        ):
            screener = factory.create_screener_service()
            data = await screener.fetch_fundamentals(symbol)
    """
    return ServiceFactory()


# Type alias for service factory dependency
Factory = Annotated[ServiceFactory, Depends(get_service_factory)]
