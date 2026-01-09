import pytest

import fca_api


class TestSearchFunctionality:
    @pytest.mark.asyncio
    async def test_common_search_http_error(self, test_client, mock_http_client):
        test_client._api_session = mock_http_client
        mock_http_client.get.return_value.status_code = 500
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.common_search("test resource", "firm")

    @pytest.mark.asyncio
    async def test_common_search_unexpected_message_error(self, test_client, mock_http_client):
        test_client._api_session = mock_http_client
        mock_http_client.get.return_value.json.return_value = {
            "status": "FSR-API-99-99-99",
            "Message": "Hey, I found something!",
            "Data": None,
        }
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.common_search("test resource", "firm")

    @pytest.mark.asyncio
    async def test_common_search_unexpected_data_type(self, test_client, mock_http_client):
        test_client._api_session = mock_http_client
        mock_http_client.get.return_value.json.return_value = {
            "status": "FSR-API-99-99-99",
            "Message": "Hey, I found something!",
            "Data": "this should be a list, not a string",
        }
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.common_search("test resource", "firm")

    @pytest.mark.asyncio
    async def test_search_frn_returns_unique_firm(self, test_client):
        # Covers the case of a successful FRN search for existing, unique firms
        recv_frn = await test_client.search_frn("hiscox insurance company")
        assert recv_frn.data == [
            {
                "Name": "Hiscox Insurance Company Limited (Postcode: EC2N 4BQ)",
                "Reference Number": "113849",
                "Status": "Authorised",
                "Type of business or Individual": "Firm",
                "URL": "https://register.fca.org.uk/services/V0.1/Firm/113849",
            }
        ]

        recv_frn = await test_client.search_frn("hastings insurance services limited")
        assert recv_frn.data == [
            {
                "Name": "Hastings Insurance Services Limited (Postcode: TN39 3LW)",
                "Reference Number": "311492",
                "Status": "Authorised",
                "Type of business or Individual": "Firm",
                "URL": "https://register.fca.org.uk/services/V0.1/Firm/311492",
            }
        ]

        recv_frn = await test_client.search_frn("citibank europe luxembourg")
        assert len(recv_frn.data) == 1

    @pytest.mark.asyncio
    async def test_search_irn_returns_unique_individual(self, test_client):
        # Covers the case of a successful IRN search for existing, unique individuals
        recv_irn1 = await test_client.search_irn("Mark Carney")
        assert recv_irn1.data == [
            {
                "Name": "Mark Carney",
                "Reference Number": "MXC29012",
                "Status": "Active",
                "Type of business or Individual": "Individual",
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/MXC29012",
            }
        ]
        recv_irn2 = await test_client.search_irn("andrew bailey")
        assert recv_irn2.data == [
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
        assert recv_irn3.data == [
            {
                "Name": "Mark Carney",
                "Reference Number": "MXC29012",
                "Status": "Active",
                "Type of business or Individual": "Individual",
                "URL": "https://register.fca.org.uk/services/V0.1/Individuals/MXC29012",
            }
        ]

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
        assert isinstance(recv_prn.data, list)
        assert recv_prn
        assert recv_prn.data[0]

    @pytest.mark.asyncio
    async def test_search_absent_prn(self, test_client):
        # Covers the case of a successful PRN search for existing, unique funds
        res = await test_client.search_prn("non existent fund akjsdhfgkasdhfo")
        assert res.is_success
        assert res.message.lower() == "no search result found"
        assert res.data == []
