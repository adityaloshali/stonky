"""
Price models for historical OHLC data.
"""

from datetime import datetime, date
from sqlalchemy import Float, ForeignKey, Index, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class PriceOHLC(Base):
    """
    Historical OHLC (Open, High, Low, Close) price data.

    Source: Yahoo Finance

    Attributes:
        id: Unique identifier
        company_id: Reference to Company
        date: Trading date
        open: Opening price
        high: High price of the day
        low: Low price of the day
        close: Closing price
        volume: Trading volume
        created_at: Timestamp of creation
    """

    __tablename__ = "prices_ohlc"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Trading date",
    )

    open: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Opening price",
    )

    high: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="High price",
    )

    low: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Low price",
    )

    close: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Closing price",
    )

    volume: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Trading volume",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Composite unique constraint: one price record per company per date
    # Index for efficient time-series queries
    __table_args__ = (
        Index("ix_prices_company_date", "company_id", "date", unique=True),
        Index("ix_prices_date", "date"),
    )

    def __repr__(self) -> str:
        return f"<PriceOHLC(company_id={self.company_id}, date={self.date}, close={self.close})>"
