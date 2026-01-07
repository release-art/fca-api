"""Mock session module for testing the Financial Services Register API without network requests."""

import pytest
import pathlib

from . import cache_filename, caching, mock

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_setup(item):
    path_parts = []
    for el in reversed(item.listnames()):
        if el.strip():
            path_parts.insert(0, el)
        if el.lower().endswith(".py"):
            # Stop at the test file name
            break
    
    cache_filename.G_CUR_TEST_PREFIX = pathlib.PurePath(*path_parts)
    yield

@pytest.fixture
def caching_session_subclass():
    return caching.CachingFinancialServicesRegisterApiSession


@pytest.fixture
def mock_session_subclass():
    return mock.MockFinancialServicesRegisterApiSession
