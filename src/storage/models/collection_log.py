"""
Collection Log Model

Tracks data collection executions from TikTok API and scrapers.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Enum as SQLEnum, Float, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.storage.models.base import Base, TimestampMixin
from src.storage.models.enums import CountryCode, DataSourceType


class CollectionStatus(str, Enum):
    """Status of a data collection execution."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    CANCELLED = "CANCELLED"


class CollectionLog(Base, TimestampMixin):
    """Collection log model for tracking data collection executions."""

    __tablename__ = "collection_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    country_code: Mapped[Optional[CountryCode]] = mapped_column(
        SQLEnum(CountryCode), nullable=True, index=True
    )
    data_source: Mapped[DataSourceType] = mapped_column(
        SQLEnum(DataSourceType), nullable=False, index=True
    )
    status: Mapped[CollectionStatus] = mapped_column(
        String(50), default=CollectionStatus.PENDING, nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    items_collected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    api_calls_made: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rate_limit_hit: Mapped[bool] = mapped_column(default=False, nullable=False)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_collection_country", "country_code"),
        Index("idx_collection_source", "data_source"),
        Index("idx_collection_status", "status"),
        Index("idx_collection_started", "started_at"),
        Index("idx_collection_completed", "completed_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<CollectionLog(id={self.id}, country={self.country_code}, "
            f"source={self.data_source}, status={self.status})>"
        )
