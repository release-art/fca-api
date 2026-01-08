import pathlib

import pytest
import pytest_asyncio

from fca_api.api import (
    FinancialServicesRegisterApiClient,
)


@pytest.fixture
def test_resources_path() -> pathlib.Path:
    out = pathlib.Path(__file__).parent / "resources"
    assert out.is_dir(), f"Test resources path does not exist: {out}"
    return out.resolve()

@pytest_asyncio.fixture
async def test_client(caching_session_subclass, test_api_username, test_api_key, test_resources_path):
    async with caching_session_subclass(
        headers={
            "ACCEPT": "application/json",
            "X-AUTH-EMAIL": test_api_username,
            "X-AUTH-KEY": test_api_key,
        },
        cache_dir=test_resources_path
    ) as api_session:
        yield FinancialServicesRegisterApiClient(
            credentials=api_session
        )


# @pytest_asyncio.fixture
# async def test_client(test_api_username, test_api_key, cache_writing_session_subclass, test_resources_path):
#     client = FinancialServicesRegisterApiClient(
#         cache_writing_session_subclass(test_api_username, test_api_key, cache_dir=test_resources_path)
#     )
#     yield client
#     await client.api_session.aclose()
