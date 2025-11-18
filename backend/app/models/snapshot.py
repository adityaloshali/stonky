"""
Snapshot model - Versioned analysis cache.
Stores complete analysis results with provenance.
"""

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.database import Base


class Snapshot(Base):
    """
    Versioned snapshot of company analysis.

    Stores complete analysis results including:
    - HQSF score
    - All engine results (Growth, Quality, Risk, Valuation, Ownership)
    - AI-generated context
    - Data provenance (sources and timestamps)

    Attributes:
        id: Unique identifier
        company_id: Reference to Company
        kind: Type of snapshot (e.g., "full_analysis", "fundamentals", "technical")
        version: Snapshot version (e.g., "v2.0")
        data: Complete analysis results (JSON)
        sources: Data provenance - which APIs/services were used with timestamps
        created_at: When this snapshot was generated
    """

    __tablename__ = "snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    kind: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Snapshot type: full_analysis, fundamentals, technical, news",
    )

    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="v2.0",
        comment="Analysis version for tracking changes",
    )

    data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Complete analysis results",
    )

    sources: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Data provenance: APIs used, timestamps, versions",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    # Indexes for efficient queries
    __table_args__ = (
        Index("ix_snapshots_company_kind", "company_id", "kind"),
        Index("ix_snapshots_company_created", "company_id", "created_at"),
        Index("ix_snapshots_kind_created", "kind", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Snapshot(company_id={self.company_id}, kind={self.kind}, created={self.created_at})>"

    @property
    def is_stale(self, max_age_hours: int = 24) -> bool:
        """
        Check if snapshot is stale (older than max_age_hours).

        Args:
            max_age_hours: Maximum age in hours before considering stale

        Returns:
            True if snapshot is older than max_age_hours
        """
        age = datetime.utcnow() - self.created_at
        return age.total_seconds() > (max_age_hours * 3600)
