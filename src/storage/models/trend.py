"""
Trend Model

Represents identified trends combining hashtags, sounds, and creators.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.models.base import Base, TimestampMixin
from src.storage.models.enums import NicheType, SentimentType

# Association tables for many-to-many relationships
trend_hashtags = Table(
    "trend_hashtags",
    Base.metadata,
    Column("trend_id", Integer, ForeignKey("trends.id", ondelete="CASCADE"), primary_key=True),
    Column("hashtag_id", Integer, ForeignKey("hashtags.id", ondelete="CASCADE"), primary_key=True),
)

trend_sounds = Table(
    "trend_sounds",
    Base.metadata,
    Column("trend_id", Integer, ForeignKey("trends.id", ondelete="CASCADE"), primary_key=True),
    Column("sound_id", Integer, ForeignKey("sounds.id", ondelete="CASCADE"), primary_key=True),
)

trend_creators = Table(
    "trend_creators",
    Base.metadata,
    Column("trend_id", Integer, ForeignKey("trends.id", ondelete="CASCADE"), primary_key=True),
    Column("creator_id", Integer, ForeignKey("creators.id", ondelete="CASCADE"), primary_key=True),
)


class Trend(Base, TimestampMixin):
    """Trend model for tracking broader TikTok trends."""

    __tablename__ = "trends"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Classification
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id", ondelete="CASCADE"))
    niche: Mapped[NicheType] = mapped_column(Enum(NicheType), nullable=False)

    # Metrics
    viral_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    momentum: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sentiment: Mapped[SentimentType] = mapped_column(
        Enum(SentimentType), default=SentimentType.NEUTRAL, nullable=False
    )

    # Lifecycle
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, server_default=func.now()
    )
    peak_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    country: Mapped["Country"] = relationship("Country", back_populates="trends")
    hashtags: Mapped[List["Hashtag"]] = relationship(
        "Hashtag", secondary=trend_hashtags, back_populates="trends"
    )
    sounds: Mapped[List["Sound"]] = relationship(
        "Sound", secondary=trend_sounds, back_populates="trends"
    )
    creators: Mapped[List["Creator"]] = relationship(
        "Creator", secondary=trend_creators, back_populates="trends"
    )

    __table_args__ = (
        Index("idx_trend_country_active", "country_id", "is_active"),
        Index("idx_trend_viral_score", "viral_score"),
    )

    def __repr__(self) -> str:
        return f"<Trend(name={self.name}, is_active={self.is_active})>"
