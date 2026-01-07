"""Mock session module for testing the Financial Services Register API without network requests."""

import pathlib

import pytest

from . import cache_filename, reading, writing


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
def cache_writing_session_subclass():
    return writing.CachingFinancialServicesRegisterApiSession


@pytest.fixture
def cache_reading_session_subclass():
    return reading.MockFinancialServicesRegisterApiSession
