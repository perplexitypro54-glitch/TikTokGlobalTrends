"""
Creator Model

Represents TikTok content creators.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.models.base import Base


class Creator(Base):
    """Creator model for tracking TikTok influencers."""

    __tablename__ = "creators"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tiktok_creator_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    profile_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    profile_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Stats
    followers: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False, index=True)
    follower_growth: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    videos_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    average_engagement: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Classification
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id", ondelete="CASCADE"))

    # Trending status
    is_trending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trending_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamps
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    country: Mapped["Country"] = relationship("Country", back_populates="creators")
    videos: Mapped[List["Video"]] = relationship(
        "Video", back_populates="creator", cascade="all, delete-orphan"
    )
    trends: Mapped[List["Trend"]] = relationship(
        "Trend", secondary="trend_creators", back_populates="creators"
    )

    __table_args__ = (
        Index("idx_creator_country_trending", "country_id", "is_trending"),
        Index("idx_creator_tiktok_id", "tiktok_creator_id"),
    )

    def __repr__(self) -> str:
        return f"<Creator(username={self.username}, followers={self.followers})>"
