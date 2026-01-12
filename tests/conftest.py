import os

import pytest

pytest_plugins = [
    "test_plugins.mock_session",
]


@pytest.fixture
def test_api_username():
    return os.getenv("FCA_API_USERNAME", "test_api_user@example.com")


@pytest.fixture
def test_api_key():
    return os.getenv("FCA_API_KEY", "mock-test-key")
