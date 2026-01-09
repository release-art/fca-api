"""High-level Financial Services Register API client.

Performs data validation and transformation on top of the raw API client.
"""
import typing
import httpx
import warnings
from . import raw, types

T = typing.TypeVar('T')


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
    
    def _check_api_version(self, request: raw.FcaApiResponse, expected: str) -> None:
        """Check that the API version in the response matches the expected version.

        Args:
            request: The API response to check.
            expected: The expected API version.
        """
        if request.status != expected:
            warnings.warn(
                f"API version mismatch: expected {expected}, got {request.status} (request url: {request.url})",
                RuntimeWarning,
            )
    
    async def search_frn(self, firm_name: str, seed_page_idx: int|None=None) -> types.pagination.MultipageList[types.api.FirmSearchResult]:
        """Search for a firm by its name."""
        res = await self._client.search_frn(firm_name, page=seed_page_idx)
        self._check_api_version(res, expected=types.api.FirmSearchResult._expected_api_version)
        result_info = types.pagination.PaginatedResultInfo.model_validate(res.result_info)
        data = res.data
        assert isinstance(data, list)
        return types.pagination.MultipageList(
            items=[
                types.api.FirmSearchResult.model_validate(item)
                for item in res.data
            ],
            result_info=result_info,
            fetch_page=lambda page_idx: self.search_frn(firm_name, seed_page_idx=page_idx),
        )

    async def search_irn(self, individual_name: str, seed_page_idx: int|None=None) -> types.pagination.MultipageList[types.api.IndividualSearchResult]:
        """Search for an individual by their name."""
        res = await self._client.search_irn(individual_name, page=seed_page_idx)
        self._check_api_version(res, expected=types.api.IndividualSearchResult._expected_api_version)
        result_info = types.pagination.PaginatedResultInfo.model_validate(res.result_info)
        data = res.data
        assert isinstance(data, list)
        return types.pagination.MultipageList(
            items=[
                types.api.IndividualSearchResult.model_validate(item)
                for item in res.data
            ],
            result_info=result_info,
            fetch_page=lambda page_idx: self.search_irn(individual_name, seed_page_idx=page_idx),
        )