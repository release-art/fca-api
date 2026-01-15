"""Pagination types and utilities for FCA API responses.

This module provides the `MultipageList` class and related types for handling
paginated API responses from the FCA Financial Services Register. The pagination
system supports:

- **Lazy loading**: Pages are fetched only when needed
- **Async iteration**: Full support for `async for` loops
- **List-like interface**: Length checking, indexing, and slicing
- **Automatic metadata**: Page counts and navigation info

The `MultipageList` class is returned by all search methods in the high-level
client and provides a seamless interface for working with large result sets.

Key Features:
    - Automatic page fetching on demand
    - Efficient memory usage (only loaded pages are kept)
    - Full async iteration support with `async for`
    - Standard list operations like `len()` and `[index]`
    - Manual control with `fetch_all_pages()` method

Example:
    Working with paginated results::

        # Get paginated search results
        results = await client.search_frn("Barclays")

        # Check total count without loading all pages
        print(f"Total results: {len(results)}")

        # Iterate through all results (loads pages as needed)
        async for firm in results:
            print(f"{firm.name} - {firm.frn}")

        # Access specific items by index
        if len(results) > 0:
            first_firm = results[0]  # Loads first page if not cached
            print(f"First result: {first_firm.name}")

        # Load all pages at once (for bulk processing)
        await results.fetch_all_pages()

        # Now all data is locally cached
        for firm in results.local_items():
            process_firm(firm)

See Also:
    - `fca_api.async_api.Client`: High-level client that returns MultipageList objects
    - `fca_api.raw_api.FcaApiResponse`: Raw response wrapper with pagination info
"""

import asyncio
import dataclasses
import enum
import logging
import typing

import httpx
import pydantic

from .. import exc
from . import settings

logger = logging.getLogger(__name__)
T = typing.TypeVar("T", bound=pydantic.BaseModel)


class PaginatedResultInfo(pydantic.BaseModel):
    """Pagination metadata from FCA API responses.

    This model represents the pagination information returned by the FCA API
    in the `ResultInfo` section of responses. It provides details about the
    current page, total results, and navigation URLs.

    Attributes:
        next: URL for the next page of results (None if this is the last page)
        previous: URL for the previous page (None if this is the first page)
        page: Current page number (1-based)
        per_page: Number of items per page
        total_count: Total number of items across all pages

    Properties:
        total_pages: Calculated total number of pages available

    Example:
        Access pagination info from a response::

            response = await raw_client.search_frn("test")
            if response.result_info:
                info = PaginatedResultInfo.model_validate(response.result_info)

                print(f"Page {info.page} of {info.total_pages}")
                print(f"{info.per_page} items per page")
                print(f"{info.total_count} total items")

                if info.next:
                    print("More pages available")

    Note:
        The `model_validate` class method handles the case-insensitive field
        mapping from the API response format.
    """

    next: typing.Optional[pydantic.HttpUrl] = None
    previous: typing.Optional[pydantic.HttpUrl] = None
    page: int
    per_page: int
    total_count: int

    @property
    def total_pages(self) -> int:
        """Calculate the total number of pages.

        Returns:
            The total number of pages needed to contain all items,
            calculated from total_count and per_page.

        Example:
            Calculate remaining pages::

                info = PaginatedResultInfo.model_validate(response.result_info)
                remaining = info.total_pages - info.page
                print(f"{remaining} pages remaining")
        """
        return (self.total_count + self.per_page - 1) // self.per_page

    @classmethod
    def model_validate(cls, data: dict) -> "PaginatedResultInfo":
        return super().model_validate(
            {key.lower().strip(): value for (key, value) in data.items()}, extra=settings.model_validate_extra
        )


FetchPageRvT = typing.Tuple[
    typing.Optional[PaginatedResultInfo],
    typing.Sequence[T],
]

FetchPageCallableT = typing.Callable[[int], typing.Awaitable[FetchPageRvT[T]]]


@enum.unique
class SpecialResultInfoState(enum.Enum):
    UNINITIALIZED = enum.auto()
    FIRST_PAGE_FETCH_FAILED = enum.auto()
    ALL_PAGES_FETCHED = enum.auto()
    PAGE_FETCH_FAILED = enum.auto()


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class FetchedPageData(typing.Generic[T]):
    items: typing.Sequence[T]
    page_info: typing.Optional[PaginatedResultInfo]


