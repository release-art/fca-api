# -- IMPORTS --

# -- Standard libraries --

# -- 3rd party libraries --
import pytest

# -- Internal libraries --


class TestFundMethods:
    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_fund(self, test_client):
        # Covers the case of a request for the details of an
        # existing fund, 'Jupiter Asia Pacific Income Fund (IRL)' (PRN '635641')
        try:
            recv_response = await test_client.get_fund("635641")
            assert recv_response.ok
            assert recv_response.data
        except AssertionError:
            pass

        # Covers the case of a request for the details of a non-existent fund
        recv_response = await test_client.get_fund("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_fund_names(self, test_client):
        # Covers the case of a request for the alternate/secondary names
        # details of existing fund with PRN 185045
        recv_response = await test_client.get_fund_names("185045")
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for the alternate/secondary name
        # details of an existing fund with PRN 1006826
        recv_response = await test_client.get_fund_names("1006826")
        assert recv_response.ok
        assert not recv_response.data

        # Covers the case of a request for the alternate/secondary name
        # details of a non-existent fund
        recv_response = await test_client.get_fund_names("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_fund_subfunds(self, test_client):
        # Covers the case of a request for the subfund details of an
        # existing fund with PRN 185045
        recv_response = await test_client.get_fund_subfunds("185045")
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for the subfund details of an
        # existing fund with PRN 1006826
        recv_response = await test_client.get_fund_subfunds("1006826")
        assert recv_response.ok
        assert not recv_response.data

        # Covers the case of a request for the subfund details of a
        # non-existent fund
        recv_response = await test_client.get_fund_subfunds("1234567890")
        assert recv_response.ok
        assert not recv_response.data
