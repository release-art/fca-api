"""High-level Financial Services Register API client.

This module provides the main user-facing interface for interacting with the
FCA Financial Services Register API. It wraps the low-level raw client to provide:

- **Automatic data validation** using Pydantic models
- **Pagination handling** with lazy-loading support
- **Type safety** with comprehensive type hints
- **Error handling** with meaningful exceptions
- **Convenient methods** for common API operations

The `Client` class is the primary entry point for most users, offering methods
for searching firms, individuals, and funds, as well as retrieving detailed
information about specific entities.

Example:
    Basic client usage::

        import fca_api.async_api

        async with fca_api.async_api.Client(
            credentials=("email@example.com", "api_key")
        ) as client:
            # Search for firms by name
            firms = await client.search_frn("revolution")

            # Iterate through paginated results
            async for firm in firms:
                print(f"{firm.name} (FRN: {firm.frn})")

            # Get detailed firm information
            if len(firms) > 0:
                firm_details = await client.get_firm(firms[0].frn)
                print(f"Status: {firm_details.status}")
"""

import logging
import re
import typing

import httpx

from . import raw_api, types

logger = logging.getLogger(__name__)

T = typing.TypeVar("T")
BaseSubclassT = typing.TypeVar("BaseSubclassT", bound=types.base.Base)


class PaginatedResponseHandler(typing.Generic[T]):
    _fetch_page: typing.Callable[[int], typing.Awaitable[raw_api.FcaApiResponse]]
    _parse_data_fn: typing.Callable[[list[dict]], list[T]]

    def __init__(
        self,
        fetch_page: typing.Callable[[int], typing.Awaitable[raw_api.FcaApiResponse]],
        parse_data: typing.Callable[[list[dict]], list[T]],
    ) -> None:
        """Initialize the paginated response handler.

        Args:
            fetch_page: A callable that fetches a page of results given a page index.
        """
        self._fetch_page = fetch_page
        self._parse_data_fn = parse_data

    async def fetch_page(self, page_idx: int) -> types.pagination.FetchPageRvT[BaseSubclassT]:
        """Fetch a page of results.

        Args:
            page_idx: The index of the page to fetch.

        Returns:
            A tuple containing the paginated result info and a list of result items.
        """
        res = await self._fetch_page(page_idx)
        if raw_result_info := res.result_info:
            if not raw_result_info.get("page"):
                # No pagination info present
                result_info = None
            else:
                result_info = types.pagination.PaginatedResultInfo.model_validate(raw_result_info)
        else:
            result_info = None
        data = res.data
        if data is None:
            items = []
        else:
            assert isinstance(data, list | dict)
            items = self._parse_data_fn(res.data)
        return (result_info, items)


