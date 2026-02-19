import pytest
import pytest_asyncio

import fca_api.async_api


class DummyRawClient:
    def __init__(self):
        self.closed = False
        self.close_calls = 0
        self.api_session = self
        self.api_version = "v1"

    async def aclose(self):
        self.closed = True
        self.close_calls += 1


@pytest_asyncio.fixture
def dummy_client():
    # Patch the Client to use DummyRawClient
    orig_raw_client = fca_api.async_api.raw_api.RawClient
    fca_api.async_api.raw_api.RawClient = lambda *args, **kwargs: DummyRawClient()
    client = fca_api.async_api.Client(credentials=("user", "key"))
    yield client
    fca_api.async_api.raw_api.RawClient = orig_raw_client


@pytest.mark.asyncio
async def test_aclose_only_on_outermost_exit(dummy_client):
    """Test that aclose() is only called on the outermost context exit."""
    client = dummy_client
    # Enter nested contexts
    async with client:
        async with client:
            async with client:
                assert not client._client.closed
    # After all contexts exit, aclose should be called once
    assert client._client.closed
    assert client._client.close_calls == 1


@pytest.mark.asyncio
async def test_aclose_manual(dummy_client):
    """Test that manual aclose() works and is idempotent."""
    client = dummy_client
    await client.aclose()
    assert client._client.closed
    assert client._client.close_calls == 1
    # Calling again should increment close_calls
    await client.aclose()
    assert client._client.close_calls == 2
