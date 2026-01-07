# -- IMPORTS --

# -- 3rd party libraries --
import httpx
import pytest

# -- Internal libraries --
from financial_services_register_api.exc import (
    FinancialServicesRegisterApiRequestException,
)


class TestResourceInfoFunctionality:
    @pytest.mark.asyncio
    async def test_get_resource_info_rejects_invalid_type(self, test_client):
        with pytest.raises(ValueError):
            await test_client._get_resource_info("test_ref_number", "invalid resource type")

    @pytest.mark.asyncio
    async def test_get_resource_info_rejects_invalid_type_with_modifiers(self, test_client):
        with pytest.raises(ValueError):
            await test_client._get_resource_info(
                "test_ref_number",
                "invalid resource type",
                modifiers=(
                    "test_modifier1",
                    "test_modifier2",
                ),
            )

    @pytest.mark.asyncio
    async def test_get_resource_info_raises_on_request_error(self, test_client, mocker):
        mock_api_session_get = mocker.patch(
            "financial_services_register_api.api.FinancialServicesRegisterApiSession.get"
        )
        mock_api_session_get.side_effect = httpx.RequestError("test RequestError")

        with pytest.raises(FinancialServicesRegisterApiRequestException):
            await test_client._get_resource_info("test_frn", "firm")
            await test_client._get_resource_info("test_prn", "fund")
            await test_client._get_resource_info("test_irn", "individual")

    @pytest.mark.asyncio
    async def test_get_resource_info_raises_on_request_error_with_modifiers(self, test_client, mocker):
        mock_api_session_get = mocker.patch(
            "financial_services_register_api.api.FinancialServicesRegisterApiSession.get"
        )
        mock_api_session_get.side_effect = httpx.RequestError("test RequestError")

        with pytest.raises(FinancialServicesRegisterApiRequestException):
            await test_client._get_resource_info(
                "test_frn",
                "firm",
                modifiers=(
                    "test_modifier1",
                    "test_modifier2",
                ),
            )
            await test_client._get_resource_info(
                "test_prn",
                "fund",
                modifiers=(
                    "test_modifier1",
                    "test_modifier2",
                ),
            )
            await test_client._get_resource_info(
                "test_irn",
                "individual",
                modifiers=(
                    "test_modifier1",
                    "test_modifier2",
                ),
            )

    @pytest.mark.asyncio
    async def test_get_firm_resource_info_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited with the FRN 113849
        recv_response = await test_client._get_resource_info("113849", "firm")
        assert recv_response.ok
        assert recv_response.data
        assert recv_response.data[0]["Organisation Name"] == "Hiscox Insurance Company Limited"

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client._get_resource_info("1234567890", "firm")
        assert recv_response.ok
        assert not recv_response.data

        # Test various modifiers for firm resource info
        modifiers_to_test = [
            ("Names",),
            ("Address",),
            ("CF",),
            ("Individuals",),
            ("Permissions",),
            ("Requirements",),
            ("Regulators",),
            ("Passports",),
            ("Waivers",),
            ("Exclusions",),
            ("DisciplinaryHistory",),
            ("AR",),
        ]

        for modifier in modifiers_to_test:
            # Test with existing firm
            recv_response = await test_client._get_resource_info("113849", "firm", modifiers=modifier)
            assert recv_response.ok

            # Test with non-existent firm
            recv_response = await test_client._get_resource_info("1234567890", "firm", modifiers=modifier)
            assert recv_response.ok
            if modifier[0] == "AR":
                # Special case for appointed representatives
                assert not recv_response.data["PreviousAppointedRepresentatives"]
                assert not recv_response.data["CurrentAppointedRepresentatives"]
            else:
                assert not recv_response.data

    @pytest.mark.asyncio
    async def test_get_fund_resource_info_success(self, test_client):
        # Covers the case of a request for an existing fund which is
        # 'Jupiter Asia Pacific Income Fund (IRL)' with the PRN 1006826
        recv_response = await test_client._get_resource_info("1006826", "fund")
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for an non-existent fund given by
        # a non-existent PRN 1234567890
        recv_response = await test_client._get_resource_info("1234567890", "fund")
        assert recv_response.ok
        assert not recv_response.data

        # Test fund modifiers
        fund_modifiers = [("Subfund",), ("Names",)]

        for modifier in fund_modifiers:
            # Test with existing fund
            recv_response = await test_client._get_resource_info("185045", "fund", modifiers=modifier)
            assert recv_response.ok

            # Test with non-existent fund
            recv_response = await test_client._get_resource_info("1234567890", "fund", modifiers=modifier)
            assert recv_response.ok
            assert not recv_response.data

    @pytest.mark.asyncio
    async def test_get_individual_resource_info_success(self, test_client):
        # Covers the case of a request for an existing individual
        # 'Mark Carney'(IRN 'MXC29012')
        recv_response = await test_client._get_resource_info("MXC29012", "individual")
        assert recv_response.ok
        assert recv_response.data
        assert recv_response.data[0]["Details"]["Full Name"] == "Mark Carney"

        # Covers the case of a request for an non-existent individual
        recv_response = await test_client._get_resource_info("1234567890", "individual")
        assert recv_response.ok
        assert not recv_response.data

        # Test individual modifiers
        individual_modifiers = [("CF",), ("DisciplinaryHistory",)]

        for modifier in individual_modifiers:
            # Test with existing individual
            recv_response = await test_client._get_resource_info("MXC29012", "individual", modifiers=modifier)
            assert recv_response.ok

            # Test with non-existent individual
            recv_response = await test_client._get_resource_info("1234567890", "individual", modifiers=modifier)
            assert recv_response.ok
            assert not recv_response.data
