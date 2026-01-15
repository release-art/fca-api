""""""

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
    next: typing.Optional[pydantic.HttpUrl] = None
    previous: typing.Optional[pydantic.HttpUrl] = None
    page: int
    per_page: int
    total_count: int

    @property
    def total_pages(self) -> int:
        """int: The total number of pages available."""
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
    """A list that represents a multipage API response.

    This class can be extended in the future to include pagination metadata.
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

    async def _asyinc_init(self) -> None:
        # Fetch the first page to initialize the result info.
        await self._fetch_page_to_item_idx(0)

    async def fetch_all_pages(self) -> None:
        """Fetch all pages from the API."""
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
                    self._pages.append(FetchedPageData(items=new_items, page_info=new_page_info))
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
        """
        Return the estimated total number of items available from the API.

        Please ntoe that the result_info.total_count may not always be accurate,
        so it is possible to get an IndexError when accessing an index less than this length.
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
