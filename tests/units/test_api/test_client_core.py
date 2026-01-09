# -- IMPORTS --
import contextlib
import re

import httpx
import pytest

import fca_api


class TestFinancialServicesRegisterApiClientCore:
    @pytest.mark.asyncio
    async def test_client_init_sets_credentials(self, test_api_username, test_api_key):
        test_client = fca_api.api.FinancialServicesRegisterApiClient(credentials=(test_api_username, test_api_key))
        assert test_client.api_session.headers["ACCEPT"] == "application/json"
        assert test_client.api_session.headers["X-AUTH-EMAIL"] == test_api_username
        assert test_client.api_session.headers["X-AUTH-KEY"] == test_api_key
        assert test_client.api_version == fca_api.const.ApiConstants.API_VERSION.value

    @pytest.mark.asyncio
    async def test_client_init_incorrect(self):
        with pytest.raises(ValueError):
            fca_api.api.FinancialServicesRegisterApiClient(credentials=None)

        with pytest.raises(ValueError):
            fca_api.api.FinancialServicesRegisterApiClient(credentials=("only_username",))

    @pytest.mark.asyncio
    async def test_rate_limiter(self, mocker):
        limiter_enter_mock = mocker.AsyncMock(name="limiter_enter_mock")
        limiter_exit_mock = mocker.AsyncMock(name="limiter_exit_mock")

        @contextlib.asynccontextmanager
        async def limiter_mock():
            await limiter_enter_mock()
            try:
                yield
            finally:
                await limiter_exit_mock()

        mock_client = mocker.create_autospec(httpx.AsyncClient, name="mock-httpx-client")
        mock_client.get.return_value = mock_req = mocker.create_autospec(
            httpx.Response,
            instance=True,
        )
        mock_req.status_code = 200
        mock_req.json.return_value = {"status": "FSR-API-04-01-00", "message": "Ok. Search successful", "Data": [{}]}
        test_client = fca_api.api.FinancialServicesRegisterApiClient(
            credentials=mock_client,
            api_limiter=limiter_mock,
        )

        for idx in range(3):
            out = await test_client.get_regulated_markets()
            assert out is not None
            assert limiter_enter_mock.await_count == idx + 1
            assert limiter_exit_mock.await_count == idx + 1

        limiter_enter_mock.reset_mock()
        limiter_exit_mock.reset_mock()
        for idx in range(3):
            out = await test_client.common_search("test resource", "firm")
            assert out is not None
            assert limiter_enter_mock.await_count == idx + 1
            assert limiter_exit_mock.await_count == idx + 1

        limiter_enter_mock.reset_mock()
        limiter_exit_mock.reset_mock()
        for idx in range(3):
            out = await test_client._get_resource_info("123", "firm", "sdf")
            assert out is not None
            assert limiter_enter_mock.await_count == idx + 1
            assert limiter_exit_mock.await_count == idx + 1

    @pytest.mark.asyncio
    async def test_common_search_raises_on_request_error(self, test_client, mocker):
        mock_api_session_get = mocker.patch.object(test_client._api_session, "get")
        mock_api_session_get.side_effect = httpx.RequestError("test RequestError")

        with pytest.raises(fca_api.exc.FinancialServicesRegisterApiRequestError):
            await test_client.common_search("exceptional resource", "firm")

    @pytest.mark.asyncio
    async def test_common_search_success(self, test_client):
        recv_response = await test_client.common_search("hastings direct", "firm")
        assert recv_response.is_success
        assert recv_response.data
        assert len(recv_response.data)
        assert recv_response.status == "FSR-API-04-01-00"
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.resultinfo

        recv_response = await test_client.common_search("non existent firm", "firm")
        assert recv_response.is_success
        assert not recv_response.data
        assert recv_response.status == "FSR-API-04-01-11"
        assert recv_response.message == "No search result found"
        assert not recv_response.resultinfo

        recv_response = await test_client.common_search("mark carney", "individual")
        assert recv_response.is_success
        assert recv_response.data
        assert len(recv_response.data)
        assert recv_response.status == "FSR-API-04-01-00"
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.resultinfo

        recv_response = await test_client.common_search("non existent individual", "individual")
        assert recv_response.is_success
        assert not recv_response.data
        assert recv_response.status == "FSR-API-04-01-11"
        assert recv_response.message == "No search result found"
        assert not recv_response.resultinfo

        recv_response = await test_client.common_search("jupiter asia pacific income", "fund")
        assert recv_response.is_success
        assert recv_response.data
        assert len(recv_response.data)
        assert recv_response.status == "FSR-API-04-01-00"
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.resultinfo

        recv_response = await test_client.common_search("non existent fund", "fund")
        assert recv_response.is_success
        assert not recv_response.data
        assert recv_response.status == "FSR-API-04-01-11"
        assert recv_response.message == "No search result found"
        assert not recv_response.resultinfo

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_regulated_markets(self, test_client):
        recv_response = await test_client.get_regulated_markets()
        assert recv_response.is_success
        assert recv_response.data
        assert len(recv_response.data)
        assert re.match(r"^FSR-API-\d{2}-\d{2}-\d{2}$", recv_response.status)
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.resultinfo
