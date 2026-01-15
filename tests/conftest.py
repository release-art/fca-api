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


@pytest.fixture(autouse=True)
def _raise_on_extra_settings_override(monkeypatch):
    """Fixture to override the global model settings to 'forbid' during tests."""
    import fca_api

    monkeypatch.setattr(fca_api.types.settings, "model_validate_extra", "forbid")
    yield
