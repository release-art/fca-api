"""Mock session module for testing the Financial Services Register API without network requests."""

import pytest

from . import cache_filename, caching, mock


@pytest.fixture
def caching_session_subclass():
    return caching.CachingFinancialServicesRegisterApiSession


@pytest.fixture
def mock_session_subclass():
    return mock.MockFinancialServicesRegisterApiSession
