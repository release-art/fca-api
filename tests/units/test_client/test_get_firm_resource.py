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
        assert firm.model_dump(mode="json") == {
            "frn": "552016",
            "name": "J.P. MORGAN PERSONAL INVESTING LIMITED",
            "status": "authorised",
            "type": "regulated",
            "companies_house_number": "07503666",
            "client_money_permission": "hold and control client money",
            "timestamp": "2026-01-14T15:38:00",
            "status_effective_date": "2011-10-06T00:00:00",
            "sub_status": "",
            "sub_status_effective_from": None,
            "mutual_society_number": "",
            "mlrs_status": "",
            "mlrs_status_effective_date": None,
            "e_money_agent_status": "",
            "e_money_agent_effective_date": None,
            "psd_emd_status": "",
            "psd_emd_effective_date": None,
            "psd_agent_status": "",
            "psd_agent_effective_date": None,
            "exceptional_info_details": [],
            "names_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Names",
            "individuals_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Individuals",
            "requirements_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Requirements",
            "permissions_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Permissions",
            "passports_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Passports",
            "regulators_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Regulators",
            "waivers_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Waivers",
            "exclusions_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Exclusions",
            "address_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Address",
            "appointed_representative_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/AR",
            "disciplinary_history_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/DisciplinaryHistory",
        }
