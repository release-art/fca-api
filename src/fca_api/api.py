"""High-level Financial Services Register API client.

Performs data validation and transformation on top of the raw API client.
"""

import typing

import httpx

from . import raw, types

T = typing.TypeVar("T")
BaseSubclassT = typing.TypeVar("BaseSubclassT", bound=types.base.Base)


class Client:
    """High-level Financial Services Register API client.

    This client wraps the low-level raw client to provide data validation
    and transformation for easier consumption.
    """

    _client: raw.RawClient

    def __init__(
        self,
        credentials: typing.Union[
            typing.Tuple[str, str],
            httpx.AsyncClient,
        ],
        api_limiter: typing.Optional[raw.LimiterContextT] = None,
    ) -> None:
        """Initialize the high-level FCA API client.

        Args:
            api_key: The API key to use for authentication.
        """
        self._client = raw.RawClient(credentials=credentials, api_limiter=api_limiter)

    @property
    def raw_client(self) -> raw.RawClient:
        """Get the underlying raw client.

        Returns:
            The raw FCA API client.
        """
        return self._client

    @property
    def api_version(self) -> str:
        """Get the API version of the underlying raw client.

        Returns:
            The API version string.
        """
        return self._client.api_version

    async def _paginated_search(
        self,
        search_fn: typing.Callable[[int], typing.Awaitable[raw.FcaApiResponse]],
        page_idx: int,
        result_t: typing.Type[BaseSubclassT],
    ) -> types.pagination.FetchPageRvT[BaseSubclassT]:
        """Execute a common search-style search with pagination support & validation.

        Parameters:
            search_fn: The search function to call (with the page number as an argument).
            page_idx: The page index to fetch.
            result_t: The expected type of the result items.
        """
        res = await search_fn(page_idx)
        if res.result_info:
            result_info = types.pagination.PaginatedResultInfo.model_validate(res.result_info)
        else:
            result_info = None
        data = res.data
        assert isinstance(data, list)
        items = [result_t.model_validate(item) for item in res.data]
        return (result_info, items)

    async def search_frn(self, firm_name: str) -> types.pagination.MultipageList[types.search.FirmSearchResult]:
        """Search for a firm by its name."""
        out = types.pagination.MultipageList(
            fetch_page=lambda page_idx: self._paginated_search(
                lambda page_idx: self._client.search_frn(firm_name, page_idx), page_idx, types.search.FirmSearchResult
            ),
        )
        await out._asyinc_init()
        return out

    async def search_irn(
        self, individual_name: str
    ) -> types.pagination.MultipageList[types.search.IndividualSearchResult]:
        """Search for an individual by their name."""
        out = types.pagination.MultipageList(
            fetch_page=lambda page_idx: self._paginated_search(
                lambda page_idx: self._client.search_irn(individual_name, page_idx),
                page_idx,
                types.search.IndividualSearchResult,
            ),
        )
        await out._asyinc_init()
        return out

    async def search_prn(self, fund_name: str) -> types.pagination.MultipageList[types.search.FirmSearchResult]:
        """Search for a firm by its name."""
        out = types.pagination.MultipageList(
            fetch_page=lambda page_idx: self._paginated_search(
                lambda page_idx: self._client.search_prn(fund_name, page_idx), page_idx, types.search.FundSearchResult
            ),
        )
        await out._asyinc_init()
        return out

    async def get_firm(self, frn: str) -> types.firm.FirmDetails:
        """Get firm details by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            The firm's details.
        """
        res = await self._client.get_firm(frn)
        data = res.data
        assert isinstance(data, list) and len(data) == 1, "Expected a single firm detail object in the response data."
        return types.firm.FirmDetails.model_validate(data[0])
