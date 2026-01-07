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


class TestIndividualMethods:
    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_individual(
        self, test_client
    ):
        # Covers the case of a request for the details of an
        # existing individual, 'Mark Carney' (IRN 'MXC29012')
        recv_response = await test_client.get_individual("MXC29012")
        assert recv_response.ok
        assert recv_response.data
        assert recv_response.data[0]["Details"]["Full Name"] == "Mark Carney"

        # Covers the case of a request for the details of a non-existent individual
        recv_response = await test_client.get_individual("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_individual_controlled_functions(
        self, test_client
    ):
        # Covers the case of a request for an existing individual -
        # 'Mark Carney' (IRN 'MXC29012')
        recv_response = await test_client.get_individual_controlled_functions(
            "MXC29012"
        )
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for an non-existent individual given by
        # a non-existent IRN '1234567890'
        recv_response = await test_client.get_individual_controlled_functions(
            "1234567890"
        )
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_individual_disciplinary_history(
        self, test_client
    ):
        # Covers the case of a request for an existing individual with -
        # disciplinary history, 'Leigh Mackey' (IRN 'LXM01328')
        recv_response = await test_client.get_individual_disciplinary_history(
            "LXM01328"
        )
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for an non-existent individual given by
        # a non-existent IRN '1234567890'
        recv_response = await test_client.get_individual_disciplinary_history(
            "1234567890"
        )
        assert recv_response.ok
        assert not recv_response.data