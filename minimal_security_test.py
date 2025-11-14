from src.data_processing.processor import DataProcessor

processor = DataProcessor(enable_ml=False)

# Test XSS prevention
xss_text = '<script>alert("xss")</script>'
clean = processor.clean_text(xss_text)
print("XSS Test:", "PASS" if "<script>" not in clean else "FAIL")

# Test SQL injection prevention
sql_text = "'; DROP TABLE users; --"
clean_sql = processor.clean_text(sql_text)
print("SQLi Test:", "PASS" if "DROP" not in clean_sql else "FAIL")

# Test hashtag normalization
hashtag = processor.normalize_hashtag_name("##FITNESS##")
print("Hashtag Test:", "PASS" if hashtag == "#fitness" else "FAIL")

# Test engagement bounds
engagement = processor.calculate_engagement_rate(likes=100, views=10000)
print("Engagement Test:", "PASS" if 0 <= engagement <= 100 else "FAIL")

print("Security Validation Complete!")