class Client:
    """High-level Financial Services Register API client.

    This client wraps the low-level raw client to provide data validation,
    type safety, and convenient pagination handling for the FCA Financial
    Services Register API.

    The client supports async context manager usage for automatic session
    management, or can be used directly with manual session handling.

    Attributes:
        raw_client (raw_api.RawClient): Access to the underlying raw API client.
        api_version (str): The API version being used.

    Example:
        Using as an async context manager::

            async with Client(
                credentials=("email@example.com", "api_key")
            ) as client:
                results = await client.search_frn("barclays")
                async for firm in results:
                    print(firm.name)

        Manual session management::

            client = Client(credentials=("email@example.com", "api_key"))
            try:
                results = await client.search_frn("barclays")
                # Process results...
            finally:
                await client.aclose()

    Note:
        All search methods return `MultipageList` objects that support:

        - Lazy pagination (pages loaded on-demand)
        - Async iteration with `async for`
        - Length checking with `len()`
        - Index access with `[n]`
        - Manual page fetching with `fetch_all_pages()`
    """

    _client: raw_api.RawClient

    def __init__(
        self,
        credentials: typing.Union[
            typing.Tuple[str, str],
            httpx.AsyncClient,
        ],
        api_limiter: typing.Optional[raw_api.LimiterContextT] = None,
    ) -> None:
        """Initialize the high-level FCA API client.

        Args:
            credentials: Authentication credentials. Either:
                - Tuple of (email, api_key) for automatic session creation
                - Pre-configured httpx.AsyncClient with auth headers set
            api_limiter: Optional async context manager for rate limiting.
                Should be a callable returning an async context manager.

        Example:
            With email/key tuple::

                client = Client(
                    credentials=("your.email@example.com", "your_api_key")
                )

            With pre-configured session::

                session = httpx.AsyncClient(headers={
                    "X-AUTH-EMAIL": "your.email@example.com",
                    "X-AUTH-KEY": "your_api_key"
                })
                client = Client(credentials=session)

            With rate limiting::

                from asyncio_throttle import Throttler
                throttler = Throttler(rate_limit=10)  # 10 requests per second

                client = Client(
                    credentials=("email", "key"),
                    api_limiter=throttler
                )
        """
        self._client = raw_api.RawClient(credentials=credentials, api_limiter=api_limiter)

    async def __aenter__(self) -> "Client":
        """Async context manager entry.

        Returns:
            The client instance for use in the async context.

        Example:
            Using as async context manager::

                async with Client(credentials=("email", "key")) as client:
                    results = await client.search_frn("test")
                    async for firm in results:
                        print(firm.name)
                # Client automatically closed here
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit.

        Automatically closes the underlying HTTP session when exiting
        the async context manager.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP session.

        This method should be called when you're finished with the client
        to properly clean up HTTP connections. When using the client as
        an async context manager, this is called automatically.

        Example:
            Manual session management::

                client = Client(credentials=("email", "key"))
                try:
                    results = await client.search_frn("test")
                    # Process results...
                finally:
                    await client.aclose()  # Important!
        """
        await self._client.api_session.aclose()

    @property
    def raw_client(self) -> raw_api.RawClient:
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
        search_fn: typing.Callable[[int], typing.Awaitable[raw_api.FcaApiResponse]],
        page_idx: int,
        result_t: typing.Type[BaseSubclassT],
    ) -> types.pagination.FetchPageRvT[BaseSubclassT]:
        """Execute a paginated search with validation.

        This internal method handles the common pattern of paginated search
        operations by fetching a page, validating the response structure,
        and converting raw API data to typed model instances.

        Args:
            search_fn: Async function that performs the actual API search
                for a given page index.
            page_idx: The page index to fetch (0-based).
            result_t: The Pydantic model class to validate each result item.

        Returns:
            A tuple containing:
            - PaginatedResultInfo or None (pagination metadata)
            - List of validated model instances

        Note:
            This is an internal method used by the public search methods.
            It should not be called directly by users.
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
        """Search for firms by name.

        Performs a text search across firm names in the Financial Services Register
        and returns paginated results with automatic validation.

        Args:
            firm_name: The firm name to search for. Supports partial matches
                and is case-insensitive.

        Returns:
            A lazy-loading paginated list of firm search results. Each result
            contains basic firm information including FRN, name, and status.
            The list supports async iteration and automatic pagination.

        Example:
            Search for firms and iterate through results::

                results = await client.search_frn("Barclays")
                print(f"Found {len(results)} firms")

                async for firm in results:
                    print(f"{firm.name} (FRN: {firm.frn})")
                    print(f"Status: {firm.status}")

            Access specific results by index::

                results = await client.search_frn("revolution")
                if len(results) > 0:
                    first_firm = results[0]
                    print(f"First result: {first_firm.name}")

        Note:
            The search is performed against the FCA's live database and
            results may change between calls. Large result sets are
            automatically paginated.
        """
        out = types.pagination.MultipageList(
            fetch_page=lambda page_idx: self._paginated_search(
                lambda page_idx: self._client.search_frn(firm_name, page_idx), page_idx, types.search.FirmSearchResult
            ),
        )
        await out._async_init()
        return out

    async def search_irn(
        self, individual_name: str
    ) -> types.pagination.MultipageList[types.search.IndividualSearchResult]:
        """Search for individuals by name.

        Performs a text search across individual names in the Financial Services
        Register and returns paginated results with automatic validation.

        Args:
            individual_name: The individual name to search for. Supports partial
                matches and is case-insensitive.

        Returns:
            A lazy-loading paginated list of individual search results. Each result
            contains basic individual information including IRN, name, and status.
            The list supports async iteration and automatic pagination.

        Example:
            Search for individuals::

                results = await client.search_irn("John Smith")
                print(f"Found {len(results)} individuals")

                async for individual in results:
                    print(f"{individual.name} (IRN: {individual.irn})")
                    print(f"Status: {individual.status}")

        Note:
            Individual searches may return many results due to common names.
            Use additional filtering or get detailed individual information
            to narrow down results.
        """
        out = types.pagination.MultipageList(
            fetch_page=lambda page_idx: self._paginated_search(
                lambda page_idx: self._client.search_irn(individual_name, page_idx),
                page_idx,
                types.search.IndividualSearchResult,
            ),
        )
        await out._async_init()
        return out

    async def search_prn(self, fund_name: str) -> types.pagination.MultipageList[types.search.FundSearchResult]:
        """Search for funds by name.

        Performs a text search across fund names in the Financial Services
        Register and returns paginated results with automatic validation.

        Args:
            fund_name: The fund name to search for. Supports partial matches
                and is case-insensitive.

        Returns:
            A lazy-loading paginated list of fund search results. Each result
            contains basic fund information including PRN, name, and status.
            The list supports async iteration and automatic pagination.

        Example:
            Search for funds::

                results = await client.search_prn("Vanguard")
                print(f"Found {len(results)} funds")

                async for fund in results:
                    print(f"{fund.name} (PRN: {fund.prn})")
                    print(f"Status: {fund.status}")

        Note:
            Fund searches include various types of collective investment schemes
            and other financial products registered with the FCA.
        """
        out = types.pagination.MultipageList(
            fetch_page=lambda page_idx: self._paginated_search(
                lambda page_idx: self._client.search_prn(fund_name, page_idx), page_idx, types.search.FundSearchResult
            ),
        )
        await out._async_init()
        return out

    async def get_firm(self, frn: str) -> types.firm.FirmDetails:
        """Get comprehensive firm details by FRN.

        Retrieves detailed information about a specific firm using its
        Firm Reference Number (FRN).

        Args:
            frn: The Firm Reference Number (FRN) of the firm to retrieve.
                Must be a valid FRN string (typically 6-7 digits).

        Returns:
            Complete firm details including status, permissions, contact
            information, and regulatory information.

        Raises:
            AssertionError: If the API response doesn't contain exactly one firm.
            ValidationError: If the firm data doesn't match expected schema.

        Example:
            Get detailed firm information::

                firm = await client.get_firm("123456")
                print(f"Name: {firm.name}")
                print(f"Status: {firm.status}")
                print(f"Effective Date: {firm.effective_date}")
                print(f"Permissions: {len(firm.permissions)}")

        Note:
            This method requires a valid FRN. Use `search_frn()` first if you
            only have the firm name.
        """
        res = await self._client.get_firm(frn)
        data = res.data
        assert isinstance(data, list) and len(data) == 1, "Expected a single firm detail object in the response data."
        return types.firm.FirmDetails.model_validate(data[0])

    def _parse_firm_names_pg(self, data: list[dict]) -> list[types.firm.FirmNameAlias]:
        out = []
        for el in data:
            if not isinstance(el, dict):
                logger.warning(f"Unexpected firm name entry format: {el!r}")
                continue
            for key, value in el.items():
                key = key.lower().strip()
                if key == "previous names":
                    assert isinstance(value, list)
                    for value_el in value:
                        out.append(value_el | {"fca_api_address_type": "previous"})
                elif key == "current names":
                    assert isinstance(value, list)
                    for value_el in value:
                        out.append(value_el | {"fca_api_address_type": "current"})
                else:
                    logger.warning(f"Unexpected firm name entry field: {key}={value!r}")

        return [types.firm.FirmNameAlias.model_validate(el) for el in out]

    async def get_firm_names(self, frn: str) -> types.pagination.MultipageList[types.firm.FirmNameAlias]:
        """Get firm names by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's names.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_names(frn, page=page_idx),
                self._parse_firm_names_pg,
            ).fetch_page,
        )
        await out._async_init()
        return out

    def _parse_firm_addresses_pg(self, data: list[dict]) -> list[types.firm.FirmAddress]:
        """Get firm addresses by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's addresses.
        """
        address_line_re = re.compile(r"address \s+ line \s+ (\d+)", re.IGNORECASE | re.VERBOSE)
        out_items = []
        for raw_row in data:
            address_lines: list[tuple[int, str]] = []
            for key in tuple(raw_row.keys()):
                if not isinstance(key, str):
                    continue
                if match := address_line_re.match(key):
                    line_idx = int(match.group(1))
                    line_value = raw_row.pop(key)
                    if not line_value:
                        # Skip empty address lines
                        continue
                    address_lines.append((line_idx, line_value))
            raw_row["address_lines"] = [line for _idx, line in sorted(address_lines, key=lambda x: x[0])]
        return [types.firm.FirmAddress.model_validate(item) for item in data]

    async def get_firm_addresses(self, frn: str) -> types.pagination.MultipageList[types.firm.FirmAddress]:
        """Get firm addresses by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's addresses.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_addresses(frn, page=page_idx),
                self._parse_firm_addresses_pg,
            ).fetch_page,
        )
        await out._async_init()
        return out

    def _parse_firm_controlled_functions_pg(self, data: list[dict]) -> list[types.firm.FirmControlledFunction]:
        """Get firm controlled functions by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's controlled functions.
        """
        out_items: list[types.firm.FirmControlledFunction] = []
        for data_row in data:
            item_data = {}
            if not isinstance(data_row, dict):
                logger.warning(f"Unexpected firm controlled function entry format: {data_row!r}")
                continue
            for key, value in data_row.items():
                item_data["fca_api_lst_type"] = key.lower().strip()
                if not isinstance(value, dict):
                    logger.warning(f"Unexpected firm controlled function entry value format: {value!r}")
                    continue
                for subkey, subvalue in value.items():
                    subkey_el = subkey.lower().strip()
                    subval_name_el = subvalue.get("name", subkey_el).lower().strip()
                    if subkey_el != subval_name_el:
                        logger.warning(
                            f"Mismatch in controlled function subkey and name: {subkey_el!r} != {subval_name_el!r}"
                        )
                    out_items.append(types.firm.FirmControlledFunction.model_validate(item_data | subvalue))
        return out_items

    async def get_firm_controlled_functions(
        self, frn: str
    ) -> types.pagination.MultipageList[types.firm.FirmControlledFunction]:
        """Get firm controlled functions by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's controlled functions.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_controlled_functions(frn, page=page_idx),
                self._parse_firm_controlled_functions_pg,
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_firm_individuals(self, frn: str) -> types.pagination.MultipageList[types.firm.FirmIndividual]:
        """Get firm individuals by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's individuals.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_individuals(frn, page=page_idx),
                lambda data: [types.firm.FirmIndividual.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    def _parse_firm_permissions_pg(self, data: dict) -> list[types.firm.FirmPermission]:
        out = []
        unwrap_fields = [
            "cbtl status",
            "cbtl effective date",
            "acting as a cbtl administrator",
            "acting as a cbtl advisor",
            "acting as a cbtl arranger",
            "acting as a cbtl lender",
        ]
        for perm_name, perm_data in data.items():
            perm_record = {"fca_api_permission_name": perm_name}
            if not isinstance(perm_data, list):
                logger.warning(f"Unexpected firm permission entry format: {perm_data!r}")
                continue
            for perm_data_el in perm_data:
                if not isinstance(perm_data_el, dict):
                    logger.warning(f"Unexpected firm permission data element format: {perm_data_el!r}")
                    continue
                perm_record = perm_record | perm_data_el
            for key, value in list(perm_record.items()):
                key_lower = key.lower().strip()
                if key_lower in unwrap_fields:
                    assert isinstance(value, list) and len(value) == 1, (
                        f"Expected a single value list for field {key_lower!r}"
                    )
                    perm_record[key] = value[0]
            out.append(types.firm.FirmPermission.model_validate(perm_record))
        return out

    async def get_firm_permissions(self, frn: str) -> types.pagination.MultipageList[types.firm.FirmPermission]:
        """Get firm permissions by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's permissions.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_permissions(frn, page=page_idx),
                self._parse_firm_permissions_pg,
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_firm_requirements(self, frn: str) -> types.pagination.MultipageList[types.firm.FirmRequirement]:
        """Get firm requirements by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's requirements.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_requirements(frn, page=page_idx),
                lambda data: [types.firm.FirmRequirement.model_validate(row) for row in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_firm_requirement_investment_types(
        self, frn: str, req_ref: str
    ) -> types.pagination.MultipageList[types.firm.FirmRequirementInvestmentType]:
        """Get investment types for a specific firm requirement.

        Retrieves the investment types associated with a particular firm
        requirement, identified by its requirement reference.

        Args:
            frn: The Firm Reference Number (FRN) of the firm.
            req_ref: The requirement reference identifier.

        Returns:
            A paginated list of investment types associated with the requirement.
            Each entry contains details about permitted investment activities.

        Example:
            Get investment types for a requirement::

                # First get firm requirements
                requirements = await client.get_firm_requirements("123456")
                if len(requirements) > 0:
                    req_ref = requirements[0].requirement_reference

                    # Get investment types for this requirement
                    investment_types = await client.get_firm_requirement_investment_types(
                        "123456", req_ref
                    )
                    async for inv_type in investment_types:
                        print(f"Investment Type: {inv_type.investment_type}")

        Note:
            The req_ref must be obtained from a firm's requirements list.
            Not all requirements have associated investment types.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_requirement_investment_types(frn, req_ref, page=page_idx),
                lambda data: [types.firm.FirmRequirementInvestmentType.model_validate(row) for row in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_firm_regulators(self, frn: str) -> types.pagination.MultipageList[types.firm.FirmRegulator]:
        """Get firm regulators by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's regulators.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_regulators(frn, page=page_idx),
                lambda data: [types.firm.FirmRegulator.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    def _parse_firm_passports_pg(self, data: list[dict]) -> list[types.firm.FirmPassport]:
        out = []
        for el in data:
            if not isinstance(el, dict):
                logger.warning(f"Unexpected firm passport entry format: {el!r}")
                continue
            for key, value in el.items():
                key = key.lower().strip()
                if key == "passports":
                    assert isinstance(value, list)
                    for value_el in value:
                        out.append(types.firm.FirmPassport.model_validate(value_el))
                else:
                    logger.warning(f"Unexpected firm passport entry field: {key}={value!r}")
        return out

    async def get_firm_passports(self, frn: str) -> types.pagination.MultipageList[types.firm.FirmPassport]:
        """Get firm passports by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's passports.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_passports(frn, page=page_idx),
                self._parse_firm_passports_pg,
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_firm_passport_permissions(
        self, frn: str, country: str
    ) -> types.pagination.MultipageList[types.firm.FirmPassportPermission]:
        """Get firm passport permissions by FRN and country.

        Args:
            frn: The firm's FRN.
            country: The country code.
        Returns:
            A list of the firm's passport permissions for the specified country.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_passport_permissions(frn, country, page=page_idx),
                lambda data: [types.firm.FirmPassportPermission.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_firm_waivers(self, frn: str) -> types.pagination.MultipageList[types.firm.FirmWaiver]:
        """Get firm waivers by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's waivers.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_waivers(frn, page=page_idx),
                lambda data: [types.firm.FirmWaiver.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_firm_exclusions(self, frn: str) -> types.pagination.MultipageList[types.firm.FirmExclusion]:
        """Get firm exclusions by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's exclusions.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_exclusions(frn, page=page_idx),
                lambda data: [types.firm.FirmExclusion.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_firm_disciplinary_history(
        self, frn: str
    ) -> types.pagination.MultipageList[types.firm.FirmDisciplinaryRecord]:
        """Get disciplinary history records for a firm.

        Retrieves all disciplinary actions, warnings, and regulatory measures
        taken against the firm by the FCA or other regulatory bodies.

        Args:
            frn: The Firm Reference Number (FRN) of the firm.

        Returns:
            A paginated list of disciplinary records including dates, types
            of action, and details of regulatory measures.

        Example:
            Review a firm's disciplinary history::

                disciplinary_records = await client.get_firm_disciplinary_history("123456")
                if len(disciplinary_records) > 0:
                    async for record in disciplinary_records:
                        print(f"Date: {record.date}")
                        print(f"Action: {record.action_type}")
                        print(f"Details: {record.details}")
                else:
                    print("No disciplinary history found")

        Note:
            An empty result indicates the firm has no recorded disciplinary
            actions, which is common for many firms.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_disciplinary_history(frn, page=page_idx),
                lambda data: [types.firm.FirmDisciplinaryRecord.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    def _parse_firm_appointed_representatives_pg(
        self, data: dict[list[dict]]
    ) -> list[types.firm.FirmAppointedRepresentative]:
        out = []
        for key, items in data.items():
            if not items:
                continue
            key = key.lower().strip()
            key = {
                "currentappointedrepresentatives": "current",
                "previousappointedrepresentatives": "previous",
            }.get(key, key)
            assert isinstance(items, list), items
            for item in items:
                out.append(types.firm.FirmAppointedRepresentative.model_validate({"fca_api_lst_type": key} | item))
        return out

    async def get_firm_appointed_representatives(
        self, frn: str
    ) -> types.pagination.MultipageList[types.firm.FirmAppointedRepresentative]:
        """Get firm appointed representatives by FRN.

        Args:
            frn: The firm's FRN.

        Returns:
            A list of the firm's appointed representatives.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_firm_appointed_representatives(frn, page=page_idx),
                self._parse_firm_appointed_representatives_pg,
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_individual(self, irn: str) -> types.individual.Individual:
        """Get individual details by IRN.

        Args:
            irn: The individual's IRN.

        Returns:
            The individual's details.
        """
        res = await self._client.get_individual(irn)
        data = res.data
        assert isinstance(data, list) and len(data) == 1, (
            "Expected a single individual detail object in the response data."
        )
        return types.individual.Individual.model_validate(data[0]["Details"])

    def _parse_individual_controlled_functions_pg(
        self, data: list[dict]
    ) -> list[types.individual.IndividualControlledFunction]:
        assert isinstance(data, list) and len(data) == 1, (
            "Expected a single individual detail object in the response data."
        )
        out = []
        for row in data:
            if not isinstance(row, dict):
                logger.warning(f"Unexpected individual controlled function entry format: {row!r}")
                continue
            for key, value in row.items():
                key = key.lower().strip()
                if not isinstance(value, dict):
                    logger.warning(f"Unexpected individual controlled function entry value format: {value!r}")
                    continue
                for fn_name, fn_data in value.items():
                    if fn_name != fn_data.get("Name", None):
                        logger.warning(
                            "Mismatch in controlled function name and data name: "
                            f"{fn_name!r} != {fn_data.get('name')!r}"
                        )
                    out.append(
                        types.individual.IndividualControlledFunction.model_validate(
                            {
                                "fca_api_lst_type": key,
                            }
                            | fn_data
                        )
                    )
        return out

    async def get_individual_controlled_functions(
        self, irn: str
    ) -> types.pagination.MultipageList[types.individual.IndividualControlledFunction]:
        """Get controlled functions for an individual.

        Retrieves all controlled functions (senior management functions and
        certification functions) held by an individual across all firms.

        Args:
            irn: The Individual Reference Number (IRN) of the individual.

        Returns:
            A paginated list of controlled functions including function types,
            associated firms, and status information.

        Example:
            Review an individual's controlled functions::

                functions = await client.get_individual_controlled_functions("ABC123")
                async for function in functions:
                    print(f"Function: {function.function_name}")
                    print(f"Firm: {function.firm_name}")
                    print(f"Status: {function.status}")
                    print(f"Start Date: {function.start_date}")

        Note:
            Controlled functions are key regulatory roles that require FCA
            approval. This includes roles like CEO, CFO, compliance officers,
            and customer-facing roles.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_individual_controlled_functions(irn, page=page_idx),
                self._parse_individual_controlled_functions_pg,
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_individual_disciplinary_history(
        self, irn: str
    ) -> types.pagination.MultipageList[types.individual.IndividualDisciplinaryRecord]:
        """Get disciplinary history records for an individual.

        Retrieves all disciplinary actions, warnings, and regulatory measures
        taken against the individual by the FCA or other regulatory bodies.

        Args:
            irn: The Individual Reference Number (IRN) of the individual.

        Returns:
            A paginated list of disciplinary records including dates, types
            of action, details, and outcomes of regulatory measures.

        Example:
            Check an individual's disciplinary history::

                records = await client.get_individual_disciplinary_history("ABC123")
                if len(records) > 0:
                    async for record in records:
                        print(f"Date: {record.date}")
                        print(f"Action: {record.action_type}")
                        print(f"Outcome: {record.outcome}")
                else:
                    print("No disciplinary history found")

        Note:
            An empty result indicates the individual has no recorded
            disciplinary actions. Disciplinary records can affect an
            individual's ability to perform regulated activities.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_individual_disciplinary_history(irn, page=page_idx),
                lambda data: [types.individual.IndividualDisciplinaryRecord.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_fund(self, prn: str) -> types.products.ProductDetails:
        """Get fund details by PRN.

        Args:
            prn: The fund's PRN.

        Returns:
            The fund's details.
        """
        res = await self._client.get_fund(prn)
        data = res.data
        assert isinstance(data, list) and len(data) == 1, "Expected a single fund detail object in the response data."
        return types.products.ProductDetails.model_validate(data[0])

    async def get_fund_names(self, prn: str) -> types.pagination.MultipageList[types.products.ProductNameAlias]:
        """Get fund names by PRN.

        Args:
            prn: The fund's PRN.

        Returns:
            A list of the fund's names.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_fund_names(prn, page=page_idx),
                lambda data: [types.products.ProductNameAlias.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_fund_subfunds(self, prn: str) -> types.pagination.MultipageList[types.products.SubFundDetails]:
        """Get fund sub-funds by PRN.

        Args:
            prn: The fund's PRN.
        Returns:
            A list of the fund's sub-funds.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_fund_subfunds(prn, page=page_idx),
                lambda data: [types.products.SubFundDetails.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out

    async def get_regulated_markets(self) -> types.pagination.MultipageList[types.markets.RegulatedMarket]:
        """Get regulated markets.

        Returns:
            A list of regulated markets.
        """
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_regulated_markets(page=page_idx),
                lambda data: [types.markets.RegulatedMarket.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out
