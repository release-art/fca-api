import pytest

import fca_api


@pytest.mark.asyncio
async def test_get_fund(test_client: fca_api.async_api.Client):
    out = await test_client.get_fund("185045")
    assert out.model_dump(mode="json") == {
        "type": "ICVC",
        "status": "authorised",
        "cis_depositary_name": "Citibank UK Limited",
        "operator_name": "abrdn Fund Managers Limited",
        "effective_date": "1997-12-23T00:00:00",
        "icvc_registration_no": "SI000001",
        "mmf_nav_type": None,
        "scheme_type": "UCITS (COLL)",
        "mmf_term_type": None,
        "operator_url": "https://register.fca.org.uk/services/V0.1/Firm/121803",
        "sub_funds_url": "https://register.fca.org.uk/services/V0.1/CIS/185045/Subfund",
        "other_name_url": "https://register.fca.org.uk/services/V0.1/CIS/185045/Names",
        "cis_depositary_url": "https://register.fca.org.uk/services/V0.1/Firm/805574",
    }


@pytest.mark.asyncio
async def test_get_fund_names(test_client: fca_api.async_api.Client):
    out = await test_client.get_fund_names("185045")
    await out.fetch_all_pages()
    assert out.model_dump(mode="json") == [
        {
            "name": "ABERDEEN INVESTMENT FUNDS ICVC",
            "effective_from": "1997-12-23T00:00:00",
            "effective_to": "2019-08-22T00:00:00",
        },
        {
            "name": "Aberdeen Standard OEIC I",
            "effective_from": "1997-12-23T00:00:00",
            "effective_to": "2022-08-01T00:00:00",
        },
    ]


@pytest.mark.asyncio
async def test_get_fund_subfunds(test_client: fca_api.async_api.Client):
    out = await test_client.get_fund_subfunds("185045")
    await out.fetch_all_pages()
    assert len(out) == 30
