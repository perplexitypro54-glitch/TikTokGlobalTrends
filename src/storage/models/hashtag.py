"""
Hashtag Model

Represents trending hashtags on TikTok.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.models.base import Base
from src.storage.models.enums import DataSourceType, NicheType, TrendDirection


class Hashtag(Base):
    """Hashtag model for tracking trending tags."""

    __tablename__ = "hashtags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id", ondelete="CASCADE"))
    niche: Mapped[NicheType] = mapped_column(Enum(NicheType), nullable=False)

    # Metrics
    posts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    views_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    growth_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    viral_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trend_direction: Mapped[TrendDirection] = mapped_column(
        Enum(TrendDirection), default=TrendDirection.STABLE, nullable=False
    )

    # Ranking
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Data collection
    data_source: Mapped[DataSourceType] = mapped_column(Enum(DataSourceType), nullable=False)

    # Timestamps
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    country: Mapped["Country"] = relationship("Country", back_populates="hashtags")
    videos: Mapped[List["Video"]] = relationship(
        "Video", secondary="video_hashtags", back_populates="hashtags"
    )
    trends: Mapped[List["Trend"]] = relationship("Trend", back_populates="hashtag")

    __table_args__ = (
        Index("idx_hashtag_name_country", "name", "country_id", unique=True),
        Index("idx_hashtag_country_niche", "country_id", "niche"),
        Index("idx_hashtag_rank_country", "rank", "country_id"),
    )

    def __repr__(self) -> str:
        return f"<Hashtag(name={self.name}, rank={self.rank}, country_id={self.country_id})>"
