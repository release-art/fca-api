import asyncio
from typing import Optional, Sequence, Tuple
from unittest.mock import AsyncMock

import pytest

import fca_api.types.pagination as pagination


class TestMultipageList:
    """Test fca_api.types.pagination.MultipageList class."""

    def create_mock_fetch_page(self, pages_data):
        """Helper to create a mock fetch_page callable with predefined pages."""

        async def mock_fetch_page(page_num: int) -> Tuple[Optional[pagination.PaginatedResultInfo], Sequence[str]]:
            if page_num > len(pages_data):
                return None, []

            page_data = pages_data[page_num - 1]
            if page_data is None:
                return None, []

            result_info, items = page_data
            if result_info is None:
                return None, items

            return pagination.PaginatedResultInfo(
                page=result_info["page"],
                per_page=result_info["per_page"],
                total_count=result_info["total_count"],
                next=result_info.get("next"),
                previous=result_info.get("previous"),
            ), items

        return mock_fetch_page

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test MultipageList initialization."""
        fetch_page = AsyncMock()
        mpl = pagination.MultipageList(fetch_page=fetch_page)

        assert mpl._items == []
        assert mpl._fetch_page_cb == fetch_page
        assert isinstance(mpl._lock, asyncio.Lock)
        assert mpl._result_info == pagination.SpecialResultInfoState.UNINITIALIZED

    @pytest.mark.asyncio
    async def test_async_init_success(self):
        """Test successful _asyinc_init with first page fetch."""
        pages_data = [({"page": 1, "per_page": 10, "total_count": 25}, ["item1", "item2", "item3"])]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)

        await mpl._asyinc_init()

        assert len(mpl._items) == 3
        assert mpl._items == ["item1", "item2", "item3"]
        assert isinstance(mpl._result_info, pagination.PaginatedResultInfo)
        assert mpl._result_info.page == 1
        assert mpl._result_info.total_count == 25

    @pytest.mark.asyncio
    async def test_async_init_first_page_failure(self):
        """Test _asyinc_init when first page fetch fails."""

        async def failing_fetch_page(page_num: int):
            return None, []

        mpl = pagination.MultipageList(fetch_page=failing_fetch_page)
        await mpl._asyinc_init()

        assert mpl._result_info == pagination.SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED
        assert len(mpl._items) == 0

    @pytest.mark.asyncio
    async def test_has_next_page_uninitialized(self):
        """Test _has_next_page when state is UNINITIALIZED."""
        fetch_page = AsyncMock()
        mpl = pagination.MultipageList(fetch_page=fetch_page)

        assert mpl._has_next_page() is True

    @pytest.mark.asyncio
    async def test_has_next_page_special_states(self):
        """Test _has_next_page with special states."""
        fetch_page = AsyncMock()
        mpl = pagination.MultipageList(fetch_page=fetch_page)

        mpl._result_info = pagination.SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED
        assert mpl._has_next_page() is False

        mpl._result_info = pagination.SpecialResultInfoState.ALL_PAGES_FETCHED
        assert mpl._has_next_page() is False

    @pytest.mark.asyncio
    async def test_has_next_page_with_result_info(self):
        """Test _has_next_page with PaginatedResultInfo."""
        fetch_page = AsyncMock()
        mpl = pagination.MultipageList(fetch_page=fetch_page)

        # Test with next page available
        mpl._result_info = pagination.PaginatedResultInfo(
            page=1, per_page=10, total_count=25, next="http://example.com/next"
        )
        assert mpl._has_next_page() is True

        # Test at last page
        mpl._result_info = pagination.PaginatedResultInfo(page=3, per_page=10, total_count=25, next=None)
        assert mpl._has_next_page() is False

        # Test beyond total pages
        mpl._result_info = pagination.PaginatedResultInfo(
            page=4, per_page=10, total_count=25, next="http://example.com/next"
        )
        assert mpl._has_next_page() is False

    @pytest.mark.asyncio
    async def test_fetch_page_to_item_idx_already_cached(self):
        """Test _fetch_page_to_item_idx when item is already cached."""
        fetch_page = AsyncMock()
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        mpl._items = ["item1", "item2", "item3"]
        mpl._result_info = pagination.SpecialResultInfoState.ALL_PAGES_FETCHED

        await mpl._fetch_page_to_item_idx(1)

        fetch_page.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_page_to_item_idx_no_next_page(self):
        """Test _fetch_page_to_item_idx when no next page available."""
        fetch_page = AsyncMock()
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        mpl._result_info = pagination.SpecialResultInfoState.ALL_PAGES_FETCHED

        await mpl._fetch_page_to_item_idx(5)

        fetch_page.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_page_to_item_idx_multiple_pages(self):
        """Test fetching multiple pages to reach desired index."""
        pages_data = [
            ({"page": 1, "per_page": 2, "total_count": 6, "next": "http://example.com/page2"}, ["item1", "item2"]),
            ({"page": 2, "per_page": 2, "total_count": 6, "next": "http://example.com/page3"}, ["item3", "item4"]),
            ({"page": 3, "per_page": 2, "total_count": 6, "next": None}, ["item5", "item6"]),
        ]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)

        # Fetch item at index 3 (4th item) - should fetch pages 1 and 2
        await mpl._fetch_page_to_item_idx(3)
        assert len(mpl._items) == 4  # Should have items 1-4 after fetching first 2 pages
        assert mpl._items == ["item1", "item2", "item3", "item4"]

        # Now fetch item at index 4 (5th item) - should fetch page 3
        await mpl._fetch_page_to_item_idx(4)
        assert len(mpl._items) == 6  # Should fetch all pages to get item 5
        assert mpl._items == ["item1", "item2", "item3", "item4", "item5", "item6"]

    @pytest.mark.asyncio
    async def test_fetch_page_assertion_error(self):
        """Test assertion error when page number mismatch."""

        async def bad_fetch_page(page_num: int):
            # Return wrong page number
            return pagination.PaginatedResultInfo(page=99, per_page=10, total_count=25), ["item1"]

        mpl = pagination.MultipageList(fetch_page=bad_fetch_page)

        with pytest.raises(AssertionError):
            await mpl._asyinc_init()

    @pytest.mark.asyncio
    async def test_getitem_single_item(self):
        """Test __getitem__ for a single item."""
        pages_data = [({"page": 1, "per_page": 10, "total_count": 25}, ["item1", "item2", "item3"])]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)

        item = await mpl[1]
        assert item == "item2"

    @pytest.mark.asyncio
    async def test_getitem_index_error(self):
        """Test __getitem__ with invalid index."""
        pages_data = [({"page": 1, "per_page": 10, "total_count": 25}, ["item1", "item2"])]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        mpl._result_info = pagination.SpecialResultInfoState.ALL_PAGES_FETCHED

        with pytest.raises(IndexError):
            await mpl[5]

    @pytest.mark.asyncio
    async def test_aiter_complete_iteration(self):
        """Test __aiter__ iterating through all items."""
        pages_data = [
            ({"page": 1, "per_page": 2, "total_count": 4, "next": "http://example.com/page2"}, ["item1", "item2"]),
            ({"page": 2, "per_page": 2, "total_count": 4, "next": None}, ["item3", "item4"]),
        ]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        await mpl._asyinc_init()

        items = []
        async for item in mpl:
            items.append(item)

        assert items == ["item1", "item2", "item3", "item4"]

    @pytest.mark.asyncio
    async def test_aiter_with_index_error_handling(self):
        """Test __aiter__ handles IndexError gracefully."""
        # Mock scenario where len() changes during iteration due to API inconsistencies
        fetch_page = AsyncMock()
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        mpl._items = ["item1", "item2"]
        mpl._result_info = pagination.PaginatedResultInfo(
            page=1,
            per_page=10,
            total_count=5,  # Claim 5 items but only have 2
        )

        items = []
        async for item in mpl:
            items.append(item)

        assert items == ["item1", "item2"]

    @pytest.mark.asyncio
    async def test_aiter_unexpected_index_error(self):
        """Test __aiter__ re-raises unexpected IndexError."""

        class BadMultipageList(pagination.MultipageList):
            async def __getitem__(self, index: int):
                if index < 2:
                    return f"item{index + 1}"
                raise IndexError("Unexpected error")

            def __len__(self):
                return 5  # Claim more items than available

        fetch_page = AsyncMock()
        mpl = BadMultipageList(fetch_page=fetch_page)

        items = []
        with pytest.raises(IndexError, match="Unexpected error"):
            async for item in mpl:
                items.append(item)

    @pytest.mark.asyncio
    async def test_local_items(self):
        """Test local_items returns cached items."""
        pages_data = [({"page": 1, "per_page": 10, "total_count": 25}, ["item1", "item2", "item3"])]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)

        # Before fetching
        assert mpl.local_items() == ()

        # After fetching
        await mpl._asyinc_init()
        assert mpl.local_items() == ("item1", "item2", "item3")

    @pytest.mark.asyncio
    async def test_len_with_has_next_page(self):
        """Test __len__ when more pages are available."""
        pages_data = [
            (
                {"page": 1, "per_page": 10, "total_count": 25, "next": "http://example.com/page2"},
                ["item1", "item2", "item3"],
            )
        ]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        await mpl._asyinc_init()

        # Should return total_count from result_info since there are more pages
        assert len(mpl) == 25

    @pytest.mark.asyncio
    async def test_len_all_pages_fetched(self):
        """Test __len__ when all pages are fetched."""
        fetch_page = AsyncMock()
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        mpl._items = ["item1", "item2", "item3"]
        mpl._result_info = pagination.SpecialResultInfoState.ALL_PAGES_FETCHED

        # Should return actual item count
        assert len(mpl) == 3

    @pytest.mark.asyncio
    async def test_repr(self):
        """Test __repr__ method."""
        fetch_page = AsyncMock()
        mpl = pagination.MultipageList(fetch_page=fetch_page)

        repr_str = repr(mpl)
        assert "MultipageList" in repr_str

    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """Test thread safety with concurrent access."""
        call_count = 0

        async def slow_fetch_page(page_num: int):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simulate slow API
            return pagination.PaginatedResultInfo(page=page_num, per_page=5, total_count=10), [
                f"item{i}" for i in range((page_num - 1) * 5 + 1, page_num * 5 + 1)
            ]

        mpl = pagination.MultipageList(fetch_page=slow_fetch_page)

        # Concurrent access to same page range
        results = await asyncio.gather(mpl[0], mpl[1], mpl[2], mpl[3], mpl[4])

        # Should only fetch once due to locking
        assert call_count == 1
        assert results == ["item1", "item2", "item3", "item4", "item5"]

    @pytest.mark.asyncio
    async def test_edge_case_empty_pages(self):
        """Test handling of empty pages."""
        pages_data = [({"page": 1, "per_page": 10, "total_count": 0}, [])]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        await mpl._asyinc_init()

        assert len(mpl) == 0
        assert mpl.local_items() == ()

    @pytest.mark.asyncio
    async def test_edge_case_inconsistent_api_total_count(self):
        """Test handling when API total_count is inconsistent."""
        pages_data = [
            (
                {"page": 1, "per_page": 10, "total_count": 100, "next": "http://example.com/page2"},
                ["item1", "item2"],
            ),  # Claims 100 but only 2 items
            (None, []),  # Next page returns None
        ]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        await mpl._asyinc_init()

        # Initially reports total_count because there appears to be a next page
        assert len(mpl) == 100

        # Try to access beyond available items - this should trigger fetching until no more pages
        await mpl._fetch_page_to_item_idx(50)  # This should trigger fetching page 2, which returns None

        # After fetching all available, _has_next_page() should return False, so len() returns actual count
        assert len(mpl) == 2

    @pytest.mark.asyncio
    async def test_pagination_with_none_next_url(self):
        """Test pagination when next URL is None but page count suggests more pages."""
        pages_data = [
            ({"page": 1, "per_page": 5, "total_count": 10, "next": None}, ["item1", "item2", "item3", "item4", "item5"])
        ]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        await mpl._asyinc_init()

        # Should not attempt to fetch more pages when next is None
        assert not mpl._has_next_page()
        assert len(mpl) == 5  # Should return actual items length


class TestPaginatedResultInfo:
    """Test fca_api.types.pagination.PaginatedResultInfo class."""

    def test_basic_initialization(self):
        """Test basic initialization of PaginatedResultInfo."""
        info = pagination.PaginatedResultInfo(page=1, per_page=10, total_count=25)

        assert info.page == 1
        assert info.per_page == 10
        assert info.total_count == 25
        assert info.next is None
        assert info.previous is None

    def test_with_urls(self):
        """Test initialization with next and previous URLs."""
        info = pagination.PaginatedResultInfo(
            page=2,
            per_page=10,
            total_count=25,
            next="https://api.example.com/page/3",
            previous="https://api.example.com/page/1",
        )

        assert str(info.next) == "https://api.example.com/page/3"
        assert str(info.previous) == "https://api.example.com/page/1"

    def test_total_pages_calculation(self):
        """Test total_pages property calculation."""
        # Exact division
        info1 = pagination.PaginatedResultInfo(page=1, per_page=10, total_count=30)
        assert info1.total_pages == 3

        # With remainder
        info2 = pagination.PaginatedResultInfo(page=1, per_page=10, total_count=25)
        assert info2.total_pages == 3

        # Single page
        info3 = pagination.PaginatedResultInfo(page=1, per_page=10, total_count=5)
        assert info3.total_pages == 1

        # Empty result
        info4 = pagination.PaginatedResultInfo(page=1, per_page=10, total_count=0)
        assert info4.total_pages == 0

    def test_model_validate_key_normalization(self):
        """Test model_validate normalizes keys to lowercase and strips whitespace."""
        raw_data = {
            "Page ": 1,
            " Per_Page": 10,
            "TOTAL_COUNT   ": 25,
            " Next  ": "https://api.example.com/next",
            "Previous": None,
        }

        info = pagination.PaginatedResultInfo.model_validate(raw_data)

        assert info.page == 1
        assert info.per_page == 10
        assert info.total_count == 25
        assert str(info.next) == "https://api.example.com/next"
        assert info.previous is None

    def test_model_validate_with_empty_dict(self):
        """Test model_validate with minimal required fields."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):  # Should fail due to missing required fields
            pagination.PaginatedResultInfo.model_validate({})

    def test_model_validate_with_invalid_url(self):
        """Test model_validate with invalid URL."""
        from pydantic import ValidationError

        raw_data = {"page": 1, "per_page": 10, "total_count": 25, "next": "not-a-valid-url"}

        with pytest.raises(ValidationError):  # Should fail URL validation
            pagination.PaginatedResultInfo.model_validate(raw_data)


