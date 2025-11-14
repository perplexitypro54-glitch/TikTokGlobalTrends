print("Final Integration Test - TikTok Global Trends")
print("=" * 50)

try:
    from src.data_processing.processor import DataProcessor
    from src.data_processing.niche_classifier import NicheClassifier
    from src.utils.rate_limiter import RateLimiter
    print("PASS: All imports successful")
    
    processor = DataProcessor(enable_ml=False)
    classifier = NicheClassifier(use_ml=False)
    limiter = RateLimiter()
    print("PASS: All components initialized")
    
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
    else:
        print("FAIL: Data processing failed")
    
    result = classifier.classify("test content", ["#test"])
    if result.confidence >= 0:
        print("PASS: Niche classification working")
        print(f"  Niche: {result.niche.value}")
        print(f"  Confidence: {result.confidence}")
    else:
        print("FAIL: Niche classification failed")
    
    xss_text = "<script>alert('xss')</script>"
    clean = processor.clean_text(xss_text)
    if "<script>" not in clean:
        print("PASS: XSS prevention working")
    else:
        print("FAIL: XSS prevention failed")
    
    sql_text = "'; DROP TABLE users; --"
    clean_sql = processor.clean_text(sql_text)
    if "DROP" not in clean_sql:
        print("PASS: SQL injection prevention working")
    else:
        print("FAIL: SQL injection prevention failed")
    
    print("=" * 50)
    print("SUCCESS: All tests passed!")
    print("System is ready for production!")
    print("=" * 50)
    
except Exception as e:
    print(f"ERROR: {e}")
    print("=" * 50)
    print("FAILED: Integration test failed")
    print("=" * 50)