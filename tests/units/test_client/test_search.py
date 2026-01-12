import pytest

import fca_api


class TestFirmSearch:
    @pytest.mark.asyncio
    async def test_search_firm_by_name(self, test_client: fca_api.api.Client):
        response = await test_client.search_frn("revolution brokers")
        assert len(response) == 2

    @pytest.mark.asyncio
    async def test_search_firm_no_results(self, test_client: fca_api.api.Client):
        response = await test_client.search_frn("nonexistent firm xyz")
        assert len(response) == 0

    @pytest.mark.asyncio
    async def test_multipage_results(self, test_client: fca_api.api.Client):
        response = await test_client.search_frn("revolution")
        assert len(response) > 50
        assert len(response.local_items()) == 20
        first_item = await response[0]
        assert first_item.name
        idx = 0
        async for item in response:
            assert item.name
            idx += 1
        assert idx == len(response)
        assert len(response.local_items()) == len(response)


class TestIndividualSearch:
    @pytest.mark.asyncio
    async def test_multiple_search_individual(self, test_client: fca_api.api.Client):
        response = await test_client.search_irn("bob")
        assert len(response) >= 1000
        idx = 0
        async for item in response:
            assert item.name
            idx += 1
        assert idx == len(response)

    @pytest.mark.asyncio
    async def test_empty_search_individual(self, test_client: fca_api.api.Client):
        response = await test_client.search_irn("f9eed039-4da8-4f21-8b02-424a6ec9d9e5")
        assert len(response) >= 1000
        idx = 0
        async for item in response:
            assert item.name
            idx += 1
        assert idx == len(response)