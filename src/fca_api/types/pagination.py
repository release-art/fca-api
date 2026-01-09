""""""

import typing
import pydantic
import asyncio

T = typing.TypeVar('T')

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
        return super().model_validate({key.lower().strip(): value for (key, value) in data.items()})

class MultipageList(typing.Generic[T]):
    """A list that represents a multipage API response.

    This class can be extended in the future to include pagination metadata.
    """

    _items: typing.List[T]
    _fetch_page_cb: typing.Callable[[int], typing.Awaitable["MultipageList[T]"]]
    _lock: asyncio.Lock
    _result_info: PaginatedResultInfo
    # _fetched_page_indices - a set of 1-based page indices that have been fetched
    _fetched_page_indices: typing.Set[int]

    def __init__(
        self,
        /,
        items: typing.Sequence[T],
        result_info: PaginatedResultInfo,
        fetch_page: typing.Callable[[int], typing.Awaitable["MultipageList[T]"]],
    ) -> None:
        self._items = list(items)
        self._lock = asyncio.Lock()
        self._result_info = result_info
        self._fetch_page_cb = fetch_page
        self._fetched_page_indices = {result_info.page}

    async def _fetch_page_to_item_idx(self, desired_item_idx: int):
        """Fetch a specific page from the API if it is not already cached.

        Args:
            desired_item_idx: The index of the desired item to fetch.
        """
        if len(self._items) > desired_item_idx:
            return
        async with self._lock:
            # Double-check after acquiring the lock
            while len(self._items) <= desired_item_idx:
                last_fetched_page = max(self._fetched_page_indices)
                new_page = await self._fetch_page_cb(last_fetched_page + 1)
                assert new_page._result_info.page == last_fetched_page + 1, (
                    new_page._result_info.page,
                    last_fetched_page + 1,
                )
                self._items.extend(new_page.local_items())
                self._fetched_page_indices.add(new_page._result_info.page)
        return new_page

    async def __getitem__(self, index: int) -> T:
        await self._fetch_page_to_item_idx(index)
        return self._items[index]
    
    async def __aiter__(self) -> typing.AsyncIterator[T]:
        for idx in range(len(self)):
            yield await self[idx]

    def local_items(self) -> typing.Tuple[T, ...]:
        """Return the items that have been locally cached without making API calls.

        Returns:
            A tuple of locally cached items.
        """
        return tuple(self._items)

    def __len__(self) -> int:
        return self._result_info.total_count

    def __repr__(self) -> str:
        return f"MultipageList({super().__repr__()})"