class TestSpecialResultInfoState:
    """Test fca_api.types.pagination.SpecialResultInfoState enum."""

    def test_enum_values(self):
        """Test that all expected enum values exist."""
        assert hasattr(pagination.SpecialResultInfoState, "UNINITIALIZED")
        assert hasattr(pagination.SpecialResultInfoState, "FIRST_PAGE_FETCH_FAILED")
        assert hasattr(pagination.SpecialResultInfoState, "ALL_PAGES_FETCHED")

    def test_enum_uniqueness(self):
        """Test that enum values are unique."""
        values = [
            pagination.SpecialResultInfoState.UNINITIALIZED,
            pagination.SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED,
            pagination.SpecialResultInfoState.ALL_PAGES_FETCHED,
        ]

        assert len(values) == len(set(values))


class TestErrorHandlingEdgeCases:
    """Test error handling and edge cases for pagination types."""

    @pytest.mark.asyncio
    async def test_fetch_page_callback_exception(self):
        """Test handling when fetch_page callback raises an exception."""

        async def failing_fetch_page(page_num: int):
            raise ValueError("API connection failed")

        mpl = pagination.MultipageList(fetch_page=failing_fetch_page)

        with pytest.raises(ValueError, match="API connection failed"):
            await mpl._asyinc_init()

    @pytest.mark.asyncio
    async def test_fetch_page_returns_invalid_data(self):
        """Test handling when fetch_page returns malformed data."""

        async def bad_fetch_page(page_num: int):
            # Return invalid tuple structure
            return "invalid", "data"

        mpl = pagination.MultipageList(fetch_page=bad_fetch_page)

        # This should raise an error due to invalid return type when trying to access page info
        with pytest.raises((AttributeError, TypeError)):
            await mpl._asyinc_init()

    @pytest.mark.asyncio
    async def test_negative_index_access(self):
        """Test accessing negative indices."""
        pages_data = [({"page": 1, "per_page": 10, "total_count": 25}, ["item1", "item2", "item3"])]
        fetch_page = self.create_mock_fetch_page(pages_data)
        mpl = pagination.MultipageList(fetch_page=fetch_page)
        await mpl._asyinc_init()

        # Negative indices should work like normal Python lists (access from end)
        item = await mpl[-1]  # Should return 'item3'
        assert item == "item3"

        item = await mpl[-2]  # Should return 'item2'
        assert item == "item2"

        # But accessing beyond available negative indices should raise IndexError
        with pytest.raises(IndexError):
            await mpl[-10]  # Only 3 items, so -10 is out of bounds

    def create_mock_fetch_page(self, pages_data):
        """Helper to create a mock fetch_page callable with predefined pages."""

        async def mock_fetch_page(page_num: int) -> Tuple[Optional[pagination.PaginatedResultInfo], Sequence[str]]:
            if page_num > len(pages_data):
                return None, []

            page_data = pages_data[page_num - 1]
            if page_data is None:
                return None, []

            result_info, items = page_data
            if result_info is None:
                return None, items

            return pagination.PaginatedResultInfo(
                page=result_info["page"],
                per_page=result_info["per_page"],
                total_count=result_info["total_count"],
                next=result_info.get("next"),
                previous=result_info.get("previous"),
            ), items

        return mock_fetch_page

    @pytest.mark.asyncio
    async def test_very_large_pagination(self):
        """Test handling of very large pagination numbers."""
        info = pagination.PaginatedResultInfo(page=1000000, per_page=1, total_count=1000000)

        assert info.total_pages == 1000000

    @pytest.mark.asyncio
    async def test_zero_per_page(self):
        """Test handling when per_page is zero."""
        # Creating PaginatedResultInfo with per_page=0 should be allowed by pydantic
        # but accessing total_pages should handle division by zero gracefully
        info = pagination.PaginatedResultInfo(page=1, per_page=0, total_count=25)

        # The total_pages calculation should handle zero per_page
        # Looking at the implementation: (total_count + per_page - 1) // per_page
        # With per_page=0: (25 + 0 - 1) // 0 = 24 // 0 which raises ZeroDivisionError
        with pytest.raises(ZeroDivisionError):
            _ = info.total_pages

    @pytest.mark.asyncio
    async def test_inconsistent_pagination_state(self):
        """Test handling when pagination state becomes inconsistent."""

        async def inconsistent_fetch_page(page_num: int):
            # First call returns normal data
            if page_num == 1:
                return pagination.PaginatedResultInfo(
                    page=1, per_page=10, total_count=25, next="http://example.com/page2"
                ), ["item1", "item2"]
            # Second call returns different total_count (API inconsistency)
            elif page_num == 2:
                return pagination.PaginatedResultInfo(
                    page=2,
                    per_page=10,
                    total_count=50,
                    next=None,  # Different total and no more pages
                ), ["item3", "item4"]
            else:
                return None, []

        mpl = pagination.MultipageList(fetch_page=inconsistent_fetch_page)
        await mpl._asyinc_init()

        # Initial length based on first page
        initial_len = len(mpl)
        assert initial_len == 25

        # Fetch second page
        await mpl._fetch_page_to_item_idx(3)

        # Length should update based on new info, but since next=None, no more pages expected
        # The _has_next_page() will return False, so len() returns actual item count
        updated_len = len(mpl)
        assert updated_len == 4  # Should reflect the actual items fetched (4 items total)
