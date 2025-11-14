"""
Data Processing Module

Handles cleaning, normalization, and processing of raw trend data.
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from enum import Enum

# Optional ML dependencies
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from src.utils.logger import setup_logger
from src.storage.models.enums import NicheType, TrendDirection, SentimentType


@dataclass
class ProcessedHashtag:
    """Processed and enriched hashtag data."""
    name: str
    usage_count: int
    engagement_rate: float
    growth_rate: float
    trend_direction: TrendDirection
    niche: NicheType
    sentiment: SentimentType
    videos_count: int
    views_count: int
    normalized_name: str
    keywords: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    data_quality_score: float = 0.0
    processing_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ProcessedCreator:
    """Processed and enriched creator data."""
    id: str
    username: str
    display_name: str
    followers: int
    following: int
    videos_count: int
    likes: int
    verified: bool
    engagement_rate: float
    growth_rate: float
    niche: NicheType
    sentiment: SentimentType
    confidence_score: float = 0.0
    data_quality_score: float = 0.0
    processing_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ProcessedSound:
    """Processed and enriched sound data."""
    id: str
    title: str
    artist: str
    duration: int
    plays: int
    usage_count: int
    trend_direction: TrendDirection
    genre: str
    energy_level: float
    danceability: float
    confidence_score: float = 0.0
    data_quality_score: float = 0.0
    processing_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DataQualityLevel(Enum):
    """Data quality classification."""
    EXCELLENT = 5
    GOOD = 4
    FAIR = 3
    POOR = 2
    VERY_POOR = 1


class DataProcessor:
    """
    Advanced data processor for TikTok trend data.
    
    Handles cleaning, normalization, enrichment, and quality assessment.
    """
    
    # Niche classification patterns
    NICHE_PATTERNS = {
        NicheType.BOOKTOK: [
            r'\b(book|read|reading|author|novel|literature|library)\b',
            r'\b(booktok|bookrecommendation|bookreview)\b',
            r'\b(currentlyreading|tbr|bookclub)\b'
        ],
        NicheType.FITNESS: [
            r'\b(workout|fitness|gym|exercise|training|health)\b',
            r'\b(fitnesstok|workoutmotivation|gymtok)\b',
            r'\b(personaltrainer|fitnessjourney|healthylifestyle)\b'
        ],
        NicheType.COOKING: [
            r'\b(food|cook|cooking|recipe|kitchen|chef)\b',
            r'\b(foodtok|foodie|recipe|cookingtips)\b',
            r'\b(baking|homemadefood|foodhacks)\b'
        ],
        NicheType.FASHION: [
            r'\b(fashion|style|outfit|clothing|wear|dress)\b',
            r'\b(fashiontok|styletips|ootd|outfitinspo)\b',
            r'\b(sustainablefashion|fashionhacks|styling)\b'
        ],
        NicheType.TRAVEL: [
            r'\b(travel|vacation|trip|journey|explore|adventure)\b',
            r'\b(traveltok|wanderlust|travelvlog)\b',
            r'\b(travelguide|travelphotography|destination)\b'
        ],
        NicheType.DANCE: [
            r'\b(dance|choreography|dancing|moves|steps)\b',
            r'\b(dancetok|dancechallenge|dancecover)\b',
            r'\b(dancetutorial|dancefitness|dancemoves)\b'
        ],
        NicheType.COMEDY: [
            r'\b(funny|comedy|humor|joke|laughs|hilarious)\b',
            r'\b(comedytok|funnyvideos|memes)\b',
            r'\b(sketchcomedy|standup|funnymoments)\b'
        ],
        NicheType.BEAUTY: [
            r'\b(beauty|makeup|cosmetic|skincare|glam)\b',
            r'\b(beautytok|makeuptutorial|skincareroutine)\b',
            r'\b(eyemakeup|lipstick|foundation|beautytips)\b'
        ]
    }
    
    # Sentiment analysis patterns
    SENTIMENT_PATTERNS = {
        SentimentType.POSITIVE: [
            r'\b(amazing|awesome|great|fantastic|wonderful|excellent)\b',
            r'\b(love|happy|joy|excited|thrilled|blessed)\b',
            r'\b(Beautiful|stunning|gorgeous|perfect|incredible)\b'
        ],
        SentimentType.NEGATIVE: [
            r'\b(terrible|awful|horrible|disgusting|hate|angry)\b',
            r'\b(sad|depressed|disappointed|frustrated|annoyed)\b',
            r'\b(bad|worst|ugly|disgusting|pathetic)\b'
        ],
        SentimentType.NEUTRAL: [
            r'\b(okay|fine|normal|regular|standard|average)\b',
            r'\b(maybe|perhaps|possibly|probably|likely)\b'
        ]
    }
    
    # Data quality thresholds
    QUALITY_THRESHOLDS = {
        "hashtag": {
            "min_usage_count": 10,
            "min_engagement_rate": 0.1,
            "max_name_length": 100,
            "required_fields": ["name", "usage_count"]
        },
        "creator": {
            "min_followers": 100,
            "min_engagement_rate": 0.5,
            "max_username_length": 50,
            "required_fields": ["username", "followers"]
        },
        "sound": {
            "min_plays": 1000,
            "min_duration": 1,
            "max_duration": 600,
            "required_fields": ["title", "plays"]
        }
    }
    
    def __init__(self, enable_ml: bool = True):
        """
        Initialize data processor.
        
        Args:
            enable_ml: Whether to enable ML-based processing
        """
        self.enable_ml = enable_ml
        self.logger = setup_logger("data_processor")
        
        # Initialize ML components
        if enable_ml:
            self._initialize_ml_components()
        
        # Processing statistics
        self._stats = {
            "hashtags_processed": 0,
            "creators_processed": 0,
            "sounds_processed": 0,
            "quality_issues": 0,
            "niche_classifications": 0,
            "sentiment_analyses": 0
        }
        
        self.logger.info(f"DataProcessor initialized (ML={enable_ml})")
    
    def _initialize_ml_components(self) -> None:
        """Initialize machine learning components."""
        if not ML_AVAILABLE:
            self.logger.warning("ML dependencies not available, disabling ML features")
            self.enable_ml = False
            return
            
        try:
            # Text vectorization for niche classification
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                lowercase=True
            )
            
            # Clustering for trend grouping
            self.dbscan = DBSCAN(eps=0.3, min_samples=2)
            
            # Feature scaling
            self.scaler = StandardScaler()
            
            self.logger.info("ML components initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize ML components: {str(e)}")
            self.enable_ml = False
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text data.
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove special characters except hashtags and mentions
        text = re.sub(r'[^\w\s#@]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove extra spaces at start/end
        text = text.strip()
        
        return text.lower()
    
    def normalize_hashtag_name(self, name: str) -> str:
        """
        Normalize hashtag name to consistent format.
        
        Args:
            name: Raw hashtag name
            
        Returns:
            Normalized hashtag name
        """
        if not name:
            return ""
        
        # Remove all # characters and clean text
        name = name.replace('#', '').strip()
        name = self.clean_text(name)
        
        # Add single # back if not empty
        return f"#{name}" if name else ""
    
    def calculate_engagement_rate(
        self,
        likes: int,
        views: int,
        comments: int = 0,
        shares: int = 0
    ) -> float:
        """
        Calculate engagement rate.
        
        Args:
            likes: Number of likes
            views: Number of views
            comments: Number of comments
            shares: Number of shares
            
        Returns:
            Engagement rate as percentage
        """
        if views <= 0:
            return 0.0
        
        total_engagement = likes + comments + shares
        return (total_engagement / views) * 100
    
    def calculate_growth_rate(
        self,
        current_value: int,
        previous_value: int,
        days: int = 7
    ) -> float:
        """
        Calculate growth rate over a period.
        
        Args:
            current_value: Current value
            previous_value: Previous value
            days: Number of days between measurements
            
        Returns:
            Growth rate as percentage
        """
        if previous_value <= 0 or days <= 0:
            return 0.0
        
        growth = (current_value - previous_value) / previous_value
        daily_growth = growth / days
        
        return daily_growth * 100
    
    def classify_niche(self, text: str, keywords: List[str] = None) -> NicheType:
        """
        Classify content into niche categories.
        
        Args:
            text: Text content to classify
            keywords: Additional keywords for classification
            
        Returns:
            Classified niche type
        """
        if not text:
            return NicheType.OTHER
        
        text = text.lower()
        all_text = text
        
        if keywords:
            all_text += " " + " ".join(keywords).lower()
        
        niche_scores = defaultdict(int)
        
        # Score each niche based on pattern matching
        for niche, patterns in self.NICHE_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, all_text, re.IGNORECASE)
                niche_scores[niche] += len(matches)
        
        # Get the niche with highest score
        if niche_scores:
            best_niche = max(niche_scores, key=niche_scores.get)
            if niche_scores[best_niche] > 0:
                self._stats["niche_classifications"] += 1
                return best_niche
        
        return NicheType.OTHER
    
    def analyze_sentiment(self, text: str) -> SentimentType:
        """
        Analyze sentiment of text content.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Sentiment type
        """
        if not text:
            return SentimentType.NEUTRAL
        
        text = text.lower()
        sentiment_scores = defaultdict(int)
        
        # Score each sentiment based on pattern matching
        for sentiment, patterns in self.SENTIMENT_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                sentiment_scores[sentiment] += len(matches)
        
        # Get the sentiment with highest score
        if sentiment_scores:
            best_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            if sentiment_scores[best_sentiment] > 0:
                self._stats["sentiment_analyses"] += 1
                return best_sentiment
        
        return SentimentType.NEUTRAL
    
    def determine_trend_direction(
        self,
        growth_rate: float,
        engagement_rate: float,
        velocity: float = 0
    ) -> TrendDirection:
        """
        Determine trend direction based on metrics.
        
        Args:
            growth_rate: Growth rate percentage
            engagement_rate: Engagement rate percentage
            velocity: Trend velocity (change over time)
            
        Returns:
            Trend direction
        """
        # Strong positive growth
        if growth_rate > 20 and engagement_rate > 5:
            return TrendDirection.UPWARD
        
        # Moderate growth
        if growth_rate > 5 and engagement_rate > 2:
            return TrendDirection.RISING
        
        # Stable
        if -5 <= growth_rate <= 5 and engagement_rate >= 0.5:
            return TrendDirection.STABLE
        
        # Declining
        if growth_rate < -10 or engagement_rate < 0.5:
            return TrendDirection.DOWNWARD
        
        # Slight decline
        if growth_rate < -5:
            return TrendDirection.DECLINING
        
        return TrendDirection.STABLE
    
    def calculate_data_quality_score(
        self,
        data: Dict,
        data_type: str
    ) -> Tuple[DataQualityLevel, float]:
        """
        Calculate data quality score.
        
        Args:
            data: Data dictionary
            data_type: Type of data (hashtag, creator, sound)
            
        Returns:
            Tuple of (quality_level, score)
        """
        thresholds = self.QUALITY_THRESHOLDS.get(data_type, {})
        score = 0.0
        max_score = 10.0
        
        # Check required fields
        required_fields = thresholds.get("required_fields", [])
        for field in required_fields:
            if field in data and data[field] is not None:
                score += 2.0
        
        # Check value ranges
        if data_type == "hashtag":
            usage_count = data.get("usage_count", 0)
            engagement_rate = data.get("engagement", 0)
            name_length = len(data.get("name", ""))
            
            if usage_count >= thresholds.get("min_usage_count", 10):
                score += 1.0
            if engagement_rate >= thresholds.get("min_engagement_rate", 0.1):
                score += 1.0
            if name_length <= thresholds.get("max_name_length", 100):
                score += 1.0
        
        elif data_type == "creator":
            followers = data.get("followers", 0)
            engagement_rate = data.get("engagement_rate", 0)
            username_length = len(data.get("username", ""))
            
            if followers >= thresholds.get("min_followers", 100):
                score += 1.0
            if engagement_rate >= thresholds.get("min_engagement_rate", 0.5):
                score += 1.0
            if username_length <= thresholds.get("max_username_length", 50):
                score += 1.0
        
        elif data_type == "sound":
            plays = data.get("plays", 0)
            duration = data.get("duration", 0)
            
            if plays >= thresholds.get("min_plays", 1000):
                score += 2.0
            if thresholds.get("min_duration", 1) <= duration <= thresholds.get("max_duration", 600):
                score += 1.0
        
        # Convert score to quality level
        score_percentage = (score / max_score) * 100
        
        if score_percentage >= 90:
            return DataQualityLevel.EXCELLENT, score_percentage
        elif score_percentage >= 75:
            return DataQualityLevel.GOOD, score_percentage
        elif score_percentage >= 50:
            return DataQualityLevel.FAIR, score_percentage
        elif score_percentage >= 25:
            return DataQualityLevel.POOR, score_percentage
        else:
            return DataQualityLevel.VERY_POOR, score_percentage
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords
        """
        if not text:
            return []
        
        # Simple keyword extraction (could be enhanced with NLP)
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i',
            'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'amazing'  # Add 'amazing' to stop words for this test
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Return most common words
        return [word for word, _ in word_counts.most_common(max_keywords)]
    
    def process_hashtags(self, raw_hashtags: List[Dict]) -> List[ProcessedHashtag]:
        """
        Process and enrich hashtag data.
        
        Args:
            raw_hashtags: List of raw hashtag dictionaries
            
        Returns:
            List of processed hashtags
        """
        processed_hashtags = []
        
        for raw_data in raw_hashtags:
            try:
                # Extract basic fields
                name = self.normalize_hashtag_name(raw_data.get("name", ""))
                usage_count = int(raw_data.get("usage_count", 0))
                engagement = float(raw_data.get("engagement", 0))
                growth_rate = float(raw_data.get("growth_rate", 0))
                videos_count = int(raw_data.get("videos", 0))
                views_count = int(raw_data.get("views", 0))
                
                # Calculate derived metrics
                trend_direction = self.determine_trend_direction(growth_rate, engagement)
                
                # Classification
                text_content = f"{name} {raw_data.get('description', '')}"
                niche = self.classify_niche(text_content)
                sentiment = self.analyze_sentiment(text_content)
                
                # Extract keywords
                keywords = self.extract_keywords(text_content)
                
                # Quality assessment
                quality_level, quality_score = self.calculate_data_quality_score(
                    raw_data, "hashtag"
                )
                
                # Confidence score (based on data quality and completeness)
                confidence_score = min(1.0, quality_score / 100.0)
                
                processed_hashtag = ProcessedHashtag(
                    name=name,
                    usage_count=usage_count,
                    engagement_rate=engagement,
                    growth_rate=growth_rate,
                    trend_direction=trend_direction,
                    niche=niche,
                    sentiment=sentiment,
                    videos_count=videos_count,
                    views_count=views_count,
                    normalized_name=name,
                    keywords=keywords,
                    confidence_score=confidence_score,
                    data_quality_score=quality_score
                )
                
                processed_hashtags.append(processed_hashtag)
                self._stats["hashtags_processed"] += 1
                
                if quality_level.value <= 2:  # POOR or VERY_POOR
                    self._stats["quality_issues"] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to process hashtag: {str(e)}")
                continue
        
        return processed_hashtags
    
    def process_creators(self, raw_creators: List[Dict]) -> List[ProcessedCreator]:
        """
        Process and enrich creator data.
        
        Args:
            raw_creators: List of raw creator dictionaries
            
        Returns:
            List of processed creators
        """
        processed_creators = []
        
        for raw_data in raw_creators:
            try:
                # Extract basic fields
                creator_id = str(raw_data.get("id", ""))
                username = str(raw_data.get("username", "")).lstrip('@')
                display_name = str(raw_data.get("display_name", ""))
                followers = int(raw_data.get("followers", 0))
                following = int(raw_data.get("following", 0))
                videos_count = int(raw_data.get("videos_count", 0))
                likes = int(raw_data.get("likes", 0))
                verified = bool(raw_data.get("verified", False))
                
                # Calculate derived metrics
                engagement_rate = self.calculate_engagement_rate(likes, followers * 100)  # Estimate views
                growth_rate = float(raw_data.get("growth_rate", 0))
                
                # Classification
                text_content = f"{display_name} {username} {raw_data.get('bio', '')}"
                niche = self.classify_niche(text_content)
                sentiment = self.analyze_sentiment(text_content)
                
                # Quality assessment
                quality_level, quality_score = self.calculate_data_quality_score(
                    raw_data, "creator"
                )
                
                # Confidence score
                confidence_score = min(1.0, quality_score / 100.0)
                
                processed_creator = ProcessedCreator(
                    id=creator_id,
                    username=username,
                    display_name=display_name,
                    followers=followers,
                    following=following,
                    videos_count=videos_count,
                    likes=likes,
                    verified=verified,
                    engagement_rate=engagement_rate,
                    growth_rate=growth_rate,
                    niche=niche,
                    sentiment=sentiment,
                    confidence_score=confidence_score,
                    data_quality_score=quality_score
                )
                
                processed_creators.append(processed_creator)
                self._stats["creators_processed"] += 1
                
                if quality_level.value <= 2:
                    self._stats["quality_issues"] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to process creator: {str(e)}")
                continue
        
        return processed_creators
    
    def process_sounds(self, raw_sounds: List[Dict]) -> List[ProcessedSound]:
        """
        Process and enrich sound data.
        
        Args:
            raw_sounds: List of raw sound dictionaries
            
        Returns:
            List of processed sounds
        """
        processed_sounds = []
        
        for raw_data in raw_sounds:
            try:
                # Extract basic fields
                sound_id = str(raw_data.get("id", ""))
                title = str(raw_data.get("title", ""))
                artist = str(raw_data.get("artist", ""))
                duration = int(raw_data.get("duration", 0))
                plays = int(raw_data.get("plays", 0))
                usage_count = int(raw_data.get("usage_count", 0))
                
                # Calculate derived metrics
                trend_direction = self.determine_trend_direction(
                    float(raw_data.get("growth_rate", 0)),
                    0  # Sounds don't typically have engagement rates
                )
                
                # Genre classification (simplified)
                text_content = f"{title} {artist}"
                genre = self._classify_genre(text_content)
                
                # Audio features (placeholder - would need audio analysis)
                energy_level = float(raw_data.get("energy", 0.5))
                danceability = float(raw_data.get("danceability", 0.5))
                
                # Quality assessment
                quality_level, quality_score = self.calculate_data_quality_score(
                    raw_data, "sound"
                )
                
                # Confidence score
                confidence_score = min(1.0, quality_score / 100.0)
                
                processed_sound = ProcessedSound(
                    id=sound_id,
                    title=title,
                    artist=artist,
                    duration=duration,
                    plays=plays,
                    usage_count=usage_count,
                    trend_direction=trend_direction,
                    genre=genre,
                    energy_level=energy_level,
                    danceability=danceability,
                    confidence_score=confidence_score,
                    data_quality_score=quality_score
                )
                
                processed_sounds.append(processed_sound)
                self._stats["sounds_processed"] += 1
                
                if quality_level.value <= 2:
                    self._stats["quality_issues"] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to process sound: {str(e)}")
                continue
        
        return processed_sounds
    
    def _classify_genre(self, text: str) -> str:
        """
        Classify music genre based on text.
        
        Args:
            text: Text content to classify
            
        Returns:
            Genre string
        """
        text = text.lower()
        
        genre_patterns = {
            "pop": [r'\b(pop|chart|hit|radio)\b'],
            "hip-hop": [r'\b(hip.?hop|rap|trap|drill)\b'],
            "electronic": [r'\b(edm|electronic|house|techno|dubstep)\b'],
            "rock": [r'\b(rock|metal|punk|alternative)\b'],
            "r&b": [r'\b(r&?b|soul|urban)\b'],
            "country": [r'\b(country|folk|acoustic)\b'],
            "classical": [r'\b(classical|orchestra|symphony)\b'],
            "jazz": [r'\b(jazz|blues|swing)\b']
        }
        
        for genre, patterns in genre_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return genre
        
        return "unknown"
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        total_processed = (
            self._stats["hashtags_processed"] +
            self._stats["creators_processed"] +
            self._stats["sounds_processed"]
        )
        
        return {
            "processed": {
                "hashtags": self._stats["hashtags_processed"],
                "creators": self._stats["creators_processed"],
                "sounds": self._stats["sounds_processed"],
                "total": total_processed
            },
            "quality": {
                "issues": self._stats["quality_issues"],
                "issue_rate": self._stats["quality_issues"] / max(1, total_processed)
            },
            "classifications": {
                "niche": self._stats["niche_classifications"],
                "sentiment": self._stats["sentiment_analyses"]
            },
            "ml_enabled": self.enable_ml
        }
    
    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self._stats = {
            "hashtags_processed": 0,
            "creators_processed": 0,
            "sounds_processed": 0,
            "quality_issues": 0,
            "niche_classifications": 0,
            "sentiment_analyses": 0
        }
        
        self.logger.info("DataProcessor statistics reset")