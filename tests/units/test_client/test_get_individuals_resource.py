import pytest

import fca_api


class TestNutmegFirmDetails:
    @pytest.fixture
    def irn(self) -> str:
        return "BXK69703"  # MrBob Keijzers

    @pytest.mark.asyncio
    async def test_get_irn(self, test_client: fca_api.api.Client, irn: str):
        out = await test_client.get_individual(irn)
        assert out.model_dump(mode="json") == {
            "irn": "BXK69703",
            "full_name": "Bob Keijzers",
            "commonly_used_name": None,
            "disciplinary_history": "https://register.fca.org.uk/services/V0.1/Individuals/BXK69703/DisciplinaryHistory",
            "status": "certified / assessed by firm",
            "current_roles_and_activities": "https://register.fca.org.uk/services/V0.1/Individuals/BXK69703/CF",
        }
