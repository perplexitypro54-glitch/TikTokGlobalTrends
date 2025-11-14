"""
Sound Model

Represents trending sounds/music on TikTok.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import (
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

from src.storage.models.base import Base
from src.storage.models.enums import NicheType, TrendDirection

# Association table between sounds and videos
sound_videos = Table(
    "sound_videos",
    Base.metadata,
    Column("sound_id", Integer, ForeignKey("sounds.id", ondelete="CASCADE"), primary_key=True),
    Column("video_id", Integer, ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True),
)


class Sound(Base):
    """Sound model for tracking audio trends."""

    __tablename__ = "sounds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tiktok_sound_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    artist: Mapped[str] = mapped_column(String(200), nullable=True)

    # Metrics
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    growth_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    viral_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Classification
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id", ondelete="CASCADE"))
    niche: Mapped[NicheType] = mapped_column(Enum(NicheType), nullable=False)

    # Ranking
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    trend_direction: Mapped[TrendDirection] = mapped_column(
        Enum(TrendDirection), default=TrendDirection.STABLE, nullable=False
    )

    # Timestamps
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    country: Mapped["Country"] = relationship("Country", back_populates="sounds")
    videos: Mapped[List["Video"]] = relationship(
        "Video", secondary=sound_videos, back_populates="sounds"
    )
    trends: Mapped[List["Trend"]] = relationship(
        "Trend", secondary="trend_sounds", back_populates="sounds"
    )

    __table_args__ = (
        Index("idx_sound_tiktok_country", "tiktok_sound_id", "country_id", unique=True),
        Index("idx_sound_country_rank", "country_id", "rank"),
        Index("idx_sound_growth_rate", "growth_rate"),
    )

    def __repr__(self) -> str:
        return f"<Sound(name={self.name}, rank={self.rank}, country_id={self.country_id})>"
