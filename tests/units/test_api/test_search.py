import httpx
import pytest

import fca_api


class TestSearchFunctionality:
    @pytest.mark.asyncio
    async def test_search_ref_number_rejects_invalid_resource_type(self, test_client):
        with pytest.raises(ValueError):
            await test_client._search_ref_number("resource_name", "incorrect_resource_type")

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "resource_name, resource_type",
        [("exceptional search", "firm"), ("exceptional search", "individual"), ("exceptional search", "fund")],
    )
    async def test_search_ref_number_raises_on_request_error(self, test_client, mocker, resource_name, resource_type):
        mocker.patch.object(test_client._api_session, "get", side_effect=httpx.RequestError("test RequestError"))

        with pytest.raises(fca_api.exc.FinancialServicesRegisterApiRequestError):
            await test_client._search_ref_number(resource_name, resource_type)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("resource_type", ["firm", "individual", "fund"])
    async def test_search_raises_on_malformed_response(self, test_client, mocker, resource_type):
        mock_response = mocker.create_autospec(httpx.Response)
        mock_response.json = mocker.MagicMock(
            name="json",
            return_value={"Data": None},
        )
        mock_response.status_code = 200
        mocker.patch.object(
            test_client._api_session,
            "get",
            mocker.AsyncMock(return_value=mock_response),
        )

        assert await test_client._api_session.get() == mock_response

        with pytest.raises(fca_api.exc.FinancialServicesRegisterApiRequestError):
            await test_client._search_ref_number("bad response", resource_type)

    @pytest.mark.asyncio
    async def test_search_ref_number_raises_on_bad_response(self, test_client, mocker):
        mocker.patch(
            "fca_api.api.FinancialServicesRegisterApiClient.common_search",
            return_value=mocker.MagicMock(ok=False),
        )
        with pytest.raises(fca_api.exc.FinancialServicesRegisterApiRequestError):
            await test_client._search_ref_number("exceptional search", "firm")
            await test_client._search_ref_number("exceptional search", "individual")
            await test_client._search_ref_number("exceptional search", "fund")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("resource_type", ["firm", "individual", "fund"])
    async def test_search_raises_on_empty_response(self, test_client, resource_type):
        with pytest.raises(fca_api.exc.FinancialServicesRegisterApiRequestError):
            await test_client._search_ref_number("bad search", resource_type)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("resource_type", ["firm", "individual", "fund"])
    async def test_search_ref_number_raises_on_nonexistent_resource(self, test_client, resource_type):
        # Covers the case of a failed FRN search for an incorrectly specified firm
        with pytest.raises(fca_api.exc.FinancialServicesRegisterApiRequestError):
            await test_client._search_ref_number("nonexistent123 search string potato", resource_type)

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
        assert recv_frn == [
            {
                "Name": "Hiscox Insurance Company Limited (Postcode: EC2N 4BQ)",
                "Reference Number": "113849",
                "Status": "Authorised",
                "Type of business or Individual": "Firm",
                "URL": "https://register.fca.org.uk/services/V0.1/Firm/113849",
            }
        ]

        # Covers the case of a successful IRN search for an existing individual
        recv_irn = await test_client._search_ref_number("mark carney", "individual")
        assert recv_irn == [
            {
                "Name": "Mark Carney",
                "Reference Number": "MXC29012",
                "Status": "Active",
                "Type of business or Individual": "Individual",
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/MXC29012",
            }
        ]

        # Covers the case of a successful PRN search for an existing fund
        recv_prn = await test_client._search_ref_number("jupiter asia pacific income", "fund")
        assert recv_prn == [
            {
                "Name": "Jupiter Asia Pacific Income Fund (IRL)",
                "Reference Number": "1044298",
                "Status": "Recognised",
                "Type of business or Individual": "Collective investment scheme",
                "URL": "https://register.fca.org.uk/services/V0.1/CIS/1044298",
            }
        ]

    @pytest.mark.asyncio
    async def test_search_frn_returns_unique_firm(self, test_client):
        # Covers the case of a successful FRN search for existing, unique firms
        recv_frn = await test_client.search_frn("hiscox insurance company")
        assert recv_frn == [
            {
                "Name": "Hiscox Insurance Company Limited (Postcode: EC2N 4BQ)",
                "Reference Number": "113849",
                "Status": "Authorised",
                "Type of business or Individual": "Firm",
                "URL": "https://register.fca.org.uk/services/V0.1/Firm/113849",
            }
        ]

        recv_frn = await test_client.search_frn("hastings insurance services limited")
        assert recv_frn == [
            {
                "Name": "Hastings Insurance Services Limited (Postcode: TN39 3LW)",
                "Reference Number": "311492",
                "Status": "Authorised",
                "Type of business or Individual": "Firm",
                "URL": "https://register.fca.org.uk/services/V0.1/Firm/311492",
            }
        ]

        recv_frn = await test_client.search_frn("citibank europe luxembourg")
        assert len(recv_frn) == 1

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
    async def test_search_irn_returns_unique_individual(self, test_client):
        # Covers the case of a successful IRN search for existing, unique individuals
        recv_irn1 = await test_client.search_irn("Mark Carney")
        assert recv_irn1 == [
            {
                "Name": "Mark Carney",
                "Reference Number": "MXC29012",
                "Status": "Active",
                "Type of business or Individual": "Individual",
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/MXC29012",
            }
        ]
        recv_irn2 = await test_client.search_irn("andrew bailey")
        assert recv_irn2 == [
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/ANB01051",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "ANB01051",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB04287",
                "Status": "Active",
                "Reference Number": "AXB04287",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB00749",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "AXB00749",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB04075",
                "Status": "Active",
                "Reference Number": "AXB04075",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB03714",
                "Status": "Active",
                "Reference Number": "AXB03714",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB01867",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "AXB01867",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/RAB01358",
                "Status": "Active",
                "Reference Number": "RAB01358",
                "Type of business or Individual": "Individual",
                "Name": "Ross Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/IAB01058",
                "Status": "Active",
                "Reference Number": "IAB01058",
                "Type of business or Individual": "Individual",
                "Name": "Iain Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/ABC01035",
                "Status": "Active",
                "Reference Number": "ABC01035",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey Thomas Cade",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/PAB00141",
                "Status": "Active",
                "Reference Number": "PAB00141",
                "Type of business or Individual": "Individual",
                "Name": "Philip Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/JXB00659",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "JXB00659",
                "Type of business or Individual": "Individual",
                "Name": "James Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/PAB00088",
                "Status": "Active",
                "Reference Number": "PAB00088",
                "Type of business or Individual": "Individual",
                "Name": "Paul Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB00042",
                "Status": "Active",
                "Reference Number": "AXB00042",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Edward Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AJB00150",
                "Status": "Active",
                "Reference Number": "AJB00150",
                "Type of business or Individual": "Individual",
                "Name": "Andrew John Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB00295",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "AXB00295",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Robert Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AJB01550",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "AJB01550",
                "Type of business or Individual": "Individual",
                "Name": "Andrew James Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/RAB01341",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "RAB01341",
                "Type of business or Individual": "Individual",
                "Name": "Robert Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AJB01267",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "AJB01267",
                "Type of business or Individual": "Individual",
                "Name": "Andrew John Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/ALB01128",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "ALB01128",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Leslie Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/SAB01342",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "SAB01342",
                "Type of business or Individual": "Individual",
                "Name": "Sean Andrew Bailey",
            },
        ]
        recv_irn3 = await test_client.search_irn("MXC29012")
        assert recv_irn2 == [
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/ANB01051",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "ANB01051",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB04287",
                "Status": "Active",
                "Reference Number": "AXB04287",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB00749",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "AXB00749",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB04075",
                "Status": "Active",
                "Reference Number": "AXB04075",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB03714",
                "Status": "Active",
                "Reference Number": "AXB03714",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB01867",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "AXB01867",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/RAB01358",
                "Status": "Active",
                "Reference Number": "RAB01358",
                "Type of business or Individual": "Individual",
                "Name": "Ross Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/IAB01058",
                "Status": "Active",
                "Reference Number": "IAB01058",
                "Type of business or Individual": "Individual",
                "Name": "Iain Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/ABC01035",
                "Status": "Active",
                "Reference Number": "ABC01035",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Bailey Thomas Cade",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/PAB00141",
                "Status": "Active",
                "Reference Number": "PAB00141",
                "Type of business or Individual": "Individual",
                "Name": "Philip Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/JXB00659",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "JXB00659",
                "Type of business or Individual": "Individual",
                "Name": "James Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/PAB00088",
                "Status": "Active",
                "Reference Number": "PAB00088",
                "Type of business or Individual": "Individual",
                "Name": "Paul Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB00042",
                "Status": "Active",
                "Reference Number": "AXB00042",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Edward Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AJB00150",
                "Status": "Active",
                "Reference Number": "AJB00150",
                "Type of business or Individual": "Individual",
                "Name": "Andrew John Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AXB00295",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "AXB00295",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Robert Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AJB01550",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "AJB01550",
                "Type of business or Individual": "Individual",
                "Name": "Andrew James Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/RAB01341",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "RAB01341",
                "Type of business or Individual": "Individual",
                "Name": "Robert Andrew Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/AJB01267",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "AJB01267",
                "Type of business or Individual": "Individual",
                "Name": "Andrew John Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/ALB01128",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "ALB01128",
                "Type of business or Individual": "Individual",
                "Name": "Andrew Leslie Bailey",
            },
            {
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/SAB01342",
                "Status": "Regulatory approval no longer required",
                "Reference Number": "SAB01342",
                "Type of business or Individual": "Individual",
                "Name": "Sean Andrew Bailey",
            },
        ]

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
        assert isinstance(recv_prn, list)
        assert recv_prn
        assert recv_prn[0]

    @pytest.mark.asyncio
    async def test_search_absent_prn(self, test_client):
        # Covers the case of a successful PRN search for existing, unique funds
        with pytest.raises(fca_api.exc.FinancialServicesRegisterApiRequestError):
            await test_client.search_prn("non existent fund akjsdhfgkasdhfo")

    @pytest.mark.asyncio
    async def test_search_prn_returns_multiple_funds(self, test_client):
        # Covers the case of an PRN search based on an inadequately specified fund
        # that produces multiple results
        recv_recs = await test_client._search_ref_number("jupiter", "fund")
        assert isinstance(recv_recs, list)
        assert all(isinstance(rec, dict) for rec in recv_recs)
