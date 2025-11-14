"""
Video Model

Represents TikTok videos.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.models.base import Base, TimestampMixin

# Association table for many-to-many relationship between videos and hashtags
video_hashtags = Table(
    "video_hashtags",
    Base.metadata,
    Column("video_id", Integer, ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True),
    Column("hashtag_id", Integer, ForeignKey("hashtags.id", ondelete="CASCADE"), primary_key=True),
)


class Video(Base, TimestampMixin):
    """Video model for tracking TikTok content."""

    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tiktok_video_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Creator info
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("creators.id", ondelete="CASCADE"), index=True
    )

    # Content
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    # Metrics
    views: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    likes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    comments: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    shares: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    bookmarks: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    viral_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)

    # Classification
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id", ondelete="CASCADE"))

    # Content metadata
    music_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamps
    tiktok_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Relationships
    creator: Mapped["Creator"] = relationship("Creator", back_populates="videos")
    country: Mapped["Country"] = relationship("Country", back_populates="videos")
    hashtags: Mapped[List["Hashtag"]] = relationship(
        "Hashtag", secondary=video_hashtags, back_populates="videos"
    )
    sounds: Mapped[List["Sound"]] = relationship(
        "Sound", secondary="sound_videos", back_populates="videos"
    )

    __table_args__ = (
        Index("idx_video_creator", "creator_id"),
        Index("idx_video_country", "country_id"),
        Index("idx_video_tiktok_id", "tiktok_video_id"),
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.tiktok_video_id}, creator_id={self.creator_id})>"
