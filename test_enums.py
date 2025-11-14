"""
Standalone enums for testing without external dependencies.
"""

from enum import Enum


class CountryCode(Enum):
    """Country codes for TikTok regions."""
    US = "US"
    BR = "BR"
    MX = "MX"
    ID = "ID"
    JP = "JP"
    GB = "GB"
    CA = "CA"
    AU = "AU"
    DE = "DE"
    FR = "FR"
    IT = "IT"
    ES = "ES"


class NicheType(Enum):
    """Content niche categories."""
    BOOKTOK = "BOOKTOK"
    FITNESS = "FITNESS"
    COOKING = "COOKING"
    FASHION = "FASHION"
    TRAVEL = "TRAVEL"
    DANCE = "DANCE"
    COMEDY = "COMEDY"
    BEAUTY = "BEAUTY"
    GAMING = "GAMING"
    FINANCE = "FINANCE"
    EDUCATION = "EDUCATION"
    PETS = "PETS"
    DIY = "DIY"
    OTHER = "OTHER"


class TrendDirection(Enum):
    """Trend direction indicators."""
    UPWARD = "UPWARD"
    RISING = "RISING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"
    DOWNWARD = "DOWNWARD"


class SentimentType(Enum):
    """Sentiment analysis results."""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class DataSourceType(Enum):
    """Data source types."""
    OFFICIAL_API = "OFFICIAL_API"
    CREATIVE_CENTER = "CREATIVE_CENTER"
    PLAYWRIGHT = "PLAYWRIGHT"
    CACHED = "CACHED"
    MANUAL = "MANUAL"