"""
Company repository with business-specific queries.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """
    Repository for Company model.
    Extends BaseRepository with company-specific queries.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Company, db)

    async def get_by_symbol(self, symbol: str) -> Company | None:
        """
        Get company by stock symbol.

        Args:
            symbol: Stock symbol (e.g., "RELIANCE.NS")

        Returns:
            Company instance or None
        """
        result = await self.db.execute(
            select(Company).where(Company.symbol == symbol)
        )
        return result.scalar_one_or_none()

    async def get_by_isin(self, isin: str) -> Company | None:
        """
        Get company by ISIN code.

        Args:
            isin: ISIN code (e.g., "INE002A01018")

        Returns:
            Company instance or None
        """
        result = await self.db.execute(
            select(Company).where(Company.isin == isin)
        )
        return result.scalar_one_or_none()

    async def get_by_sector(
        self,
        sector: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> list[Company]:
        """
        Get all companies in a sector.

        Args:
            sector: Sector name (e.g., "IT", "Banking")
            skip: Number to skip (pagination)
            limit: Max results

        Returns:
            List of companies
        """
        result = await self.db.execute(
            select(Company)
            .where(Company.sector == sector)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_name(
        self,
        query: str,
        *,
        limit: int = 10
    ) -> list[Company]:
        """
        Search companies by name (case-insensitive).

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of matching companies
        """
        result = await self.db.execute(
            select(Company)
            .where(Company.name.ilike(f"%{query}%"))
            .limit(limit)
        )
        return list(result.scalars().all())
