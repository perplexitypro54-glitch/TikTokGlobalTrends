"""
Country Model

Represents countries/regions where TikTok trends are tracked.
"""

from __future__ import annotations

from typing import List

from sqlalchemy import Boolean, Enum, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.models.base import Base, TimestampMixin
from src.storage.models.enums import CountryCode


class Country(Base, TimestampMixin):
    """Country model for tracking regional TikTok data."""

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[CountryCode] = mapped_column(
        Enum(CountryCode), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    users_in_millions: Mapped[float] = mapped_column(Float, nullable=False)
    growth_rate: Mapped[float] = mapped_column(Float, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    hashtags: Mapped[List["Hashtag"]] = relationship(
        "Hashtag", back_populates="country", cascade="all, delete-orphan"
    )
    videos: Mapped[List["Video"]] = relationship(
        "Video", back_populates="country", cascade="all, delete-orphan"
    )
    creators: Mapped[List["Creator"]] = relationship(
        "Creator", back_populates="country", cascade="all, delete-orphan"
    )
    sounds: Mapped[List["Sound"]] = relationship(
        "Sound", back_populates="country", cascade="all, delete-orphan"
    )
    trends: Mapped[List["Trend"]] = relationship(
        "Trend", back_populates="country", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("idx_country_code", "code"), Index("idx_country_active", "is_active"))

    def __repr__(self) -> str:
        return f"<Country(code={self.code}, name={self.name})>"
