import contextlib
import re

import httpx
import pytest

import fca_api


class TestFinancialServicesRegisterApiClientCore:
    @pytest.mark.asyncio
    async def test_client_init_sets_credentials(self, test_api_username, test_api_key):
        test_client = fca_api.raw_api.RawClient(credentials=(test_api_username, test_api_key))
        assert test_client.api_session.headers["ACCEPT"] == "application/json"
        assert test_client.api_session.headers["X-AUTH-EMAIL"] == test_api_username
        assert test_client.api_session.headers["X-AUTH-KEY"] == test_api_key
        assert test_client.api_version == fca_api.const.ApiConstants.API_VERSION.value

    @pytest.mark.asyncio
    async def test_client_init_incorrect(self):
        with pytest.raises(ValueError):
            fca_api.raw_api.RawClient(credentials=None)

        with pytest.raises(ValueError):
            fca_api.raw_api.RawClient(credentials=("only_username",))

    @pytest.mark.asyncio
    async def test_rate_limiter(self, mocker, mock_http_client):
        limiter_enter_mock = mocker.AsyncMock(name="limiter_enter_mock")
        limiter_exit_mock = mocker.AsyncMock(name="limiter_exit_mock")

        @contextlib.asynccontextmanager
        async def limiter_mock():
            await limiter_enter_mock()
            try:
                yield
            finally:
                await limiter_exit_mock()

        test_client = fca_api.raw_api.RawClient(
            credentials=mock_http_client,
            api_limiter=limiter_mock,
        )

        for idx in range(3):
            out = await test_client.get_regulated_markets()
            assert out is not None
            assert limiter_enter_mock.await_count == idx + 1
            assert limiter_exit_mock.await_count == idx + 1

    @pytest.mark.asyncio
    async def test_common_search_empty_resource_name(self, mock_http_client):
        """Test that common_search raises ValueError for empty resource name."""
        test_client = fca_api.raw_api.RawClient(credentials=mock_http_client)

        with pytest.raises(ValueError, match="Resource name must be a non-empty string"):
            await test_client.common_search("", "firm")

    @pytest.mark.asyncio
    async def test_common_search_empty_resource_type(self, mock_http_client):
        """Test that common_search raises ValueError for empty resource type."""
        test_client = fca_api.raw_api.RawClient(credentials=mock_http_client)

        with pytest.raises(ValueError, match="Resource type must be a non-empty string"):
            await test_client.common_search("test", "")

    @pytest.mark.asyncio
    async def test_get_regulated_markets_with_page_raises(self, mock_http_client):
        """Test that get_regulated_markets raises NotImplementedError for pagination."""
        test_client = fca_api.raw_api.RawClient(credentials=mock_http_client)

        with pytest.raises(NotImplementedError, match="Pagination is not supported for regulated markets"):
            await test_client.get_regulated_markets(page=2)

    @pytest.mark.asyncio
    async def test_common_search_success(self, test_client):
        """Test common search success."""
        response = await test_client.common_search("test", "firm")
        assert response is not None

    @pytest.mark.asyncio
    async def test_common_search_raises_on_request_error(self, test_client, mocker):
        mock_api_session_get = mocker.patch.object(test_client._api_session, "get")
        mock_api_session_get.side_effect = httpx.RequestError("test RequestError")

        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.common_search("exceptional resource", "firm")

    @pytest.mark.asyncio
    async def test_common_search_success_2(self, test_client):
        recv_response = await test_client.common_search("hastings direct", "firm")
        assert recv_response.is_success
        assert recv_response.data
        assert len(recv_response.data)
        assert recv_response.fca_api_status == "FSR-API-04-01-00"
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.result_info

        recv_response = await test_client.common_search("non existent firm", "firm")
        assert recv_response.is_success
        assert not recv_response.data
        assert recv_response.fca_api_status == "FSR-API-04-01-11"
        assert recv_response.message == "No search result found"
        assert not recv_response.result_info

        recv_response = await test_client.common_search("mark carney", "individual")
        assert recv_response.is_success
        assert recv_response.data
        assert len(recv_response.data)
        assert recv_response.fca_api_status == "FSR-API-04-01-00"
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.result_info

        recv_response = await test_client.common_search("non existent individual", "individual")
        assert recv_response.is_success
        assert not recv_response.data
        assert recv_response.fca_api_status == "FSR-API-04-01-11"
        assert recv_response.message == "No search result found"
        assert not recv_response.result_info

        recv_response = await test_client.common_search("jupiter asia pacific income", "fund")
        assert recv_response.is_success
        assert recv_response.data
        assert len(recv_response.data)
        assert recv_response.fca_api_status == "FSR-API-04-01-00"
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.result_info

        recv_response = await test_client.common_search("non existent fund", "fund")
        assert recv_response.is_success
        assert not recv_response.data
        assert recv_response.fca_api_status == "FSR-API-04-01-11"
        assert recv_response.message == "No search result found"
        assert not recv_response.result_info

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_regulated_markets(self, test_client):
        recv_response = await test_client.get_regulated_markets()
        assert recv_response.is_success
        assert recv_response.data
        assert len(recv_response.data)
        assert re.match(r"^FSR-API-\d{2}-\d{2}-\d{2}$", recv_response.fca_api_status)
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.result_info