class MultipageList(typing.Generic[T]):
    """A list-like container for paginated API responses.

    This class provides a seamless interface for working with paginated data
    from the FCA API. It behaves like a regular Python list but automatically
    handles page fetching, caching, and async iteration.

    The class implements lazy loading: pages are only fetched from the API
    when needed (e.g., when iterating or accessing specific indices). This
    provides efficient memory usage for large result sets.

    Type Parameters:
        T: The type of items contained in the list (usually Pydantic models)

    Key Features:
        - **Lazy page loading**: Pages fetched only when accessed
        - **Async iteration**: Full support for `async for` loops
        - **List operations**: `len()`, indexing, and slicing support
        - **Caching**: Previously fetched pages are cached locally
        - **Thread-safe**: Uses asyncio locks for concurrent access

    Usage Patterns:
        Check total count (fetches first page)::

            results = await client.search_frn("test")
            print(f"Found {len(results)} total results")

        Iterate through all results (fetches pages as needed)::

            async for item in results:
                print(f"Processing {item.name}")

        Access specific items by index::

            if len(results) > 0:
                first_item = results[0]  # May trigger page fetch
                last_item = results[-1]  # May trigger multiple page fetches

        Bulk processing with pre-loading::

            await results.fetch_all_pages()  # Load everything
            for item in results.local_items():
                process_item(item)  # No more API calls

    Performance Notes:
        - First access to `len()` requires fetching the first page
        - Random access to high indices may require fetching multiple pages
        - Sequential iteration is most efficient (pages fetched in order)
        - Use `fetch_all_pages()` for bulk processing scenarios

    Example:
        Complete usage example::

            # Get search results (no API call yet)
            results = await client.search_frn("Barclays")

            # Check if any results (triggers first page fetch)
            if len(results) > 0:
                print(f"Found {len(results)} firms")

                # Process first few results
                for i in range(min(5, len(results))):
                    firm = results[i]
                    print(f"{i+1}. {firm.name} ({firm.frn})")

                # Iterate through all results efficiently
                count = 0
                async for firm in results:
                    if firm.status == "Authorised":
                        count += 1

                print(f"Found {count} authorised firms")

    See Also:
        - `PaginatedResultInfo`: Pagination metadata
        - `fca_api.async_api.Client`: Returns MultipageList from search methods
    """

    _pages: typing.List[FetchedPageData[T]]
    _fetch_page_cb: FetchPageCallableT[T]
    _lock: asyncio.Lock
    _result_info: PaginatedResultInfo | SpecialResultInfoState

    def __init__(
        self,
        /,
        fetch_page: FetchPageCallableT[T],
    ) -> None:
        """Initialize a new MultipageList.

        Args:
            fetch_page: Async function that fetches a page of results given
                a page index. Should return a tuple of (pagination_info, items).

        Note:
            After initialization, call `_async_init()` to fetch the first page
            and populate metadata. This is done automatically by the high-level
            client methods.

        Example:
            Manual MultipageList creation::

                async def fetch_firms(page_idx: int):
                    response = await raw_client.search_frn("test", page=page_idx)
                    # Parse and return (info, items)

                results = MultipageList(fetch_page=fetch_firms)
                await results._async_init()  # Required!
        """
        self._pages = []
        self._lock = asyncio.Lock()
        self._fetch_page_cb = fetch_page
        self._result_info = SpecialResultInfoState.UNINITIALIZED

    def _has_next_page(self) -> bool:
        if self._result_info is SpecialResultInfoState.UNINITIALIZED:
            return True
        elif isinstance(self._result_info, SpecialResultInfoState):
            # Any other special state means that there are no more pages to fetch.
            return False
        assert isinstance(self._result_info, PaginatedResultInfo)
        return (self._result_info.page < self._result_info.total_pages) and self._result_info.next is not None

    async def _async_init(self) -> None:
        """Initialize the MultipageList by fetching the first page.

        This method must be called after construction to populate the initial
        pagination metadata. It fetches the first page to determine total
        counts, page sizes, and other pagination information.

        Raises:
            Various exceptions depending on the fetch_page callback behavior
            (typically HTTP errors, validation errors, etc.)

        Note:
            This method is called automatically by the high-level client methods.
            Manual callers must ensure this is called before using the list.

        Example:
            Manual initialization::

                results = MultipageList(fetch_page=my_fetch_function)
                await results._async_init()  # Required before use
                print(len(results))  # Now safe to call
        """
        # Fetch the first page to initialize the result info.
        await self._fetch_page_to_item_idx(0)

    async def fetch_all_pages(self) -> None:
        """Fetch all remaining pages from the API.

        This method loads all pages into local memory, which can be useful
        for bulk processing scenarios where you need to access the data
        multiple times or perform operations that require the complete dataset.

        After calling this method, all subsequent access to the list items
        will be served from the local cache without additional API calls.

        Example:
            Bulk processing pattern::

                results = await client.search_frn("test")

                # Load all data once
                await results.fetch_all_pages()

                # Now process multiple times without API calls
                authorised = [f for f in results.local_items() if f.status == "Authorised"]
                unauthorised = [f for f in results.local_items() if f.status != "Authorised"]

                print(f"Authorised: {len(authorised)}, Unauthorised: {len(unauthorised)}")

        Warning:
            This method can consume significant memory and time for large result
            sets. Use judiciously and consider whether streaming with async
            iteration might be more appropriate.
        """
        while self._has_next_page():
            await self._fetch_page_to_item_idx(self.local_len() + 1)

    async def _fetch_page_to_item_idx(self, desired_item_idx: int) -> typing.Optional[PaginatedResultInfo]:
        """Fetch a specific page from the API if it is not already cached.

        Args:
            desired_item_idx: The index of the desired item to fetch.
        """
        if self.local_len() > desired_item_idx or not self._has_next_page():
            return None
        new_page_info = None
        async with self._lock:
            # Double-check after acquiring the lock.
            while self.local_len() <= desired_item_idx and self._has_next_page():
                if isinstance(self._result_info, SpecialResultInfoState):
                    last_fetched_page = 0
                else:
                    last_fetched_page = self._result_info.page

                try:
                    (new_page_info, new_items) = await self._fetch_page_cb(last_fetched_page + 1)
                except (httpx.RequestError, exc.FcaBaseError) as e:
                    logger.exception(f"Failed to fetch page {last_fetched_page + 1}: {e}")
                    if last_fetched_page == 0:
                        self._result_info = SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED
                    else:
                        self._result_info = SpecialResultInfoState.PAGE_FETCH_FAILED
                    return None
                self._max_fetched_page = last_fetched_page + 1
                self._pages.append(FetchedPageData(items=new_items, page_info=new_page_info))
                if new_page_info is None:
                    if last_fetched_page == 0:
                        self._result_info = SpecialResultInfoState.FIRST_PAGE_FETCH_FAILED
                    else:
                        self._result_info = SpecialResultInfoState.ALL_PAGES_FETCHED
                else:
                    assert new_page_info.page == last_fetched_page + 1, (
                        new_page_info.page,
                        last_fetched_page + 1,
                    )
                    self._result_info = new_page_info
        return new_page_info

    async def __getitem__(self, index: int) -> T:
        """Get an item by its index, fetching pages as necessary.

        Please note: negative indices are not supported.
        """
        if index < 0:
            raise IndexError("Negative indices are not supported.")
        await self._fetch_page_to_item_idx(index)
        return self.local_items()[index]

    async def __aiter__(self) -> typing.AsyncIterator[T]:
        idx = 0
        for idx in range(len(self)):
            try:
                yield await self[idx]
            except IndexError:
                # Double check that this is an actual IndexError, or the __len__
                # has changed due to FCA api inconsistencies.
                if idx >= len(self):
                    break
                else:
                    raise

    def local_items(self) -> typing.Tuple[T, ...]:
        """Return the items that have been locally cached without making API calls.

        Returns:
            A tuple of locally cached items.
        """
        items = []
        for page in self._pages:
            items.extend(page.items)
        return tuple(items)

    def local_len(self) -> int:
        """Return the number of items that have been locally cached without making API calls.

        Returns:
            The number of locally cached items.
        """
        return sum(len(page.items) for page in self._pages)

    def local_pages(self) -> typing.Tuple[tuple[T, ...], ...]:
        """Return the pages that have been locally cached without making API calls.

        Returns:
            A tuple of locally cached pages, each page is a tuple of items.
        """
        return tuple(tuple(page.items) for page in self._pages)

    def __len__(self) -> int:
        """Return the total number of items reported by the API.

        When not all pages have been fetched this uses the ``total_count``
        value from the pagination metadata returned by the FCA API, so it
        should be treated as an estimate. In rare cases where the backend
        metadata is inconsistent it is still possible to receive an
        ``IndexError`` when accessing an index that is less than this length.
        """
        if self._has_next_page():
            # while the list was not fully fetched,
            # return an estimate based on the total_count from result_info
            out = self._result_info.total_count
        else:
            out = self.local_len()
        return out

    def __repr__(self) -> str:
        return f"MultipageList({self._pages})"

    def model_dump(self, mode: typing.Literal["json", "python"] = "json") -> typing.List[typing.Dict[str, typing.Any]]:
        """Dump the items in the list to a list of dictionaries.

        Returns:
            A list of dictionaries representing the items.
        """
        return [item.model_dump(mode=mode) for item in self.local_items()]

    async def get_all(self) -> typing.Tuple[T, ...]:
        """Fetch all pages and return all items as a list.

        Returns:
            A list of all items.
        """
        await self.fetch_all_pages()
        return self.local_items()
