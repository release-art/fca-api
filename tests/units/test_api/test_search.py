# -- IMPORTS --

# -- 3rd party libraries --
import httpx
import pytest

# -- Internal libraries --
from financial_services_register_api.exceptions import (
    FinancialServicesRegisterApiRequestException,
    FinancialServicesRegisterApiResponseException,
)


class TestSearchFunctionality:
    @pytest.mark.asyncio
    async def test_search_ref_number_rejects_invalid_resource_type(self, test_client):
        with pytest.raises(ValueError):
            await test_client._search_ref_number("resource_name", "incorrect_resource_type")

    @pytest.mark.asyncio
    async def test_search_ref_number_raises_on_request_error(self, test_client, mocker):
        mock_api_session_get = mocker.patch(
            "financial_services_register_api.api.FinancialServicesRegisterApiSession.get"
        )
        mock_api_session_get.side_effect = httpx.RequestError("test RequestError")

        with pytest.raises(FinancialServicesRegisterApiRequestException):
            await test_client._search_ref_number("exceptional search", "firm")
            await test_client._search_ref_number("exceptional search", "individual")
            await test_client._search_ref_number("exceptional search", "fund")

    @pytest.mark.asyncio
    async def test_search_ref_number_raises_on_bad_response(self, test_client, mocker):
        mocker.patch(
            "financial_services_register_api.api.FinancialServicesRegisterApiClient.common_search",
            return_value=mocker.MagicMock(ok=False),
        )
        with pytest.raises(FinancialServicesRegisterApiRequestException):
            await test_client._search_ref_number("exceptional search", "firm")
            await test_client._search_ref_number("exceptional search", "individual")
            await test_client._search_ref_number("exceptional search", "fund")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("resource_type", ["firm", "individual", "fund"])
    async def test_financial_services_register_api_client___search_ref_number__no_fs_register_data_in_response__api_request_exception_raised(
        self, test_client, resource_type
    ):
        with pytest.raises(FinancialServicesRegisterApiRequestException):
            await test_client._search_ref_number("bad search", resource_type)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("resource_type", ["firm", "individual", "fund"])
    async def test_financial_services_register_api_client___search_ref_number__fs_register_data_with_key_error__api_request_exception_raised(
        self, test_client, mocker, resource_type
    ):
        # mock_api_session_get = mocker.patch.object(
        #     test_client._api_session, "get"
        # )
        mock_response = mocker.create_autospec(httpx.Response)
        mock_response.json = mocker.MagicMock(
            name="json",
            return_value={"Data": [{"not a Reference Number": None}]},
        )
        mock_response.status_code = 200
        # mock_api_session_get = mocker.AsyncMock(return_value=mock_response)
        mocker.patch.object(
            test_client._api_session,
            "get",
            mocker.AsyncMock(return_value=mock_response),
        )

        assert await test_client._api_session.get() == mock_response

        with pytest.raises(FinancialServicesRegisterApiResponseException):
            await test_client._search_ref_number("bad response", resource_type)

    @pytest.mark.asyncio
    async def test_search_ref_number_raises_on_nonexistent_resource(self, test_client):
        # Covers the case of a failed FRN search for an incorrectly specified firm
        with pytest.raises(FinancialServicesRegisterApiRequestException):
            await test_client._search_ref_number("nonexistent123 insurance company", "firm")

        # Covers the case of a failed IRN search for an incorrectly specified individual
        with pytest.raises(FinancialServicesRegisterApiRequestException):
            await test_client._search_ref_number("a nonexistent individual", "individual")

        # Covers the case of a failed PRN search for an incorrectly specified firm
        with pytest.raises(FinancialServicesRegisterApiRequestException):
            await test_client._search_ref_number("a nonexistent fund", "fund")

    @pytest.mark.asyncio
    async def test_search_ref_number_returns_multiple_matches(self, test_client):
        # Covers the case of an FRN search based on an inadequately specified firm
        # that produces multiple results
        recv_recs = await test_client._search_ref_number("direct line", "firm")
        assert isinstance(recv_recs, list)
        assert all(isinstance(rec, dict) for rec in recv_recs)

        # Covers the case of an IRN search based on an inadequately specified individual
        # that produces multiple results
        recv_recs = await test_client._search_ref_number("john smith", "individual")
        assert isinstance(recv_recs, list)
        assert all(isinstance(rec, dict) for rec in recv_recs)

        # Covers the case of an PRN search based on an inadequately specified firm
        # that produces multiple results
        recv_recs = await test_client._search_ref_number("jupiter", "fund")
        assert isinstance(recv_recs, list)
        assert all(isinstance(rec, dict) for rec in recv_recs)

    @pytest.mark.asyncio
    async def test_search_ref_number_returns_unique_match(self, test_client):
        # Covers the case of a successful FRN search for an existing firm
        recv_frn = await test_client._search_ref_number("hiscox insurance company", "firm")
        assert isinstance(recv_frn, str)
        assert recv_frn

        # Covers the case of a successful IRN search for an existing individual
        recv_irn = await test_client._search_ref_number("mark carney", "individual")
        assert isinstance(recv_irn, str)
        assert recv_irn

        # Covers the case of a successful PRN search for an existing fund
        recv_prn = await test_client._search_ref_number("jupiter asia pacific income", "fund")
        assert isinstance(recv_prn, str)
        assert recv_prn

    @pytest.mark.asyncio
    async def test_search_frn_returns_unique_firm(self, test_client):
        # Covers the case of a successful FRN search for existing, unique firms
        recv_frn = await test_client.search_frn("hiscox insurance company")
        assert isinstance(recv_frn, str)
        assert recv_frn

        recv_frn = await test_client.search_frn("hastings insurance services limited")
        assert isinstance(recv_frn, str)
        assert recv_frn

        recv_frn = await test_client.search_frn("citibank europe luxembourg")
        assert isinstance(recv_frn, str)
        assert recv_frn

    @pytest.mark.asyncio
    async def test_search_frn_returns_multiple_firms(self, test_client):
        # Covers the case of a successful FRN search for existing, unique firms
        recv_recs = await test_client._search_ref_number("hsbc", "firm")
        assert isinstance(recv_recs, list)
        assert all(isinstance(rec, dict) for rec in recv_recs)

        recv_recs = await test_client._search_ref_number("northern", "firm")
        assert isinstance(recv_recs, list)
        assert all(isinstance(rec, dict) for rec in recv_recs)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "search_value, return_type",
        [
            ("Mark Carney", str),
            ("andrew bailey", list),
            ("MXC29012", str),
        ],
    )
    async def test_search_irn_returns_unique_individual(self, test_client, search_value, return_type):
        # Covers the case of a successful IRN search for existing, unique individuals
        recv_irn = await test_client.search_irn(search_value)
        print(recv_irn)
        assert isinstance(recv_irn, return_type)
        assert recv_irn

    @pytest.mark.asyncio
    async def test_search_irn_returns_multiple_individuals(self, test_client):
        # Covers the case of an IRN search based on an inadequately specified individual
        # that produces multiple results
        recv_recs = await test_client._search_ref_number("john smith", "individual")
        assert isinstance(recv_recs, list)
        assert all(isinstance(rec, dict) for rec in recv_recs)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "search_value",
        [
            "jupiter asia pacific income",
            "abrdn ACS I",
        ],
    )
    async def test_search_prn_returns_unique_fund(self, test_client, search_value):
        # Covers the case of a successful PRN search for existing, unique funds
        recv_prn = await test_client.search_prn(search_value)
        assert isinstance(recv_prn, str)
        assert recv_prn

    @pytest.mark.asyncio
    async def test_search_absent_prn(self, test_client):
        # Covers the case of a successful PRN search for existing, unique funds
        with pytest.raises(FinancialServicesRegisterApiRequestException):
            await test_client.search_prn("non existent fund akjsdhfgkasdhfo")

    @pytest.mark.asyncio
    async def test_search_prn_returns_multiple_funds(self, test_client):
        # Covers the case of an PRN search based on an inadequately specified fund
        # that produces multiple results
        recv_recs = await test_client._search_ref_number("jupiter", "fund")
        assert isinstance(recv_recs, list)
        assert all(isinstance(rec, dict) for rec in recv_recs)
