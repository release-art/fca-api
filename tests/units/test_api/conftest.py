import pytest
import pathlib
import pytest_asyncio

from financial_services_register_api.api import (
    FinancialServicesRegisterApiSession,
    FinancialServicesRegisterApiClient,
)


@pytest.fixture
def test_resources_path() -> pathlib.Path:
    out = pathlib.Path(__file__).parent / "resources"
    assert out.is_dir(), f"Test resources path does not exist: {out}"
    return out.resolve()


@pytest_asyncio.fixture
async def test_session(test_api_username, test_api_key):
    session = FinancialServicesRegisterApiSession(test_api_username, test_api_key)
    yield session
    await session.aclose()


@pytest_asyncio.fixture
async def test_client(test_api_username, test_api_key):
    client = FinancialServicesRegisterApiClient(test_api_username, test_api_key)
    yield client
    await client.api_session.aclose()
