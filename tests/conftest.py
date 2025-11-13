"""
Pytest Configuration and Fixtures

Provides common test configuration and fixtures for all tests.
"""

import pytest


@pytest.fixture
def mock_config():
    """Provide mock configuration for tests."""
    return {
        "TIKTOK_CLIENT_KEY": "test_key",
        "TIKTOK_CLIENT_SECRET": "test_secret",
        "DATABASE_URL": "sqlite:///:memory:",
    }
