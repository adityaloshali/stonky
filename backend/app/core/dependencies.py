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

    # Service creators will be added as we build them
    # Example:
    # def create_screener_service(self) -> ScreenerService:
    #     return ScreenerService(self.config.SCREENER_COOKIE)


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
