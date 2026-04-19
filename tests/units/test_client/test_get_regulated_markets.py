import pytest

import fca_api


@pytest.mark.asyncio
async def test_get_fund_subfunds(test_client: fca_api.async_api.Client):
    out = await test_client.get_regulated_markets(result_count=100)
    assert len(out.data) == 5
    assert [item.model_dump(mode="json") for item in out.data] == [
        {
            "name": "The London Metal Exchange",
            "trading_name": None,
            "type": "Exchange - RM",
            "status": "",
            "reference_number": None,
            "firm_url": "https://register.fca.org.uk/services/V0.1/Firm/",
        },
        {
            "name": "ICE Futures Europe",
            "trading_name": None,
            "type": "Exchange - RM",
            "status": "",
            "reference_number": None,
            "firm_url": "https://register.fca.org.uk/services/V0.1/Firm/",
        },
        {
            "name": "London Stock Exchange",
            "trading_name": None,
            "type": "Exchange - RM",
            "status": "",
            "reference_number": None,
            "firm_url": "https://register.fca.org.uk/services/V0.1/Firm/",
        },
        {
            "name": "Aquis Stock Exchange Limited",
            "trading_name": "ICAP Securities & Derivatives Exchange Limited",
            "type": "Exchange - RM",
            "status": "",
            "reference_number": None,
            "firm_url": "https://register.fca.org.uk/services/V0.1/Firm/",
        },
        {
            "name": "Cboe Europe Equities Regulated Market",
            "trading_name": None,
            "type": "Exchange - RM",
            "status": "",
            "reference_number": None,
            "firm_url": "https://register.fca.org.uk/services/V0.1/Firm/",
        },
    ]
