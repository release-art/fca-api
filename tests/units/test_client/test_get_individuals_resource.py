import unittest.mock

import pytest

import fca_api


class TestNutmegFirmDetails:
    @pytest.fixture
    def irn(self) -> str:
        return "BXK69703"  # MrBob Keijzers

    @pytest.mark.asyncio
    async def test_get_irn(self, test_client: fca_api.async_api.Client, irn: str):
        out = await test_client.get_individual(irn)
        assert out.model_dump(mode="json") == {
            "irn": "BXK69703",
            "full_name": "Bob Keijzers",
            "commonly_used_name": None,
            "disciplinary_history": "https://register.fca.org.uk/services/V0.1/Individuals/BXK69703/DisciplinaryHistory",
            "status": "certified / assessed by firm",
            "current_roles_and_activities": "https://register.fca.org.uk/services/V0.1/Individuals/BXK69703/CF",
        }

    @pytest.mark.asyncio
    async def test_get_individual_details(self, test_client: fca_api.async_api.Client):
        out = await test_client.get_individual("RBS01054")
        assert out.model_dump(mode="json") == {
            "irn": "RBS01054",
            "full_name": "Bob Seaman",
            "commonly_used_name": "Bob",
            "disciplinary_history": "https://register.fca.org.uk/services/V0.1/Individuals/RBS01054/DisciplinaryHistory",
            "status": "regulatory approval no longer required",
            "current_roles_and_activities": "https://register.fca.org.uk/services/V0.1/Individuals/RBS01054/CF",
        }

    @pytest.mark.asyncio
    async def test_get_individual_controlled_functions(self, test_client: fca_api.async_api.Client, irn: str):
        out = await test_client.get_individual_controlled_functions(irn, result_count=100)
        assert [item.model_dump(mode="json") for item in out.data] == [
            {
                "type": "current",
                "name": "[FCA CF] Client dealing",
                "restriction": None,
                "restriction_start_date": None,
                "restriction_end_date": None,
                "customer_engagement_method": "",
                "effective_date": "2025-09-02T00:00:00",
                "firm_name": "Barclays Bank Plc",
                "end_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Firm/122702",
            },
            {
                "type": "current",
                "name": "[FCA CF] Client dealing",
                "restriction": None,
                "restriction_start_date": None,
                "restriction_end_date": None,
                "customer_engagement_method": "",
                "effective_date": "2025-09-02T00:00:00",
                "firm_name": "Barclays Capital Securities Limited",
                "end_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Firm/124431",
            },
            {
                "type": "previous",
                "name": "[FCA CF] Client dealing",
                "restriction": None,
                "restriction_start_date": None,
                "restriction_end_date": None,
                "customer_engagement_method": "",
                "effective_date": "2020-02-10T00:00:00",
                "firm_name": "Barclays Bank Plc",
                "end_date": "2025-02-11T00:00:00",
                "url": "https://register.fca.org.uk/services/V0.1/Firm/122702",
            },
            {
                "type": "previous",
                "name": "[FCA CF] Client dealing",
                "restriction": None,
                "restriction_start_date": None,
                "restriction_end_date": None,
                "customer_engagement_method": "",
                "effective_date": "2020-02-10T00:00:00",
                "firm_name": "Barclays Capital Securities Limited",
                "end_date": "2025-02-11T00:00:00",
                "url": "https://register.fca.org.uk/services/V0.1/Firm/124431",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_individual_controlled_functions_2(self, test_client: fca_api.async_api.Client, irn: str):
        out = await test_client.get_individual_disciplinary_history(irn, result_count=100)
        assert len(out.data) == 0

    @pytest.mark.asyncio
    async def test_get_individual_controlled_functions_3(self, test_client: fca_api.async_api.Client):
        # Neil Dwane - prohibited from performing regulated activities
        #  https://register.fca.org.uk/s/individual?id=003b000000LUiF4AAL
        out = await test_client.get_individual_disciplinary_history("NPD01015", result_count=100)
        assert len(out.data) == 1
        assert [item.model_dump(mode="json") for item in out.data] == [
            {
                "type_of_action": "prohibition",
                "enforcement_type": "fsma",
                "type_of_description": unittest.mock.ANY,
                "action_effective_from": "2025-10-23T00:00:00",
            }
        ]
