"""
Enumerations for database models.
"""

from enum import Enum


class CountryCode(str, Enum):
    """Supported country codes."""

    US = "US"
    BR = "BR"
    MX = "MX"
    ID = "ID"
    PH = "PH"
    VN = "VN"
    PK = "PK"
    BD = "BD"
    EG = "EG"
    NG = "NG"
    TH = "TH"
    JP = "JP"
    UK = "UK"
    DE = "DE"
    FR = "FR"


class NicheType(str, Enum):
    """Content niche types."""

    BOOKTOK = "BOOKTOK"
    HEALTHTOK = "HEALTHTOK"
    DIYTOK = "DIYTOK"
    GAMINGTOK = "GAMINGTOK"
    FINANCETOK = "FINANCETOK"
    MUSICTOK = "MUSICTOK"
    COMEDYTOK = "COMEDYTOK"
    ACTIVISMTOK = "ACTIVISMTOK"
    FOODTOK = "FOODTOK"
    BEAUTYTOK = "BEAUTYTOK"
    FASHIONTOK = "FASHIONTOK"
    DANCETOK = "DANCETOK"
    COMMERCETOK = "COMMERCETOK"
    EDUCATIONTOK = "EDUCATIONTOK"
    LIFESTYLETOK = "LIFESTYLETOK"
    TRAVELLTOK = "TRAVELLTOK"
    ENTERTAINMENTTOK = "ENTERTAINMENTTOK"
    ARTTOK = "ARTTOK"
    ENTREPRENEURTOK = "ENTREPRENEURTOK"


class TrendDirection(str, Enum):
    """Trend direction options."""

    UP = "UP"
    DOWN = "DOWN"
    STABLE = "STABLE"


class SentimentType(str, Enum):
    """Sentiment classification."""

    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class DataSourceType(str, Enum):
    """Source of collected data."""

    OFFICIAL_API = "OFFICIAL_API"
    CREATIVE_CENTER = "CREATIVE_CENTER"
    PLAYWRIGHT_SCRAPER = "PLAYWRIGHT_SCRAPER"
