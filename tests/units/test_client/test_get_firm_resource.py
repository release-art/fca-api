"""Test get firm resources"""

import pytest

import fca_api


class TestFirmDetails:
    @pytest.fixture
    def frn(self) -> str:
        return "552016"  # Nutmeg / J.P. Morgan Personal Investing FRN

    @pytest.mark.asyncio
    async def test_get_firm(self, test_client: fca_api.api.Client, frn: str):
        firm = await test_client.get_firm(frn)
        print(firm.model_dump(mode="python"))
        1 / 0
        assert firm.frn == frn
        assert firm.name == "J.P. MORGAN PERSONAL INVESTING LIMITED"
        assert firm.status == "Authorised"
