import pathlib

import httpx
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


@pytest.fixture
def mock_http_client(mocker):
    mock_client = mocker.create_autospec(httpx.AsyncClient, name="mock-httpx-client")
    mock_client.get.return_value = mock_req = mocker.create_autospec(
        httpx.Response,
        instance=True,
    )
    mock_req.status_code = 200
    mock_req.json.return_value = {"status": "FSR-API-04-01-00", "message": "Ok. Search successful", "Data": [{}]}
    mock_req.extensions = {}
    return mock_client


@pytest_asyncio.fixture
async def test_client(caching_session_subclass, test_api_username, test_api_key, test_resources_path):
    async with caching_session_subclass(
        headers={
            "ACCEPT": "application/json",
            "X-AUTH-EMAIL": test_api_username,
            "X-AUTH-KEY": test_api_key,
        },
        cache_dir=test_resources_path,
        cache_mode="read",
    ) as api_session:
        yield FinancialServicesRegisterApiClient(credentials=api_session)
