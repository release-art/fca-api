"""Test get firm resources"""

import pytest

import fca_api


class TestNutmegFirmDetails:
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

    @pytest.mark.asyncio
    async def test_get_firm_names(self, test_client: fca_api.api.Client, frn: str):
        names = await test_client.get_firm_names(frn)
        assert names.model_dump(mode="json") == {
            "current": [
                {
                    "name": "J.P. Morgan Personal Investing",
                    "status": "trading",
                    "effective_from": "2025-11-03T00:00:00",
                },
                {
                    "name": "J.P. MORGAN PERSONAL INVESTING LIMITED",
                    "status": "registered",
                    "effective_from": "2025-11-03T00:00:00",
                },
            ],
            "previous": [
                {
                    "name": "Nutmeg",
                    "status": "trading",
                    "effective_from": "2011-05-24T00:00:00",
                    "effective_to": "2025-11-03T00:00:00",
                },
                {
                    "name": "Nutmeg Saving and Investment Limited",
                    "status": "registered",
                    "effective_from": "2012-05-25T00:00:00",
                    "effective_to": "2025-11-03T00:00:00",
                },
                {
                    "name": "Hungry Finance Limited",
                    "status": "registered",
                    "effective_from": "2011-10-06T00:00:00",
                    "effective_to": "2012-05-25T00:00:00",
                },
            ],
        }
