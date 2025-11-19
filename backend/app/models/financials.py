"""
Financial data models for annual and quarterly financials.
Stores 10-year historical data from Screener.in.
"""

from datetime import datetime, date
from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, Index, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.database import Base


class FinancialsAnnual(Base):
    """
    Annual financial data for a company.
    Stores fundamental metrics for 10 years.

    Source: Screener.in

    Attributes:
        id: Unique identifier
        company_id: Reference to Company
        fiscal_year: Fiscal year (e.g., 2023)
        revenue: Total revenue/sales (in Cr)
        profit: Net profit (in Cr)
        roce: Return on Capital Employed (%)
        roe: Return on Equity (%)
        debt_equity: Debt to Equity ratio
        current_ratio: Current assets / Current liabilities
        eps: Earnings Per Share
        book_value: Book value per share
        dividend_yield: Dividend yield (%)
        cash_flow_operating: Operating cash flow (in Cr)
        cash_flow_investing: Investing cash flow (in Cr)
        cash_flow_financing: Financing cash flow (in Cr)
        raw_data: Complete JSON dump from Screener.in
    """

    __tablename__ = "financials_annual"

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

    fiscal_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Fiscal year (e.g., 2023)",
    )

    # Income Statement
    revenue: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Revenue in Crores",
    )

    profit: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Net Profit in Crores",
    )

    # Profitability Metrics
    roce: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Return on Capital Employed (%)",
    )

    roe: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Return on Equity (%)",
    )

    # Leverage
    debt_equity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Debt to Equity ratio",
    )

    current_ratio: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Current Ratio",
    )

    # Per Share Metrics
    eps: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Earnings Per Share",
    )

    book_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Book Value Per Share",
    )

    dividend_yield: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Dividend Yield (%)",
    )

    # Cash Flow Statement
    cash_flow_operating: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Operating Cash Flow in Crores",
    )

    cash_flow_investing: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Investing Cash Flow in Crores",
    )

    cash_flow_financing: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Financing Cash Flow in Crores",
    )

    # Raw data from Screener.in (for flexibility)
    raw_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Complete JSON from Screener.in",
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

    # Relationship
    # company: Mapped["Company"] = relationship(back_populates="financials")

    # Composite unique constraint: one record per company per year
    __table_args__ = (
        Index("ix_financials_company_year", "company_id", "fiscal_year", unique=True),
        Index("ix_financials_year", "fiscal_year"),
    )

    def __repr__(self) -> str:
        return f"<FinancialsAnnual(company_id={self.company_id}, year={self.fiscal_year})>"


class FinancialsQuarterly(Base):
    """
    Quarterly financial data (optional, for future use).
    Similar structure to FinancialsAnnual but with quarter info.
    """

    __tablename__ = "financials_quarterly"

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

    quarter_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Quarter ending date (e.g., 2023-12-31)",
    )

    revenue: Mapped[float | None] = mapped_column(Float, nullable=True)
    profit: Mapped[float | None] = mapped_column(Float, nullable=True)
    eps: Mapped[float | None] = mapped_column(Float, nullable=True)

    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_financials_quarterly_company_date", "company_id", "quarter_date", unique=True),
    )

    def __repr__(self) -> str:
        return f"<FinancialsQuarterly(company_id={self.company_id}, quarter={self.quarter_date})>"
