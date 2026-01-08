# -- IMPORTS --
import re

import httpx
import pytest

import fca_api
from fca_api.const import (
    FINANCIAL_SERVICES_REGISTER_API_CONSTANTS as API_CONSTANTS,
)
from fca_api.exc import (
    FinancialServicesRegisterApiRequestError,
)


class TestFinancialServicesRegisterApiClientCore:
    @pytest.mark.asyncio
    async def test_client_init_sets_credentials(self, test_api_username, test_api_key):
        test_client = fca_api.api.FinancialServicesRegisterApiClient(credentials=(test_api_username, test_api_key))
        assert test_client.api_session.headers["ACCEPT"] == "application/json"
        assert test_client.api_session.headers["X-AUTH-EMAIL"] == test_api_username
        assert test_client.api_session.headers["X-AUTH-KEY"] == test_api_key
        assert test_client.api_version == API_CONSTANTS.API_VERSION.value

    @pytest.mark.asyncio
    async def test_client_init_incorrect(self):
        with pytest.raises(ValueError):
            fca_api.api.FinancialServicesRegisterApiClient(credentials=None)

        with pytest.raises(ValueError):
            fca_api.api.FinancialServicesRegisterApiClient(credentials=("only_username",))

    @pytest.mark.asyncio
    async def test_common_search_raises_on_request_error(self, test_client, mocker):
        mock_api_session_get = mocker.patch.object(test_client._api_session, "get")
        mock_api_session_get.side_effect = httpx.RequestError("test RequestError")

        with pytest.raises(FinancialServicesRegisterApiRequestError):
            await test_client.common_search("exceptional resource", "firm")

    @pytest.mark.asyncio
    async def test_common_search_success(self, test_client):
        recv_response = await test_client.common_search("hastings direct", "firm")
        assert recv_response.ok
        assert recv_response.data
        assert len(recv_response.data)
        assert recv_response.status == "FSR-API-04-01-00"
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.resultinfo

        recv_response = await test_client.common_search("non existent firm", "firm")
        assert recv_response.ok
        assert not recv_response.data
        assert recv_response.status == "FSR-API-04-01-11"
        assert recv_response.message == "No search result found"
        assert not recv_response.resultinfo

        recv_response = await test_client.common_search("mark carney", "individual")
        assert recv_response.ok
        assert recv_response.data
        assert len(recv_response.data)
        assert recv_response.status == "FSR-API-04-01-00"
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.resultinfo

        recv_response = await test_client.common_search("non existent individual", "individual")
        assert recv_response.ok
        assert not recv_response.data
        assert recv_response.status == "FSR-API-04-01-11"
        assert recv_response.message == "No search result found"
        assert not recv_response.resultinfo

        recv_response = await test_client.common_search("jupiter asia pacific income", "fund")
        assert recv_response.ok
        assert recv_response.data
        assert len(recv_response.data)
        assert recv_response.status == "FSR-API-04-01-00"
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.resultinfo

        recv_response = await test_client.common_search("non existent fund", "fund")
        assert recv_response.ok
        assert not recv_response.data
        assert recv_response.status == "FSR-API-04-01-11"
        assert recv_response.message == "No search result found"
        assert not recv_response.resultinfo

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_regulated_markets(self, test_client):
        recv_response = await test_client.get_regulated_markets()
        assert recv_response.ok
        assert recv_response.data
        assert len(recv_response.data)
        assert re.match(r"^FSR-API-\d{2}-\d{2}-\d{2}$", recv_response.status)
        assert recv_response.message == "Ok. Search successful"
        assert recv_response.resultinfo
