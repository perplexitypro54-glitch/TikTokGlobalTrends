"""
Niche Classification Module

Classifies content into TikTok niches (BookTok, FitTok, etc.) using advanced ML techniques.
"""

import re
import json
import pickle
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from collections import defaultdict, Counter
from pathlib import Path

# Optional ML dependencies
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, accuracy_score
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import LabelEncoder
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from src.utils.logger import setup_logger
from src.storage.models.enums import NicheType


@dataclass
class ClassificationResult:
    """Result of niche classification."""
    niche: NicheType
    confidence: float
    probabilities: Dict[NicheType, float]
    keywords_used: List[str]
    method_used: str
    processing_time_ms: float


@dataclass
class TrainingData:
    """Training data sample for niche classification."""
    text: str
    hashtags: List[str]
    niche: NicheType
    source: str = "manual"
    quality_score: float = 1.0


class NicheClassifier:
    """
    Advanced niche classifier using multiple ML approaches.
    
    Combines rule-based, statistical, and machine learning methods
    for accurate TikTok niche classification.
    """
    
    # Enhanced niche patterns with weights
    NICHE_PATTERNS = {
        NicheType.BOOKTOK: {
            "patterns": [
                r'\b(book|read|reading|author|novel|literature|library|bibliophile)\b',
                r'\b(booktok|bookrecommendation|bookreview|bookclub|tbr|currentlyreading)\b',
                r'\b(bestseller|paperback|hardcover|ebook|audiobook|kindle)\b',
                r'\b(literary|fiction|nonfiction|poetry|genre|classic)\b'
            ],
            "hashtags": ["#booktok", "#bookreview", "#bookrecommendation", "#reading", "#author"],
            "weight": 1.0
        },
        NicheType.FITNESS: {
            "patterns": [
                r'\b(workout|fitness|gym|exercise|training|health|wellness|cardio)\b',
                r'\b(fitnesstok|workoutmotivation|gymtok|fitnessjourney|healthylifestyle)\b',
                r'\b(personaltrainer|fitnessroutine|exercise|strength|muscle|weightloss)\b',
                r'\b(yoga|pilates|crossfit|hiit|cardio|flexibility|endurance)\b'
            ],
            "hashtags": ["#fitness", "#workout", "#gym", "#health", "#exercise", "#fitnesstok"],
            "weight": 1.0
        },
        NicheType.COOKING: {
            "patterns": [
                r'\b(food|cook|cooking|recipe|kitchen|chef|culinary|baking)\b',
                r'\b(foodtok|foodie|recipe|cookingtips|foodhacks|homemadefood)\b',
                r'\b(ingredient|flavor|delicious|tasty|meal|dinner|lunch|breakfast)\b',
                r'\b(restaurant|cuisine|gourmet|dish|appetizer|dessert|snack)\b'
            ],
            "hashtags": ["#food", "#cooking", "#recipe", "#foodtok", "#chef", "#foodie"],
            "weight": 1.0
        },
        NicheType.FASHION: {
            "patterns": [
                r'\b(fashion|style|outfit|clothing|wear|dress|apparel|textile)\b',
                r'\b(fashiontok|styletips|ootd|outfitinspo|fashionhacks|styling)\b',
                r'\b(sustainablefashion|thrift|vintage|designer|brand|collection)\b',
                r'\b(accessories|jewelry|shoes|bags|cosmetics|beauty|glamour)\b'
            ],
            "hashtags": ["#fashion", "#style", "#ootd", "#outfit", "#fashiontok", "#styletips"],
            "weight": 1.0
        },
        NicheType.TRAVEL: {
            "patterns": [
                r'\b(travel|vacation|trip|journey|explore|adventure|destination)\b',
                r'\b(traveltok|wanderlust|travelvlog|travelguide|travelphotography)\b',
                r'\b(hotel|flight|airport|passport|tourism|sightseeing|backpacking)\b',
                r'\b(beach|mountain|city|countryside|abroad|international|tourist)\b'
            ],
            "hashtags": ["#travel", "#vacation", "#traveltok", "#wanderlust", "#explore"],
            "weight": 1.0
        },
        NicheType.DANCE: {
            "patterns": [
                r'\b(dance|choreography|dancing|moves|steps|rhythm|beat)\b',
                r'\b(dancetok|dancechallenge|dancecover|dancetutorial|dancemoves)\b',
                r'\b(choreographer|dancer|performance|stage|routine|freestyle)\b',
                r'\b(hiphop|ballet|contemporary|salsa|ballroom|jazz|tap)\b'
            ],
            "hashtags": ["#dance", "#dancetok", "#dancechallenge", "#choreography", "#dancing"],
            "weight": 1.0
        },
        NicheType.COMEDY: {
            "patterns": [
                r'\b(funny|comedy|humor|joke|laughs|hilarious|entertainment)\b',
                r'\b(comedytok|funnyvideos|memes|sketch|standup|parody|spoof)\b',
                r'\b(laugh|hilarious|comedian|funnymoments|jokes|humorous)\b',
                r'\b(silly|amusing|entertaining|comical|wit|satire|irony)\b'
            ],
            "hashtags": ["#comedy", "#funny", "#comedytok", "#humor", "#laughs", "#memes"],
            "weight": 1.0
        },
        NicheType.BEAUTY: {
            "patterns": [
                r'\b(beauty|makeup|cosmetic|skincare|glam|beautytips|tutorial)\b',
                r'\b(beautytok|makeuptutorial|skincareroutine|beautytips|glamup)\b',
                r'\b(eyemakeup|lipstick|foundation|concealer|mascara|eyeliner)\b',
                r'\b(serum|moisturizer|cleanser|toner|facemask|skincare)\b'
            ],
            "hashtags": ["#beauty", "#makeup", "#skincare", "#beautytok", "#makeuptutorial"],
            "weight": 1.0
        },
        NicheType.GAMING: {
            "patterns": [
                r'\b(game|gaming|gamer|play|player|esports|tournament)\b',
                r'\b(gamingtok|gamertok|videogames|console|pc|mobile|streaming)\b',
                r'\b(controller|joystick|keyboard|mouse|headset|monitor|fps)\b',
                r'\b(nintendo|playstation|xbox|steam|twitch|youtube|discord)\b'
            ],
            "hashtags": ["#gaming", "#gamer", "#gamingtok", "#videogames", "#esports", "#streaming"],
            "weight": 1.0
        },
        NicheType.FINANCE: {
            "patterns": [
                r'\b(money|finance|financial|invest|investment|saving|budget)\b',
                r'\b(financetok|moneytok|investing|personalfinance|wealth|rich)\b',
                r'\b(stock|crypto|bitcoin|trading|portfolio|dividend|interest)\b',
                r'\b(budgeting|saving|retirement|insurance|tax|debt|credit)\b'
            ],
            "hashtags": ["#finance", "#money", "#investing", "#financetok", "#personalfinance"],
            "weight": 1.0
        },
        NicheType.EDUCATION: {
            "patterns": [
                r'\b(learn|education|study|school|knowledge|academic|teach)\b',
                r'\b(educationtok|learnontiktok|studytok|school|university|college)\b',
                r'\b(science|math|history|literature|physics|chemistry|biology)\b',
                r'\b(homework|exam|test|grade|student|teacher|professor)\b'
            ],
            "hashtags": ["#education", "#learn", "#study", "#educationtok", "#studytok"],
            "weight": 1.0
        },
        NicheType.PETS: {
            "patterns": [
                r'\b(pet|dog|cat|animal|pet|puppy|kitten|fur|cute)\b',
                r'\b(pettok|dogtok|cattok|cuteanimals|petlover|animallover)\b',
                r'\b(puppy|kitten|rescue|shelter|vet|grooming|training)\b',
                r'\b(breed|play|walk|feed|care|adopt|foster)\b'
            ],
            "hashtags": ["#pets", "#dogs", "#cats", "#pettok", "#cuteanimals", "#animals"],
            "weight": 1.0
        },
        NicheType.DIY: {
            "patterns": [
                r'\b(diy|craft|handmade|project|create|build|make|tutorial)\b',
                r'\b(diytok|crafttok|handmade|diyprojects|howto|tutorial)\b',
                r'\b(supplies|materials|tools|instructions|stepbystep|guide)\b',
                r'\b(creative|art|paint|draw|design|decorate|renovate)\b'
            ],
            "hashtags": ["#diy", "#crafts", "#handmade", "#diytok", "#howto", "#tutorial"],
            "weight": 1.0
        }
    }
    
    # Model file paths
    MODEL_DIR = Path("models")
    VECTORIZER_FILE = MODEL_DIR / "niche_vectorizer.pkl"
    CLASSIFIER_FILE = MODEL_DIR / "niche_classifier.pkl"
    LABEL_ENCODER_FILE = MODEL_DIR / "niche_label_encoder.pkl"
    TRAINING_DATA_FILE = MODEL_DIR / "training_data.json"
    
    def __init__(
        self,
        model_type: str = "ensemble",
        use_ml: bool = True,
        confidence_threshold: float = 0.3
    ):
        """
        Initialize niche classifier.
        
        Args:
            model_type: Type of ML model ('naive_bayes', 'random_forest', 'logistic', 'ensemble')
            use_ml: Whether to use ML models or rule-based only
            confidence_threshold: Minimum confidence for classification
        """
        self.model_type = model_type
        self.use_ml = use_ml
        self.confidence_threshold = confidence_threshold
        
        self.logger = setup_logger("niche_classifier")
        
        # Initialize components
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None
        self.is_trained = False
        
        # Statistics
        self._stats = {
            "classifications": 0,
            "rule_based": 0,
            "ml_based": 0,
            "fallbacks": 0,
            "high_confidence": 0,
            "low_confidence": 0
        }
        
        # Load existing models if available
        if self.use_ml:
            self._load_models()
        
        self.logger.info(
            f"NicheClassifier initialized (ML={use_ml}, model={model_type})"
        )
    
    def _load_models(self) -> None:
        """Load pre-trained models from disk."""
        try:
            if self.MODEL_DIR.exists():
                if self.VECTORIZER_FILE.exists():
                    self.vectorizer = joblib.load(self.VECTORIZER_FILE)
                
                if self.LABEL_ENCODER_FILE.exists():
                    self.label_encoder = joblib.load(self.LABEL_ENCODER_FILE)
                
                if self.CLASSIFIER_FILE.exists():
                    self.classifier = joblib.load(self.CLASSIFIER_FILE)
                    self.is_trained = True
                
                self.logger.info("Loaded existing models from disk")
        except Exception as e:
            self.logger.warning(f"Failed to load models: {str(e)}")
            self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize new ML models."""
        if not ML_AVAILABLE:
            self.logger.warning("ML dependencies not available, disabling ML features")
            self.use_ml = False
            return
            
        try:
            # Text vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.8,
                lowercase=True,
                strip_accents='ascii'
            )
            
            # Label encoder
            self.label_encoder = LabelEncoder()
            
            # Classifier based on type
            if self.model_type == "naive_bayes":
                self.classifier = MultinomialNB(alpha=0.1)
            elif self.model_type == "random_forest":
                self.classifier = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
            elif self.model_type == "logistic":
                self.classifier = LogisticRegression(
                    max_iter=1000,
                    random_state=42
                )
            elif self.model_type == "ensemble":
                # Simple ensemble using Random Forest
                self.classifier = RandomForestClassifier(
                    n_estimators=200,
                    max_depth=15,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42
                )
            
            self.logger.info(f"Initialized {self.model_type} model")
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {str(e)}")
            self.use_ml = False
    
    def _rule_based_classify(
        self,
        text: str,
        hashtags: List[str]
    ) -> Tuple[Optional[NicheType], float, Dict[str, float]]:
        """
        Classify using rule-based pattern matching.
        
        Args:
            text: Text content
            hashtags: List of hashtags
            
        Returns:
            Tuple of (niche, confidence, all_scores)
        """
        text = text.lower()
        hashtag_text = " ".join([h.lower().lstrip('#') for h in hashtags])
        combined_text = f"{text} {hashtag_text}"
        
        niche_scores = {}
        
        # Score each niche
        for niche, config in self.NICHE_PATTERNS.items():
            score = 0.0
            
            # Pattern matching in text
            for pattern in config["patterns"]:
                matches = re.findall(pattern, combined_text, re.IGNORECASE)
                score += len(matches) * config["weight"]
            
            # Hashtag matching (higher weight)
            for hashtag in config["hashtags"]:
                if hashtag.lower() in hashtag_text:
                    score += 2.0 * config["weight"]
            
            niche_scores[niche.value] = score
        
        # Find best niche
        if niche_scores:
            best_niche_name = max(niche_scores, key=niche_scores.get)
            best_score = niche_scores[best_niche_name]
            
            if best_score > 0:
                best_niche = NicheType(best_niche_name)
                confidence = min(1.0, best_score / 10.0)  # Normalize to 0-1
                return best_niche, confidence, niche_scores
        
        return None, 0.0, niche_scores
    
    def _ml_classify(
        self,
        text: str,
        hashtags: List[str]
    ) -> Tuple[Optional[NicheType], float, Dict[str, float]]:
        """
        Classify using ML models.
        
        Args:
            text: Text content
            hashtags: List of hashtags
            
        Returns:
            Tuple of (niche, confidence, all_probabilities)
        """
        if not self.is_trained or not self.use_ml:
            return None, 0.0, {}
        
        try:
            # Prepare features
            combined_text = f"{text} {' '.join(hashtags)}"
            
            # Vectorize text
            text_features = self.vectorizer.transform([combined_text])
            
            # Predict
            prediction = self.classifier.predict(text_features)[0]
            probabilities = self.classifier.predict_proba(text_features)[0]
            
            # Convert label encoder back to niche
            niche_name = self.label_encoder.inverse_transform([prediction])[0]
            niche = NicheType(niche_name)
            
            # Create probability dictionary
            prob_dict = {}
            for i, prob in enumerate(probabilities):
                niche_name = self.label_encoder.inverse_transform([i])[0]
                prob_dict[niche_name] = prob
            
            confidence = max(probabilities)
            
            return niche, confidence, prob_dict
            
        except Exception as e:
            self.logger.error(f"ML classification failed: {str(e)}")
            return None, 0.0, {}
    
    def classify(
        self,
        text: str,
        hashtags: List[str],
        method: str = "hybrid"
    ) -> ClassificationResult:
        """
        Classify content into niche.
        
        Args:
            text: Content text or description
            hashtags: List of hashtags
            method: Classification method ('rule', 'ml', 'hybrid')
            
        Returns:
            ClassificationResult with niche and confidence
        """
        start_time = datetime.now()
        
        # Clean inputs
        text = text or ""
        hashtags = hashtags or []
        
        self._stats["classifications"] += 1
        
        # Rule-based classification
        rule_niche, rule_confidence, rule_scores = self._rule_based_classify(text, hashtags)
        
        # ML classification
        ml_niche, ml_confidence, ml_probs = self._ml_classify(text, hashtags)
        
        # Combine results based on method
        if method == "rule" or not self.use_ml:
            final_niche = rule_niche or NicheType.OTHER
            final_confidence = rule_confidence
            final_probabilities = {NicheType(name): score for name, score in rule_scores.items()}
            method_used = "rule_based"
            self._stats["rule_based"] += 1
            
        elif method == "ml":
            final_niche = ml_niche or NicheType.OTHER
            final_confidence = ml_confidence
            final_probabilities = {NicheType(name): prob for name, prob in ml_probs.items()}
            method_used = "ml_based"
            self._stats["ml_based"] += 1
            
        else:  # hybrid
            # Combine rule-based and ML results
            if rule_niche and ml_niche:
                if rule_niche == ml_niche:
                    # Both agree - high confidence
                    final_niche = rule_niche
                    final_confidence = (rule_confidence + ml_confidence) / 2
                else:
                    # Disagree - use higher confidence
                    if rule_confidence > ml_confidence:
                        final_niche = rule_niche
                        final_confidence = rule_confidence
                    else:
                        final_niche = ml_niche
                        final_confidence = ml_confidence
            elif rule_niche:
                final_niche = rule_niche
                final_confidence = rule_confidence
            elif ml_niche:
                final_niche = ml_niche
                final_confidence = ml_confidence
            else:
                final_niche = NicheType.OTHER
                final_confidence = 0.0
            
            # Combine probabilities
            final_probabilities = {}
            all_niches = set(rule_scores.keys()) | set(ml_probs.keys())
            for niche_name in all_niches:
                niche = NicheType(niche_name)
                rule_score = rule_scores.get(niche_name, 0) / 10.0  # Normalize
                ml_prob = ml_probs.get(niche_name, 0)
                final_probabilities[niche] = (rule_score + ml_prob) / 2
            
            method_used = "hybrid"
        
        # Apply confidence threshold
        if final_confidence < self.confidence_threshold:
            final_niche = NicheType.OTHER
            final_confidence = 0.0
            self._stats["fallbacks"] += 1
        elif final_confidence > 0.7:
            self._stats["high_confidence"] += 1
        else:
            self._stats["low_confidence"] += 1
        
        # Extract keywords used
        keywords_used = self._extract_classification_keywords(text, hashtags, final_niche)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ClassificationResult(
            niche=final_niche,
            confidence=final_confidence,
            probabilities=final_probabilities,
            keywords_used=keywords_used,
            method_used=method_used,
            processing_time_ms=processing_time
        )
    
    def _extract_classification_keywords(
        self,
        text: str,
        hashtags: List[str],
        niche: NicheType
    ) -> List[str]:
        """Extract keywords that contributed to classification."""
        keywords = []
        
        if niche == NicheType.OTHER:
            return keywords
        
        config = self.NICHE_PATTERNS.get(niche, {})
        
        # Check patterns in text
        text_lower = text.lower()
        for pattern in config.get("patterns", []):
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            keywords.extend(matches)
        
        # Check hashtags
        for hashtag in hashtags:
            hashtag_lower = hashtag.lower().lstrip('#')
            if hashtag_lower in [h.lstrip('#') for h in config.get("hashtags", [])]:
                keywords.append(hashtag)
        
        # Remove duplicates and limit
        return list(set(keywords))[:5]
    
    def train(
        self,
        training_data: List[TrainingData],
        test_size: float = 0.2,
        save_models: bool = True
    ) -> Dict[str, float]:
        """
        Train the ML classifier with new data.
        
        Args:
            training_data: List of training samples
            test_size: Fraction of data for testing
            save_models: Whether to save trained models
            
        Returns:
            Training metrics
        """
        if not training_data:
            raise ValueError("Training data cannot be empty")
        
        self.logger.info(f"Training classifier with {len(training_data)} samples")
        
        # Prepare data
        texts = []
        labels = []
        
        for sample in training_data:
            combined_text = f"{sample.text} {' '.join(sample.hashtags)}"
            texts.append(combined_text)
            labels.append(sample.niche.value)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        # Vectorize text
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Encode labels
        y_train_enc = self.label_encoder.fit_transform(y_train)
        y_test_enc = self.label_encoder.transform(y_test)
        
        # Train classifier
        self.classifier.fit(X_train_vec, y_train_enc)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test_vec)
        accuracy = accuracy_score(y_test_enc, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.classifier, X_train_vec, y_train_enc, cv=5
        )
        
        self.is_trained = True
        
        # Save models
        if save_models:
            self._save_models()
            self._save_training_data(training_data)
        
        metrics = {
            "accuracy": accuracy,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        }
        
        self.logger.info(f"Training completed. Accuracy: {accuracy:.3f}")
        
        return metrics
    
    def _save_models(self) -> None:
        """Save trained models to disk."""
        try:
            self.MODEL_DIR.mkdir(exist_ok=True)
            
            joblib.dump(self.vectorizer, self.VECTORIZER_FILE)
            joblib.dump(self.classifier, self.CLASSIFIER_FILE)
            joblib.dump(self.label_encoder, self.LABEL_ENCODER_FILE)
            
            self.logger.info("Models saved to disk")
        except Exception as e:
            self.logger.error(f"Failed to save models: {str(e)}")
    
    def _save_training_data(self, training_data: List[TrainingData]) -> None:
        """Save training data for future use."""
        try:
            data_dicts = [
                {
                    "text": sample.text,
                    "hashtags": sample.hashtags,
                    "niche": sample.niche.value,
                    "source": sample.source,
                    "quality_score": sample.quality_score
                }
                for sample in training_data
            ]
            
            with open(self.TRAINING_DATA_FILE, 'w') as f:
                json.dump(data_dicts, f, indent=2)
            
            self.logger.info(f"Saved {len(training_data)} training samples")
        except Exception as e:
            self.logger.error(f"Failed to save training data: {str(e)}")
    
    def get_supported_niches(self) -> List[NicheType]:
        """Get list of supported niche types."""
        return list(self.NICHE_PATTERNS.keys())
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics."""
        total = self._stats["classifications"]
        
        return {
            "total_classifications": total,
            "rule_based": {
                "count": self._stats["rule_based"],
                "percentage": self._stats["rule_based"] / max(1, total) * 100
            },
            "ml_based": {
                "count": self._stats["ml_based"],
                "percentage": self._stats["ml_based"] / max(1, total) * 100
            },
            "fallbacks": {
                "count": self._stats["fallbacks"],
                "percentage": self._stats["fallbacks"] / max(1, total) * 100
            },
            "confidence": {
                "high": self._stats["high_confidence"],
                "low": self._stats["low_confidence"],
                "high_percentage": self._stats["high_confidence"] / max(1, total) * 100
            },
            "model_info": {
                "type": self.model_type,
                "trained": self.is_trained,
                "ml_enabled": self.use_ml,
                "confidence_threshold": self.confidence_threshold
            }
        }
    
    def reset_stats(self) -> None:
        """Reset classification statistics."""
        self._stats = {
            "classifications": 0,
            "rule_based": 0,
            "ml_based": 0,
            "fallbacks": 0,
            "high_confidence": 0,
            "low_confidence": 0
        }
        
        self.logger.info("NicheClassifier statistics reset")
    
    def create_training_sample(
        self,
        text: str,
        hashtags: List[str],
        niche: NicheType,
        source: str = "manual"
    ) -> TrainingData:
        """Create a training data sample."""
        return TrainingData(
            text=text,
            hashtags=hashtags,
            niche=niche,
            source=source
        )
    
    def batch_classify(
        self,
        texts: List[str],
        hashtags_list: List[List[str]],
        method: str = "hybrid"
    ) -> List[ClassificationResult]:
        """Classify multiple texts in batch."""
        results = []
        
        for text, hashtags in zip(texts, hashtags_list):
            result = self.classify(text, hashtags, method)
            results.append(result)
        
        return results