#!/usr/bin/env python3
"""
Simple integration test for the new components without external dependencies.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import standalone enums for testing
from test_enums import CountryCode, NicheType, TrendDirection, SentimentType

# Mock the enum imports to avoid SQLAlchemy dependency
sys.modules['src.storage.models.enums'] = type(sys)('enums')
sys.modules['src.storage.models.enums'].CountryCode = CountryCode
sys.modules['src.storage.models.enums'].NicheType = NicheType
sys.modules['src.storage.models.enums'].TrendDirection = TrendDirection
sys.modules['src.storage.models.enums'].SentimentType = SentimentType
sys.modules['src.storage.models.enums'].DataSourceType = type('DataSourceType', (), {'OFFICIAL_API': 'OFFICIAL_API'})


# Test basic imports that don't require external dependencies
def test_basic_imports():
    """Test that basic modules can be imported."""
    try:
        # Test logger
        from src.utils.logger import setup_logger
        logger = setup_logger('test')
        logger.info('Logger test successful')
        
        # Test enums (should work without SQLAlchemy)
        assert CountryCode.US.value == 'US'
        assert NicheType.FITNESS.value == 'FITNESS'
        assert TrendDirection.UPWARD.value == 'UPWARD'
        
        print("✅ Basic imports and enums work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Basic imports failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_text_processing():
    """Test text processing functions without ML."""
    try:
        from src.data_processing.processor import DataProcessor
        
        # Initialize without ML
        processor = DataProcessor(enable_ml=False)
        
        # Test text cleaning
        dirty_text = "Hello!!!   World   #test   "
        clean = processor.clean_text(dirty_text)
        expected = "hello world #test"
        assert clean == expected, f"Expected '{expected}', got '{clean}'"
        
        # Test hashtag normalization
        hashtag = processor.normalize_hashtag_name("##FITNESS##")
        expected = "#fitness"
        assert hashtag == expected, f"Expected '{expected}', got '{hashtag}'"
        
        # Test engagement calculation
        engagement = processor.calculate_engagement_rate(likes=100, views=10000)
        expected = 1.0  # (100/10000) * 100
        assert abs(engagement - expected) < 0.01, f"Expected {expected}, got {engagement}"
        
        # Test growth rate calculation
        growth = processor.calculate_growth_rate(current_value=110, previous_value=100, days=7)
        expected = 1.4285714285714286  # ((110-100)/100)/7 * 100
        assert abs(growth - expected) < 0.01, f"Expected {expected}, got {growth}"
        
        print("✅ Text processing functions work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Text processing test failed: {str(e)}")
        return False


def test_niche_classification():
    """Test niche classification without ML."""
    try:
        from src.data_processing.niche_classifier import NicheClassifier
        
        # Initialize without ML
        classifier = NicheClassifier(use_ml=False)
        
        # Test fitness classification
        result = classifier.classify(
            text="Amazing workout routine at the gym",
            hashtags=["#fitness", "#gym", "#workout"]
        )
        
        assert result.niche == NicheType.FITNESS, f"Expected FITNESS, got {result.niche}"
        assert result.confidence > 0, "Confidence should be > 0"
        assert result.method_used == "rule_based", "Should use rule-based method"
        
        # Test book classification
        result = classifier.classify(
            text="Love reading books and literature",
            hashtags=["#booktok", "#reading", "#author"]
        )
        
        assert result.niche == NicheType.BOOKTOK, f"Expected BOOKTOK, got {result.niche}"
        
        # Test cooking classification
        result = classifier.classify(
            text="Delicious recipe for homemade pasta",
            hashtags=["#food", "#cooking", "#recipe"]
        )
        
        assert result.niche == NicheType.COOKING, f"Expected COOKING, got {result.niche}"
        
        print("✅ Niche classification works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Niche classification test failed: {str(e)}")
        return False


def test_data_quality():
    """Test data quality assessment."""
    try:
        from src.data_processing.processor import DataProcessor, DataQualityLevel
        
        processor = DataProcessor(enable_ml=False)
        
        # Test good hashtag data
        good_data = {
            "name": "#fitness",
            "usage_count": 1000,
            "engagement": 5.0
        }
        
        quality_level, score = processor.calculate_data_quality_score(good_data, "hashtag")
        assert quality_level in DataQualityLevel, "Should return valid quality level"
        assert 0 <= score <= 100, "Score should be between 0 and 100"
        
        # Test poor hashtag data
        poor_data = {
            "name": "",  # Empty name
            "usage_count": 1,  # Very low usage
            "engagement": 0.01  # Very low engagement
        }
        
        quality_level, score = processor.calculate_data_quality_score(poor_data, "hashtag")
        assert quality_level.value <= 3, "Poor data should get low quality"
        
        print("✅ Data quality assessment works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Data quality test failed: {str(e)}")
        return False


def test_keyword_extraction():
    """Test keyword extraction."""
    try:
        from src.data_processing.processor import DataProcessor
        
        processor = DataProcessor(enable_ml=False)
        
        text = "workout routine fitness gym exercise health"
        keywords = processor.extract_keywords(text, max_keywords=5)
        
        assert len(keywords) > 0, "Should extract some keywords"
        assert "workout" in keywords, "Should include content words"
        
        print("✅ Keyword extraction works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Keyword extraction test failed: {str(e)}")
        return False


def test_hashtag_processing():
    """Test hashtag processing with simple data."""
    try:
        from src.data_processing.processor import DataProcessor
        
        processor = DataProcessor(enable_ml=False)
        
        # Test with simple hashtag data
        raw_hashtags = [
            {
                "name": "#fitness",
                "usage_count": 1000,
                "engagement": 5.0,
                "growth_rate": 10.0,
                "videos": 100,
                "views": 10000,
                "description": "Workout and fitness content"
            }
        ]
        
        processed = processor.process_hashtags(raw_hashtags)
        
        assert len(processed) == 1, "Should process one hashtag"
        hashtag = processed[0]
        
        assert hashtag.name == "#fitness", "Should normalize name correctly"
        assert hashtag.usage_count == 1000, "Should preserve usage count"
        assert hashtag.niche == NicheType.FITNESS, "Should classify as fitness"
        assert hashtag.trend_direction in [TrendDirection.UPWARD, TrendDirection.RISING], f"Should detect upward/rising trend, got {hashtag.trend_direction}"
        assert hashtag.confidence_score > 0, "Should have confidence score"
        
        print("✅ Hashtag processing works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Hashtag processing test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("🚀 Running integration tests for TikTok Global Trends...")
    print()
    
    tests = [
        test_basic_imports,
        test_text_processing,
        test_niche_classification,
        test_data_quality,
        test_keyword_extraction,
        test_hashtag_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The new components are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)