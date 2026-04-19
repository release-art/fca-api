import pytest

import fca_api


class TestFirmSearch:
    @pytest.mark.asyncio
    async def test_search_firm_by_name(self, test_client: fca_api.async_api.Client):
        response = await test_client.search_frn("revolution brokers")
        assert response.pagination.size == 2
        assert len(response.data) == 2

    @pytest.mark.asyncio
    async def test_search_firm_no_results(self, test_client: fca_api.async_api.Client):
        response = await test_client.search_frn("nonexistent firm xyz")
        assert len(response.data) == 0
        assert not response.pagination.has_next

    @pytest.mark.asyncio
    async def test_multipage_results(self, test_client: fca_api.async_api.Client):
        # First page
        page1 = await test_client.search_frn("revolution")
        assert page1.pagination.size > 50
        assert len(page1.data) > 0
        assert page1.pagination.has_next
        for item in page1.data:
            assert item.name

        # Explicit multi-page fetch via result_count
        all_results = await test_client.search_frn("revolution", result_count=page1.pagination.size)
        assert len(all_results.data) == page1.pagination.size or not all_results.pagination.has_next
        for item in all_results.data:
            assert item.name


class TestIndividualSearch:
    @pytest.mark.asyncio
    async def test_multiple_search_individual(self, test_client: fca_api.async_api.Client):
        page1 = await test_client.search_irn("bob")
        assert page1.pagination.size >= 1000
        for item in page1.data:
            assert item.name
        # Verify pagination token works for subsequent page
        assert page1.pagination.has_next
        page2 = await test_client.search_irn("bob", next_page=page1.pagination.next_page)
        assert len(page2.data) > 0

    @pytest.mark.asyncio
    async def test_empty_search_individual(self, test_client: fca_api.async_api.Client):
        response = await test_client.search_irn("f9eed039-4da8-4f21-8b02-424a6ec9d9e5")
        assert len(response.data) == 0
        assert not response.pagination.has_next


class TestFundSearch:
    @pytest.mark.asyncio
    async def test_search_fund_by_name(self, test_client: fca_api.async_api.Client):
        page1 = await test_client.search_prn("global equity fund")
        assert page1.pagination.size > 500
        for item in page1.data:
            assert item.name
        assert page1.pagination.has_next

    @pytest.mark.asyncio
    async def test_search_fund_no_results(self, test_client: fca_api.async_api.Client):
        response = await test_client.search_prn("nonexistent fund xyz")
        assert len(response.data) == 0
