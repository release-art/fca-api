import httpx
import pytest

import fca_api
from fca_api.exc import (
    FcaRequestError,
)


class TestResourceInfoFunctionality:
    @pytest.mark.asyncio
    async def test_get_resource_info_rejects_invalid_type(self, test_client: fca_api.raw_api.RawClient):
        with pytest.raises(ValueError):
            await test_client._get_resource_info("test_ref_number", "invalid resource type")

    @pytest.mark.asyncio
    async def test_get_resource_info_rejects_invalid_type_with_modifiers(self, test_client: fca_api.raw_api.RawClient):
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
    @pytest.mark.parametrize(
        "resource_ref_number, resource_type", [("test_frn", "firm"), ("test_prn", "fund"), ("test_irn", "individual")]
    )
    async def test_get_resource_info_raises_on_request_error(
        self, test_client, mocker, resource_ref_number, resource_type
    ):
        mocker.patch.object(test_client._api_session, "get", side_effect=httpx.RequestError("test RequestError"))

        with pytest.raises(FcaRequestError):
            await test_client._get_resource_info(resource_ref_number, resource_type)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "resource_ref_number, resource_type", [("test_frn", "firm"), ("test_prn", "fund"), ("test_irn", "individual")]
    )
    async def test_get_resource_info_raises_on_request_error_with_modifiers(
        self, test_client, mocker, resource_ref_number, resource_type
    ):
        mocker.patch.object(test_client._api_session, "get", side_effect=httpx.RequestError("test RequestError"))

        with pytest.raises(FcaRequestError):
            await test_client._get_resource_info(
                resource_ref_number,
                resource_type,
                modifiers=(
                    "test_modifier1",
                    "test_modifier2",
                ),
            )

    @pytest.mark.asyncio
    async def test_get_firm_resource_info_success(self, test_client: fca_api.raw_api.RawClient):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited with the FRN 113849
        recv_response = await test_client._get_resource_info("113849", "firm")
        assert recv_response.is_success
        assert recv_response.data
        assert recv_response.data[0]["Organisation Name"] == "Hiscox Insurance Company Limited"

    @pytest.mark.asyncio
    async def test_get_firm_resource_info_failure(self, test_client: fca_api.raw_api.RawClient):
        # Now expects a successful response with empty data for non-existent firm
        recv_response = await test_client._get_resource_info("1234567890", "firm")
        assert recv_response.is_success
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_resource_info_modifiers_success(self, test_client: fca_api.raw_api.RawClient):
        # Test various modifiers for firm resource info with existing firm
        # Only test modifiers that are expected to succeed for this firm
        modifiers_to_test = [
            ("Names",),
            ("Address",),
            ("CF",),
            ("Individuals",),
            ("Permissions",),
            ("Regulators",),
            ("Passports",),
            ("AR",),
        ]

        for modifier in modifiers_to_test:
            # Test with existing firm
            recv_response = await test_client._get_resource_info("113849", "firm", modifiers=modifier)
            assert recv_response.is_success

    @pytest.mark.asyncio
    async def test_get_firm_resource_info_modifiers_success_requirements(self, test_client: fca_api.raw_api.RawClient):
        # Test requirements modifier that returns data for firm 113849
        recv_response = await test_client._get_resource_info("113849", "firm", modifiers=("Requirements",))
        assert recv_response.is_success
        assert recv_response.data  # This firm actually has requirements data

    @pytest.mark.asyncio
    async def test_get_firm_resource_info_modifiers_success_waivers(self, test_client: fca_api.raw_api.RawClient):
        # Test waivers modifier that returns data for firm 113849
        recv_response = await test_client._get_resource_info("113849", "firm", modifiers=("Waivers",))
        assert recv_response.is_success
        assert recv_response.data  # This firm has waivers data

    @pytest.mark.asyncio
    async def test_get_firm_resource_info_modifiers_no_disciplinary_history(
        self, test_client: fca_api.raw_api.RawClient
    ):
        # Now expects an exception for no disciplinary history (SOQL no record)
        out = await test_client._get_resource_info("113849", "firm", modifiers=("DisciplinaryHistory",))
        assert out.data is None

    @pytest.mark.asyncio
    async def test_get_firm_resource_info_modifiers_failure_exclusions(self, test_client: fca_api.raw_api.RawClient):
        # Now expects a successful response with empty data for no exclusions
        recv_response = await test_client._get_resource_info("113849", "firm", modifiers=("Exclusions",))
        assert recv_response.is_success
        assert not recv_response.data

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "modifier",
        [
            "Names",
            "Address",
            "CF",
            "Individuals",
            "Permissions",
            "Regulators",
            "Passports",
            "Waivers",
            "Exclusions",
            "DisciplinaryHistory",
        ],
    )
    async def test_get_firm_resource_info_modifiers_failure(self, test_client: fca_api.raw_api.RawClient, modifier):
        # Now expects a successful response with empty data for all modifiers on non-existent firm
        recv_response = await test_client._get_resource_info("1234567890", "firm", modifiers=(modifier,))
        assert recv_response.is_success
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_resource_info_ar_modifier_empty_result(self, test_client: fca_api.raw_api.RawClient):
        # Special case for appointed representatives - returns empty but doesn't fail
        recv_response = await test_client._get_resource_info("1234567890", "firm", modifiers=("AR",))
        assert recv_response.is_success
        assert not recv_response.data["PreviousAppointedRepresentatives"]
        assert not recv_response.data["CurrentAppointedRepresentatives"]

    @pytest.mark.asyncio
    async def test_get_fund_resource_info_success(self, test_client: fca_api.raw_api.RawClient):
        # Covers the case of a request for an existing fund which is
        # 'Jupiter Asia Pacific Income Fund (IRL)' with the PRN 1006826
        recv_response = await test_client._get_resource_info("1006826", "fund")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_fund_resource_info_failure(self, test_client: fca_api.raw_api.RawClient):
        # Covers the case of a request for an non-existent fund given by
        # a non-existent PRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client._get_resource_info("1234567890", "fund")

    @pytest.mark.asyncio
    async def test_get_fund_resource_info_modifiers_success(self, test_client: fca_api.raw_api.RawClient):
        # Test fund modifiers with existing fund
        fund_modifiers = [("Subfund",), ("Names",)]

        for modifier in fund_modifiers:
            # Test with existing fund
            recv_response = await test_client._get_resource_info("185045", "fund", modifiers=modifier)
            assert recv_response.is_success

    @pytest.mark.asyncio
    async def test_get_fund_resource_info_modifiers_failure_nonexistent_names(
        self, test_client: fca_api.raw_api.RawClient
    ):
        # Test fund Names modifier with non-existent fund - raises exception
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client._get_resource_info("1234567890", "fund", modifiers=("Names",))

    @pytest.mark.asyncio
    async def test_get_fund_resource_info_modifiers_empty_result_subfund(self, test_client: fca_api.raw_api.RawClient):
        # Test fund Subfund modifier with non-existent fund - returns empty data
        recv_response = await test_client._get_resource_info("1234567890", "fund", modifiers=("Subfund",))
        assert recv_response.is_success
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_get_individual_resource_info_success(self, test_client: fca_api.raw_api.RawClient):
        # Covers the case of a request for an existing individual
        # 'Mark Carney'(IRN 'MXC29012')
        recv_response = await test_client._get_resource_info("MXC29012", "individual")
        assert recv_response.is_success
        assert recv_response.data
        assert recv_response.data[0]["Details"]["Full Name"] == "Mark Carney"

    @pytest.mark.asyncio
    async def test_get_individual_resource_info_not_found(self, test_client: fca_api.raw_api.RawClient):
        # Covers the case of a request for an non-existent individual
        out = await test_client._get_resource_info("1234567890", "individual")
        assert out.data is None

    @pytest.mark.asyncio
    async def test_get_individual_resource_info_modifiers_success(self, test_client: fca_api.raw_api.RawClient):
        # Test individual modifiers with existing individual
        # Only test modifiers that work for Mark Carney
        individual_modifiers = [("CF",)]

        for modifier in individual_modifiers:
            # Test with existing individual
            recv_response = await test_client._get_resource_info("MXC29012", "individual", modifiers=modifier)
            assert recv_response.is_success

    @pytest.mark.asyncio
    @pytest.mark.parametrize("modifier", ["CF", "DisciplinaryHistory"])
    async def test_get_individual_resource_info_modifiers_no_data(
        self, test_client: fca_api.raw_api.RawClient, modifier
    ):
        # Test individual modifiers with non-existent individual
        out = await test_client._get_resource_info("1234567890", "individual", modifiers=(modifier,))
        assert out.data is None
