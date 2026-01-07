# -- IMPORTS --

# -- Standard libraries --
import os
import unittest.mock as mock

# -- 3rd party libraries --
import pytest
import httpx

# -- Internal libraries --
from financial_services_register_api.constants import (
    FINANCIAL_SERVICES_REGISTER_API_CONSTANTS as API_CONSTANTS,
)
from financial_services_register_api.exceptions import (
    FinancialServicesRegisterApiRequestException,
    FinancialServicesRegisterApiResponseException,
)


class TestFinancialServicesRegisterApiClientCore:
    @pytest.mark.asyncio
    async def test_financial_services_register_api_client____init__(
        self, test_client, test_api_username, test_api_key
    ):
        assert test_client.api_session.api_username == test_api_username
        assert test_client.api_session.api_key == test_api_key
        assert test_client.api_session.headers == {
            "ACCEPT": "application/json",
            "X-AUTH-EMAIL": test_api_username,
            "X-AUTH-KEY": test_api_key,
        }
        assert test_client.api_version == API_CONSTANTS.API_VERSION.value

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__common_search__api_request_exception_raised(
        self, test_client
    ):
        with mock.patch(
            "financial_services_register_api.api.FinancialServicesRegisterApiSession.get"
        ) as mock_api_session_get:
            mock_api_session_get.side_effect = httpx.RequestError("test RequestError")

            with pytest.raises(FinancialServicesRegisterApiRequestException):
                await test_client.common_search("exceptional resource", "firm")

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__common_search__no_api_request_exception(
        self, test_client
    ):
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

        recv_response = await test_client.common_search(
            "non existent individual", "individual"
        )
        assert recv_response.ok
        assert not recv_response.data
        assert recv_response.status == "FSR-API-04-01-11"
        assert recv_response.message == "No search result found"
        assert not recv_response.resultinfo

        recv_response = await test_client.common_search(
            "jupiter asia pacific income", "fund"
        )
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
    async def test_financial_services_register_api_client__get_regulated_markets(
        self, test_client
    ):
        recv_response = await test_client.get_regulated_markets()
        assert recv_response.ok
        assert recv_response.data
        assert len(recv_response.data)
        assert recv_response.status == "FSR-API-01-01-00"
        assert recv_response.message == "Ok. List of regulated markets"
        assert not recv_response.resultinfo
