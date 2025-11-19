"""
Company model - Core entity for stock analysis.
"""

from datetime import datetime
from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class Company(Base):
    """
    Company entity representing a stock/security.

    Attributes:
        id: Unique identifier (UUID)
        symbol: Stock symbol (e.g., "RELIANCE.NS")
        isin: International Securities Identification Number
        name: Company name (e.g., "Reliance Industries Limited")
        sector: Sector classification (e.g., "Energy", "IT", "Banking")
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Stock symbol (e.g., RELIANCE.NS)",
    )

    isin: Mapped[str | None] = mapped_column(
        String(12),
        unique=True,
        nullable=True,
        index=True,
        comment="ISIN code (INE002A01018)",
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Company name",
    )

    sector: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Sector classification",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships (to be added as we build other models)
    # snapshots: Mapped[list["Snapshot"]] = relationship(back_populates="company")
    # financials: Mapped[list["FinancialsAnnual"]] = relationship(back_populates="company")
    # prices: Mapped[list["PriceOHLC"]] = relationship(back_populates="company")

    # Indexes
    __table_args__ = (
        Index("ix_companies_symbol_sector", "symbol", "sector"),
    )

    def __repr__(self) -> str:
        return f"<Company(symbol={self.symbol}, name={self.name})>"
