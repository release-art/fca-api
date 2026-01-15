import pytest

import fca_api


class TestFundMethods:
    @pytest.mark.asyncio
    async def test_get_fund_success(self, test_client):
        # Covers the case of a request for the details of an
        # existing fund, 'Jupiter Asia Pacific Income Fund (IRL)' (PRN '185045')
        recv_response = await test_client.get_fund("185045")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_fund_failure(self, test_client):
        # Covers the case of a request for the details of a non-existent fund
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_fund("1234567890")

    @pytest.mark.asyncio
    async def test_get_fund_names_success(self, test_client):
        # Covers the case of a request for the alternate/secondary names
        # details of existing fund with PRN 185045
        recv_response = await test_client.get_fund_names("185045")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_fund_names_failure_no_names(self, test_client):
        # Covers the case of a request for the alternate/secondary name
        # details of an existing fund with PRN 1006826 - this raises an error
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_fund_names("1006826")

    @pytest.mark.asyncio
    async def test_get_fund_names_failure(self, test_client):
        # Covers the case of a request for the alternate/secondary name
        # details of a non-existent fund
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_fund_names("1234567890")

    @pytest.mark.asyncio
    async def test_get_fund_subfunds_success(self, test_client):
        # Covers the case of a request for the subfund details of an
        # existing fund with PRN 185045
        recv_response = await test_client.get_fund_subfunds("185045")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_fund_subfunds_empty_result(self, test_client):
        # Covers the case of a request for the subfund details of an
        # existing fund with PRN 1006826
        recv_response = await test_client.get_fund_subfunds("1006826")
        assert recv_response.is_success
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_get_fund_subfunds_empty_result_nonexistent(self, test_client):
        # Covers the case of a request for the subfund details of a
        # non-existent fund - returns empty but doesn't fail
        recv_response = await test_client.get_fund_subfunds("1234567890")
        assert recv_response.is_success
        assert not recv_response.data
