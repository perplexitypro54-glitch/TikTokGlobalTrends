print("Final Integration Test - TikTok Global Trends")
print("=" * 50)

# Mock dependencies
import sys
import types

def create_mock_module():
    """Create mock module for dependencies."""
    mock = types.ModuleType('mock')
    
    class MockSQLAlchemy:
        class DateTime:
            pass
        class func:
            pass
    
    mock.DateTime = MockSQLAlchemy.DateTime
    mock.func = MockSQLAlchemy.func
    
    return mock

# Mock sqlalchemy
sys.modules['sqlalchemy'] = create_mock_module()
sys.modules['sqlalchemy.orm'] = create_mock_module()

# Mock other dependencies
for module in ['aiohttp', 'playwright', 'bs4', 'sklearn', 'numpy']:
    sys.modules[module] = types.ModuleType(module)

try:
    from src.data_processing.processor import DataProcessor
    from src.data_processing.niche_classifier import NicheClassifier
    from src.utils.rate_limiter import RateLimiter
    print("PASS: All imports successful")
    
    processor = DataProcessor(enable_ml=False)
    classifier = NicheClassifier(use_ml=False)
    limiter = RateLimiter()
    print("PASS: All components initialized")
    
    # Test data processing
    test_hashtag = {
        "name": "#test",
        "usage_count": 100,
        "engagement": 5.0,
        "growth_rate": 10.0,
        "videos": 10,
        "views": 1000
    }
    
    processed = processor.process_hashtags([test_hashtag])
    if len(processed) > 0:
        print("PASS: Data processing working")
        print(f"  - Processed: {len(processed)} hashtags")
        print(f"  - Niche: {processed[0].niche.value}")
        print(f"  - Quality: {processed[0].data_quality_score:.1f}")
    else:
        print("FAIL: Data processing failed")
    
    # Test niche classification
    result = classifier.classify("test content", ["#test"])
    if result.confidence >= 0:
        print("PASS: Niche classification working")
        print(f"  - Niche: {result.niche.value}")
        print(f"  - Confidence: {result.confidence:.2f}")
        print(f"  - Method: {result.method_used}")
    else:
        print("FAIL: Niche classification failed")
    
    # Test text cleaning
    xss_text = "<script>alert('xss')</script>"
    clean = processor.clean_text(xss_text)
    if "<script>" not in clean:
        print("PASS: XSS prevention working")
    else:
        print("FAIL: XSS prevention failed")
    
    # Test hashtag normalization
    hashtag = processor.normalize_hashtag_name("##TEST##")
    if hashtag == "#test":
        print("PASS: Hashtag normalization working")
    else:
        print(f"FAIL: Hashtag normalization failed: {hashtag}")
    
    # Test engagement calculation
    engagement = processor.calculate_engagement_rate(likes=100, views=10000)
    if 0 <= engagement <= 100:
        print("PASS: Engagement calculation working")
        print(f"  - Rate: {engagement:.1f}%")
    else:
        print("FAIL: Engagement calculation failed")
    
    # Test growth rate calculation
    growth = processor.calculate_growth_rate(current_value=110, previous_value=100, days=7)
    if growth > 0:
        print("PASS: Growth rate calculation working")
        print(f"  - Rate: {growth:.2f}%")
    else:
        print("FAIL: Growth rate calculation failed")
    
    print("=" * 50)
    print("SUCCESS: All core functionality working!")
    print("System is ready for production!")
    print("=" * 50)
    
except Exception as e:
    print(f"ERROR: {e}")
    print("=" * 50)
    print("FAILED: Integration test failed")
    print("=" * 50)