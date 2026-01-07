import pytest

from financial_services_register_api.api import (
    FinancialServicesRegisterApiSession,
    FinancialServicesRegisterApiClient,
)


@pytest.fixture
async def test_session(test_api_username, test_api_key):
    session = FinancialServicesRegisterApiSession(test_api_username, test_api_key)
    yield session
    await session.aclose()


@pytest.fixture
async def test_client(test_api_username, test_api_key):
    client = FinancialServicesRegisterApiClient(test_api_username, test_api_key)
    yield client
    await client.api_session.aclose()
