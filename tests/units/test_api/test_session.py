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


class TestFinancialServicesRegisterApiSession:
    @pytest.mark.asyncio
    async def test_fs_register_api_session(
        self, test_session, test_api_username, test_api_key
    ):
        assert test_session.api_username == test_api_username
        assert test_session.api_key == test_api_key
        assert test_session.headers == {
            "ACCEPT": "application/json",
            "X-AUTH-EMAIL": test_api_username,
            "X-AUTH-KEY": test_api_key,
        }
