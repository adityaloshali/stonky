"""
Base repository pattern for database operations.
Provides generic CRUD operations for all models.
"""

from typing import Generic, TypeVar, Type, Any, Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

# Type variable for model classes
ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic repository providing CRUD operations for any SQLAlchemy model.

    Usage:
        class CompanyRepository(BaseRepository[Company]):
            def __init__(self, db: AsyncSession):
                super().__init__(Company, db)

            async def get_by_symbol(self, symbol: str) -> Company | None:
                result = await self.db.execute(
                    select(Company).where(Company.symbol == symbol)
                )
                return result.scalar_one_or_none()
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    async def get(self, id: Any) -> ModelType | None:
        """
        Get a single record by ID.

        Args:
            id: Primary key value

        Returns:
            Model instance or None if not found
        """
        return await self.db.get(self.model, id)

    async def get_by(self, **filters) -> ModelType | None:
        """
        Get a single record by filters.

        Args:
            **filters: Column=value pairs

        Returns:
            Model instance or None if not found
        """
        query = select(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_many(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> Sequence[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Column=value pairs

        Returns:
            List of model instances
        """
        query = select(self.model)

        # Apply filters
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, **data) -> ModelType:
        """
        Create a new record.

        Args:
            **data: Model fields

        Returns:
            Created model instance
        """
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)

        logger.debug(f"Created {self.model.__name__}: {instance}")
        return instance

    async def update(self, id: Any, **data) -> ModelType | None:
        """
        Update a record by ID.

        Args:
            id: Primary key value
            **data: Fields to update

        Returns:
            Updated model instance or None if not found
        """
        instance = await self.get(id)
        if not instance:
            return None

        for key, value in data.items():
            setattr(instance, key, value)

        await self.db.flush()
        await self.db.refresh(instance)

        logger.debug(f"Updated {self.model.__name__} {id}: {data}")
        return instance

    async def delete(self, id: Any) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Primary key value

        Returns:
            True if deleted, False if not found
        """
        instance = await self.get(id)
        if not instance:
            return False

        await self.db.delete(instance)
        await self.db.flush()

        logger.debug(f"Deleted {self.model.__name__} {id}")
        return True

    async def exists(self, **filters) -> bool:
        """
        Check if a record exists matching filters.

        Args:
            **filters: Column=value pairs

        Returns:
            True if exists, False otherwise
        """
        query = select(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)

        result = await self.db.execute(query.limit(1))
        return result.scalar_one_or_none() is not None

    async def count(self, **filters) -> int:
        """
        Count records matching filters.

        Args:
            **filters: Column=value pairs

        Returns:
            Number of matching records
        """
        from sqlalchemy import func

        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)

        result = await self.db.execute(query)
        return result.scalar_one()
