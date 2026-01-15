"""Test get firm resources"""

import unittest

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
            "timestamp": unittest.mock.ANY,
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
        assert names.model_dump(mode="json") == [
            {
                "name": "J.P. Morgan Personal Investing",
                "type": "current",
                "status": "trading",
                "effective_from": "2025-11-03T00:00:00",
                "effective_to": None,
            },
            {
                "name": "J.P. MORGAN PERSONAL INVESTING LIMITED",
                "type": "current",
                "status": "registered",
                "effective_from": "2025-11-03T00:00:00",
                "effective_to": None,
            },
            {
                "name": "Nutmeg",
                "type": "previous",
                "status": "trading",
                "effective_from": "2011-05-24T00:00:00",
                "effective_to": "2025-11-03T00:00:00",
            },
            {
                "name": "Nutmeg Saving and Investment Limited",
                "type": "previous",
                "status": "registered",
                "effective_from": "2012-05-25T00:00:00",
                "effective_to": "2025-11-03T00:00:00",
            },
            {
                "name": "Hungry Finance Limited",
                "type": "previous",
                "status": "registered",
                "effective_from": "2011-10-06T00:00:00",
                "effective_to": "2012-05-25T00:00:00",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_firm_addresses(self, test_client: fca_api.api.Client, frn: str):
        addresses = await test_client.get_firm_addresses(frn)
        assert addresses.model_dump(mode="json") == [
            {
                "type": "principal place of business",
                "phone_number": "+442035981515",
                "address_lines": ["25 Bank Street"],
                "town": "london",
                "postcode": "E14 5JP",
                "county": "",
                "country": "united kingdom",
                "website": "https://www.personalinvesting.jpmorgan.com/",
                "individual": None,
                "address_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Address?Type=PPOB",
            },
            {
                "type": "complaints contact",
                "phone_number": "+442035981515",
                "address_lines": ["25 Bank Street"],
                "town": "london",
                "postcode": "E14 5JP",
                "county": "",
                "country": "united kingdom",
                "website": None,
                "individual": "Anders Fries",
                "address_url": "https://register.fca.org.uk/services/V0.1/Firm/552016/Address?Type=Complaint",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_firm_cf(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_controlled_functions(frn)
        assert out.model_dump(mode="json") == [
            {
                "type": "current",
                "name": "[FCA CF] Functions requiring qualifications",
                "effective_date": "2025-07-08T00:00:00",
                "end_date": None,
                "individual_name": "Karine Sweeney",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/SXK02084",
            },
            {
                "type": "current",
                "name": "[FCA CF] CASS oversight function",
                "effective_date": "2025-07-08T00:00:00",
                "end_date": None,
                "individual_name": "Karine Sweeney",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/SXK02084",
            },
            {
                "type": "current",
                "name": "SMF9 Chair of the Governing Body",
                "effective_date": "2022-03-11T00:00:00",
                "end_date": None,
                "individual_name": "Clive Peter Adamson",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/CPA01034",
            },
            {
                "type": "current",
                "name": "Director of firm who is not a certification employee or a SMF manager",
                "effective_date": "2021-09-24T00:00:00",
                "end_date": None,
                "individual_name": "Clive Peter Adamson",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/CPA01034",
            },
            {
                "type": "current",
                "name": "[FCA CF] Material risk taker",
                "effective_date": "2026-01-07T00:00:00",
                "end_date": None,
                "individual_name": "Eileen O'Connell",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/EXO00003",
            },
            {
                "type": "current",
                "name": "SMF3 Executive Director",
                "effective_date": "2022-03-15T00:00:00",
                "end_date": None,
                "individual_name": "Matthew Paul Melling",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/MPM01145",
            },
            {
                "type": "current",
                "name": "SMF17 Money Laundering Reporting Officer (MLRO)",
                "effective_date": "2024-06-24T00:00:00",
                "end_date": None,
                "individual_name": "Joanne Helen Phizacklea",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/JXP00417",
            },
            {
                "type": "current",
                "name": "SMF3 Executive Director",
                "effective_date": "2024-05-09T00:00:00",
                "end_date": None,
                "individual_name": "Matthew Gatrell",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/MXG02692",
            },
            {
                "type": "current",
                "name": "SMF1 Chief Executive",
                "effective_date": "2024-05-09T00:00:00",
                "end_date": None,
                "individual_name": "Matthew Gatrell",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/MXG02692",
            },
            {
                "type": "current",
                "name": "SMF16 Compliance Oversight",
                "effective_date": "2024-06-18T00:00:00",
                "end_date": None,
                "individual_name": "Robert George Rule",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/RXR00422",
            },
            {
                "type": "previous",
                "name": "[FCA CF] Significant management",
                "effective_date": "2021-10-05T00:00:00",
                "end_date": "2024-05-09T00:00:00",
                "individual_name": "Matthew Gatrell",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/MXG02692",
            },
            {
                "type": "previous",
                "name": "SMF3 Executive Director",
                "effective_date": "2019-12-09T00:00:00",
                "end_date": "2022-04-30T00:00:00",
                "individual_name": "Neil Ross Alexander",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/NRA01042",
            },
            {
                "type": "previous",
                "name": "SMF1 Chief Executive",
                "effective_date": "2020-03-26T00:00:00",
                "end_date": "2022-04-30T00:00:00",
                "individual_name": "Neil Ross Alexander",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/NRA01042",
            },
            {
                "type": "previous",
                "name": "CF28 Systems and controls",
                "effective_date": "2018-06-14T00:00:00",
                "end_date": "2019-12-08T00:00:00",
                "individual_name": "Neil Ross Alexander",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/NRA01042",
            },
            {
                "type": "previous",
                "name": "CF1 Director",
                "effective_date": "2018-06-14T00:00:00",
                "end_date": "2019-12-08T00:00:00",
                "individual_name": "Neil Ross Alexander",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/NRA01042",
            },
            {
                "type": "previous",
                "name": "CF2 Non Executive Director",
                "effective_date": "2014-02-14T00:00:00",
                "end_date": "2019-12-08T00:00:00",
                "individual_name": "Stephen Clark",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/SXC01299",
            },
            {
                "type": "previous",
                "name": "Director of firm who is not a certification employee or a SMF manager",
                "effective_date": "2020-04-30T00:00:00",
                "end_date": "2021-09-24T00:00:00",
                "individual_name": "Stephen Clark",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/SXC01299",
            },
            {
                "type": "previous",
                "name": "[FCA CF] Manager of certification employee",
                "effective_date": "2022-08-09T00:00:00",
                "end_date": "2024-03-13T00:00:00",
                "individual_name": "Alexa Collinson",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/AJC34316",
            },
            {
                "type": "previous",
                "name": "CF3 Chief Executive",
                "effective_date": "2013-10-15T00:00:00",
                "end_date": "2016-04-18T00:00:00",
                "individual_name": "Lee Cowles",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/LXC01588",
            },
            {
                "type": "previous",
                "name": "CF1 Director",
                "effective_date": "2013-02-20T00:00:00",
                "end_date": "2016-04-18T00:00:00",
                "individual_name": "Lee Cowles",
                "restriction": None,
                "restriction_end_date": None,
                "restriction_start_date": None,
                "url": "https://register.fca.org.uk/services/V0.1/Individuals/LXC01588",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_firm_individuals(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_individuals(frn)
        await out.fetch_all_pages()
        assert len(out) >= 120
        assert out.model_dump(mode="json")[0] == {
            "irn": "RXR00422",
            "name": "Robert George Rule",
            "status": "approved by regulator",
            "url": "https://register.fca.org.uk/services/V0.1/Individuals/RXR00422",
        }

    @pytest.mark.asyncio
    async def test_get_firm_permissions(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_permissions(frn)
        await out.fetch_all_pages()
        assert len(out) >= 10

    @pytest.mark.asyncio
    async def test_get_firm_requirements(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_requirements(frn)
        await out.fetch_all_pages()
        assert len(out) == 1
        assert out.model_dump(mode="json") == [
            {
                "reference": "OR-0263614",
                "effective_date": "2025-01-30T00:00:00",
                "financial_promotions_requirement": True,
                "financial_promotions_investment_types": "https://register.fca.org.uk/services/V0.1/Firm/552016/Requirements/OR-0263614/InvestmentTypes",
                "financial promotion for other unauthorised clients": (
                    "This firm can: (1) approve its own financial promotions as well as those of members "
                    "of its wider group and, in certain circumstances, those of its appointed representatives; "
                    "and (2) approve financial promotions for other unauthorised persons for the following types "
                    "of investment:"
                ),
            }
        ]
        el_one = await out[0]
        assert el_one.get_additional_fields() == {
            "financial promotion for other unauthorised clients": (
                "This firm can: (1) approve its own financial promotions as well as those of members "
                "of its wider group and, in certain circumstances, those of its appointed representatives; "
                "and (2) approve financial promotions for other unauthorised persons for the following types "
                "of investment:"
            ),
        }

    @pytest.mark.asyncio
    async def test_get_firm_requirement_investment_types(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_requirement_investment_types(frn, "OR-0263614")
        await out.fetch_all_pages()
        assert len(out) == 8
        assert out.model_dump(mode="json") == [
            {"name": "certificates representing certain securities"},
            {"name": "debentures"},
            {"name": "government and public security"},
            {"name": "listed shares"},
            {"name": "pensions"},
            {"name": "rights to or interests in investments"},
            {"name": "units"},
            {"name": "warrants"},
        ]

    @pytest.mark.asyncio
    async def test_get_firm_regulators(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_regulators(frn)
        await out.fetch_all_pages()
        assert len(out) == 2
        assert out.model_dump(mode="json") == [
            {"name": "Financial Conduct Authority", "effective_date": "2013-04-01T00:00:00", "termination_date": None},
            {
                "name": "Financial Services Authority",
                "effective_date": "2011-09-26T00:00:00",
                "termination_date": "2013-03-31T00:00:00",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_firm_passports(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_passports(frn)
        await out.fetch_all_pages()
        assert len(out) == 0

    @pytest.mark.asyncio
    async def test_get_firm_waivers(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_waivers(frn)
        await out.fetch_all_pages()
        assert len(out) == 1
        assert out.model_dump(mode="json") == [
            {"discretions": None, "discretions_url": None, "rule_article_numbers": ["MIFIDPRU 3.3.3R"]}
        ]

    @pytest.mark.asyncio
    async def test_get_firm_exclusions(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_exclusions(frn)
        await out.fetch_all_pages()
        assert len(out) == 0

    @pytest.mark.asyncio
    async def test_get_firm_disciplinary_history(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_disciplinary_history(frn)
        await out.fetch_all_pages()
        assert len(out) == 0


LARGE_BANK_FRNS = [
    "122702",  # Barclays Bank Plc
    "759676",  # Barclays Bank UK PLC
    "765112",  # HSBC UK Bank Plc
]


class TestRandomFirmDetails:
    @pytest.mark.asyncio
    async def test_mortgage_1st_perms(self, test_client: fca_api.api.Client):
        out = await test_client.get_firm_permissions("484231")
        await out.fetch_all_pages()
        assert len(out) == 0

    @pytest.mark.asyncio
    async def test_barclays_passports(self, test_client: fca_api.api.Client):
        out = await test_client.get_firm_passports("122702")
        await out.fetch_all_pages()
        assert len(out) == 1
        assert out.model_dump(mode="json") == [
            {
                "country": "GIBRALTAR",
                "direction": "out",
                "permissions": "https://register.fca.org.uk/services/v0.1/firm/122702/passports/gibraltar/permission",
            }
        ]
        # Test fetching the permissions for the passport
        passport_perm = await test_client.get_firm_passport_permissions("122702", "GIBRALTAR")
        await passport_perm.fetch_all_pages()
        assert len(passport_perm) == 3

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "frn",
        LARGE_BANK_FRNS,
    )
    async def test_get_firm_permissions(self, test_client: fca_api.api.Client, frn):
        """Test that the data is correcly parsed for the large banks"""
        out = await test_client.get_firm_permissions(frn)
        await out.fetch_all_pages()
        assert len(out) > 10

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "frn",
        LARGE_BANK_FRNS,
    )
    async def test_get_firm_requirements(self, test_client: fca_api.api.Client, frn):
        """Test that the data is correcly parsed for the large banks"""
        out = await test_client.get_firm_requirements(frn)
        await out.fetch_all_pages()
        assert len(out) > 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "frn",
        LARGE_BANK_FRNS,
    )
    async def test_get_firm_passports(self, test_client: fca_api.api.Client, frn):
        """Test that the data is correcly parsed for the large banks"""
        out = await test_client.get_firm_passports(frn)
        await out.fetch_all_pages()
        assert len(out) > 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "frn",
        LARGE_BANK_FRNS,
    )
    async def test_get_firm_passport_permissions(self, test_client: fca_api.api.Client, frn):
        """Test that the data is correcly parsed for the large banks"""
        out = await test_client.get_firm_passports(frn)
        await out.fetch_all_pages()
        for passport in out.local_items():
            perm_out = await test_client.get_firm_passport_permissions(frn, passport.country)
            await perm_out.fetch_all_pages()
            assert len(perm_out) > 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "frn",
        LARGE_BANK_FRNS,
    )
    async def test_get_firm_waivers(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_waivers(frn)
        await out.fetch_all_pages()
        assert len(out) > 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "frn",
        LARGE_BANK_FRNS,
    )
    async def test_get_firm_exclusions(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_exclusions(frn)
        await out.fetch_all_pages()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "frn",
        LARGE_BANK_FRNS,
    )
    async def test_get_firm_disciplinary_history(self, test_client: fca_api.api.Client, frn: str):
        out = await test_client.get_firm_disciplinary_history(frn)
        await out.fetch_all_pages()
        assert len(out) > 1
