"""High-level Financial Services Register API client.

Wraps the raw HTTP client to provide Pydantic-typed responses, cursor-based
pagination, and an optional :class:`~fca_api.types.pagination.PageTokenSerializer`
hook for signing or encrypting pagination tokens. See :class:`Client`.
"""

import contextvars
import logging
import re
import threading
import typing

import httpx

from . import raw_api, types
from ._paginate import current_resume_state, paginated

logger = logging.getLogger(__name__)

T = typing.TypeVar("T")
BaseSubclassT = typing.TypeVar("BaseSubclassT", bound=types.base.Base)


#: Resume position published by :meth:`Client.fetch_next_page` for
#: :meth:`Client._fetch_paginated` to read. ``None`` on a fresh call.
_resume_from_ctx: contextvars.ContextVar[typing.Optional[types.pagination._PageState]] = contextvars.ContextVar(
    "fca_api_resume_from_ctx", default=None
)


class Client:
    """High-level Financial Services Register API client.

    Each paginated endpoint returns a :class:`~fca_api.types.pagination.MultipageList`
    holding one batch and a ``pagination.next_page`` cursor. Advance with
    :meth:`fetch_next_page`, or pass ``result_count=N`` to collect at least
    ``N`` items in a single call.

    Example::

        async with Client(credentials=("email@example.com", "api_key")) as client:
            page = await client.search_frn("barclays")
            for firm in page.data:
                print(firm.name)
    """

    _client: raw_api.RawClient
    _lock: threading.Lock
    _ctx_enter_count: int
    _page_token_serializer: typing.Optional[types.pagination.PageTokenSerializer]

    #: Paginated methods :meth:`fetch_next_page` may dispatch to. A tampered
    #: or malformed token cannot reach arbitrary attributes.
    _RESUMABLE_ENDPOINTS: typing.ClassVar[frozenset[str]] = frozenset(
        {
            "search_frn",
            "search_irn",
            "search_prn",
            "get_firm_names",
            "get_firm_addresses",
            "get_firm_controlled_functions",
            "get_firm_individuals",
            "get_firm_permissions",
            "get_firm_requirements",
            "get_firm_requirement_investment_types",
            "get_firm_regulators",
            "get_firm_passports",
            "get_firm_passport_permissions",
            "get_firm_waivers",
            "get_firm_exclusions",
            "get_firm_disciplinary_history",
            "get_firm_appointed_representatives",
            "get_individual_controlled_functions",
            "get_individual_disciplinary_history",
            "get_fund_names",
            "get_fund_subfunds",
            "get_regulated_markets",
        }
    )

    def __init__(
        self,
        credentials: typing.Union[
            typing.Tuple[str, str],
            httpx.AsyncClient,
        ],
        api_limiter: typing.Optional[raw_api.LimiterContextT] = None,
        page_token_serializer: typing.Optional[types.pagination.PageTokenSerializer] = None,
    ) -> None:
        """Initialize the client.

        Args:
            credentials: ``(email, api_key)`` tuple, or a pre-configured
                ``httpx.AsyncClient`` with auth headers set.
            api_limiter: Optional zero-arg callable returning an async context
                manager; entered around each HTTP request.
            page_token_serializer: Optional hook to sign/encrypt pagination
                tokens — outgoing tokens pass through ``serialize`` and
                incoming tokens through ``deserialize``.
        """
        self._client = raw_api.RawClient(credentials=credentials, api_limiter=api_limiter)
        self._lock = threading.Lock()
        self._ctx_enter_count = 0
        self._page_token_serializer = page_token_serializer

    async def __aenter__(self) -> "Client":
        with self._lock:
            self._ctx_enter_count += 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        with self._lock:
            self._ctx_enter_count -= 1
            if self._ctx_enter_count <= 0:
                logger.debug("Context manager exit: closing HTTP session")
                await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying HTTP session."""
        await self._client.api_session.aclose()

    @property
    def raw_client(self) -> raw_api.RawClient:
        """The underlying raw API client."""
        return self._client

    @property
    def api_version(self) -> str:
        """The API version string."""
        return self._client.api_version

    # ------------------------------------------------------------------
    # Token encode / decode helpers
    # ------------------------------------------------------------------

    def _encode_next_page(self, state: types.pagination._PageState) -> types.pagination.NextPageToken:
        """Encode a page state into an externally-safe NextPageToken."""
        raw = state.encode()
        if self._page_token_serializer is not None:
            return self._page_token_serializer.serialize(raw)
        return raw

    def _decode_next_page(self, token: types.pagination.NextPageToken) -> types.pagination._PageState:
        """Decode a caller-provided NextPageToken into internal page state."""
        raw = token
        if self._page_token_serializer is not None:
            raw = self._page_token_serializer.deserialize(token)
        return types.pagination._PageState.decode(raw)

    # ------------------------------------------------------------------
    # Core pagination helper
    # ------------------------------------------------------------------

    async def _fetch_paginated(
        self,
        fetch_page_fn: typing.Callable[[int], typing.Awaitable[raw_api.FcaApiResponse]],
        parse_data_fn: typing.Callable[[typing.Union[list, dict]], list],
        result_count: int,
    ) -> types.pagination.MultipageList:
        """Fetch pages until ``result_count`` items are collected or none remain.

        Starts from the resume position on :data:`_resume_from_ctx` (or page 1)
        and stamps the outgoing cursor with the endpoint and arguments
        published by the surrounding :func:`paginated` decorator. Always
        fetches at least one page.
        """
        resume = current_resume_state()
        page_state = _resume_from_ctx.get() or types.pagination._PageState.first()
        current_page = page_state.page
        items: list = []
        last_info: typing.Optional[types.pagination.PaginatedResultInfo] = None
        has_next = False

        while True:
            response = await fetch_page_fn(current_page)

            # Parse result_info from the response (keys may be mixed-case; some endpoints
            # return empty strings for page/per_page when no pagination applies)
            if raw_info := response.result_info:
                normalized = {k.lower().strip(): v for k, v in raw_info.items()}
                if normalized.get("page"):
                    last_info = types.pagination.PaginatedResultInfo.model_validate(raw_info)

            # Parse data items
            data = response.data
            if data is not None:
                assert isinstance(data, (list, dict))
                items.extend(parse_data_fn(data))

            # Determine whether a next page exists
            has_next = last_info is not None and last_info.next is not None and last_info.page < last_info.total_pages

            # Stop when we have enough items or there are no more pages
            if not has_next or len(items) >= result_count:
                break

            current_page += 1

        next_page_out: typing.Optional[types.pagination.NextPageToken] = None
        if has_next and last_info is not None:
            next_state = types.pagination._PageState(
                page=last_info.page + 1,
                endpoint=resume.endpoint,
                params=resume.params,
            )
            next_page_out = self._encode_next_page(next_state)

        return types.pagination.MultipageList(
            data=tuple(items),
            pagination=types.pagination.PaginationInfo(
                has_next=has_next,
                next_page=next_page_out,
                size=last_info.total_count if last_info is not None else None,
            ),
        )

    # ------------------------------------------------------------------
    # Next-page dispatcher
    # ------------------------------------------------------------------

    async def fetch_next_page(
        self,
        next_page: types.pagination.NextPageToken,
    ) -> types.pagination.MultipageList:
        """Fetch the next page given a ``pagination.next_page`` token.

        The token embeds the originating endpoint and arguments, so resuming
        needs only the token — no need to retain the original query. Suitable
        for stateless services that hand the cursor to a caller and resume on
        a later request.

        Raises:
            ValueError: If the token does not name a resumable endpoint
                (position-only, malformed, or tampered).
        """
        state = self._decode_next_page(next_page)
        if state.endpoint not in self._RESUMABLE_ENDPOINTS:
            raise ValueError(
                f"next_page token does not identify a resumable endpoint (got {state.endpoint!r}); "
                "it may be position-only, malformed, or tampered."
            )
        method = getattr(self, state.endpoint)
        ctx_token = _resume_from_ctx.set(state)
        try:
            return await method(**state.params)
        finally:
            _resume_from_ctx.reset(ctx_token)

    # ------------------------------------------------------------------
    # Search endpoints
    # ------------------------------------------------------------------

    @paginated()
    async def search_frn(
        self,
        firm_name: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.search.FirmSearchResult]:
        """Search for firms by name (partial match, case-insensitive).

        Args:
            firm_name: Firm name (or substring) to search for.
            result_count: Minimum items to collect; the client issues multiple
                API calls if needed. Defaults to 1 (one API page).
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.search_frn(firm_name, p),
            parse_data_fn=lambda data: [types.search.FirmSearchResult.model_validate(item) for item in data],
            result_count=result_count,
        )

    @paginated()
    async def search_irn(
        self,
        individual_name: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.search.IndividualSearchResult]:
        """Search for individuals by name.

        Args:
            individual_name: Individual name to search for.
            result_count: Minimum number of results to return.

        Returns:
            A page of individual search results with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.search_irn(individual_name, p),
            parse_data_fn=lambda data: [types.search.IndividualSearchResult.model_validate(item) for item in data],
            result_count=result_count,
        )

    @paginated()
    async def search_prn(
        self,
        fund_name: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.search.FundSearchResult]:
        """Search for funds by name.

        Args:
            fund_name: Fund name to search for.
            result_count: Minimum number of results to return.

        Returns:
            A page of fund search results with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.search_prn(fund_name, p),
            parse_data_fn=lambda data: [types.search.FundSearchResult.model_validate(item) for item in data],
            result_count=result_count,
        )

    # ------------------------------------------------------------------
    # Firm detail endpoints
    # ------------------------------------------------------------------

    async def get_firm(self, frn: str) -> types.firm.FirmDetails:
        """Get comprehensive firm details by FRN.

        Args:
            frn: The Firm Reference Number (FRN).

        Returns:
            Complete firm details.
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

    @paginated()
    async def get_firm_names(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmNameAlias]:
        """Get firm names (current and previous) by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm name aliases with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_names(frn, page=p),
            parse_data_fn=self._parse_firm_names_pg,
            result_count=result_count,
        )

    def _parse_firm_addresses_pg(self, data: list[dict]) -> list[types.firm.FirmAddress]:
        address_line_re = re.compile(r"address \s+ line \s+ (\d+)", re.IGNORECASE | re.VERBOSE)
        for raw_row in data:
            address_lines: list[tuple[int, str]] = []
            for key in tuple(raw_row.keys()):
                if not isinstance(key, str):
                    continue
                if match := address_line_re.match(key):
                    line_idx = int(match.group(1))
                    line_value = raw_row.pop(key)
                    if not line_value:
                        continue
                    address_lines.append((line_idx, line_value))
            raw_row["address_lines"] = [line for _idx, line in sorted(address_lines, key=lambda x: x[0])]
        return [types.firm.FirmAddress.model_validate(item) for item in data]

    @paginated()
    async def get_firm_addresses(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmAddress]:
        """Get firm addresses by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm addresses with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_addresses(frn, page=p),
            parse_data_fn=self._parse_firm_addresses_pg,
            result_count=result_count,
        )

    def _parse_firm_controlled_functions_pg(self, data: list[dict]) -> list[types.firm.FirmControlledFunction]:
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

    @paginated()
    async def get_firm_controlled_functions(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmControlledFunction]:
        """Get firm controlled functions by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm controlled functions with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_controlled_functions(frn, page=p),
            parse_data_fn=self._parse_firm_controlled_functions_pg,
            result_count=result_count,
        )

    @paginated()
    async def get_firm_individuals(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmIndividual]:
        """Get individuals associated with a firm by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm individuals with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_individuals(frn, page=p),
            parse_data_fn=lambda data: [types.firm.FirmIndividual.model_validate(item) for item in data],
            result_count=result_count,
        )

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

    @paginated()
    async def get_firm_permissions(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmPermission]:
        """Get firm permissions by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm permissions with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_permissions(frn, page=p),
            parse_data_fn=self._parse_firm_permissions_pg,
            result_count=result_count,
        )

    @paginated()
    async def get_firm_requirements(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmRequirement]:
        """Get firm requirements by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm requirements with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_requirements(frn, page=p),
            parse_data_fn=lambda data: [types.firm.FirmRequirement.model_validate(row) for row in data],
            result_count=result_count,
        )

    @paginated()
    async def get_firm_requirement_investment_types(
        self,
        frn: str,
        req_ref: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmRequirementInvestmentType]:
        """Get investment types for a specific firm requirement.

        Args:
            frn: The Firm Reference Number (FRN) of the firm.
            req_ref: The requirement reference identifier.
            result_count: Minimum number of results to return.

        Returns:
            A page of investment types with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_requirement_investment_types(frn, req_ref, page=p),
            parse_data_fn=lambda data: [types.firm.FirmRequirementInvestmentType.model_validate(row) for row in data],
            result_count=result_count,
        )

    @paginated()
    async def get_firm_regulators(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmRegulator]:
        """Get firm regulators by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm regulators with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_regulators(frn, page=p),
            parse_data_fn=lambda data: [types.firm.FirmRegulator.model_validate(item) for item in data],
            result_count=result_count,
        )

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

    @paginated()
    async def get_firm_passports(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmPassport]:
        """Get firm passports by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm passports with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_passports(frn, page=p),
            parse_data_fn=self._parse_firm_passports_pg,
            result_count=result_count,
        )

    @paginated()
    async def get_firm_passport_permissions(
        self,
        frn: str,
        country: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmPassportPermission]:
        """Get firm passport permissions by FRN and country.

        Args:
            frn: The firm's FRN.
            country: The country code.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm passport permissions with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_passport_permissions(frn, country, page=p),
            parse_data_fn=lambda data: [types.firm.FirmPassportPermission.model_validate(item) for item in data],
            result_count=result_count,
        )

    @paginated()
    async def get_firm_waivers(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmWaiver]:
        """Get firm waivers by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm waivers with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_waivers(frn, page=p),
            parse_data_fn=lambda data: [types.firm.FirmWaiver.model_validate(item) for item in data],
            result_count=result_count,
        )

    @paginated()
    async def get_firm_exclusions(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmExclusion]:
        """Get firm exclusions by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm exclusions with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_exclusions(frn, page=p),
            parse_data_fn=lambda data: [types.firm.FirmExclusion.model_validate(item) for item in data],
            result_count=result_count,
        )

    @paginated()
    async def get_firm_disciplinary_history(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmDisciplinaryRecord]:
        """Get disciplinary history records for a firm.

        Args:
            frn: The Firm Reference Number (FRN) of the firm.
            result_count: Minimum number of results to return.

        Returns:
            A page of disciplinary records with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_disciplinary_history(frn, page=p),
            parse_data_fn=lambda data: [types.firm.FirmDisciplinaryRecord.model_validate(item) for item in data],
            result_count=result_count,
        )

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

    @paginated()
    async def get_firm_appointed_representatives(
        self,
        frn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.firm.FirmAppointedRepresentative]:
        """Get firm appointed representatives by FRN.

        Args:
            frn: The firm's FRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of firm appointed representatives with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_firm_appointed_representatives(frn, page=p),
            parse_data_fn=self._parse_firm_appointed_representatives_pg,
            result_count=result_count,
        )

    # ------------------------------------------------------------------
    # Individual endpoints
    # ------------------------------------------------------------------

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
                            {"fca_api_lst_type": key} | fn_data
                        )
                    )
        return out

    @paginated()
    async def get_individual_controlled_functions(
        self,
        irn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.individual.IndividualControlledFunction]:
        """Get controlled functions for an individual.

        Args:
            irn: The Individual Reference Number (IRN).
            result_count: Minimum number of results to return.

        Returns:
            A page of controlled functions with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_individual_controlled_functions(irn, page=p),
            parse_data_fn=self._parse_individual_controlled_functions_pg,
            result_count=result_count,
        )

    @paginated()
    async def get_individual_disciplinary_history(
        self,
        irn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.individual.IndividualDisciplinaryRecord]:
        """Get disciplinary history records for an individual.

        Args:
            irn: The Individual Reference Number (IRN).
            result_count: Minimum number of results to return.

        Returns:
            A page of disciplinary records with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_individual_disciplinary_history(irn, page=p),
            parse_data_fn=lambda data: [
                types.individual.IndividualDisciplinaryRecord.model_validate(item) for item in data
            ],
            result_count=result_count,
        )

    # ------------------------------------------------------------------
    # Fund endpoints
    # ------------------------------------------------------------------

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

    @paginated()
    async def get_fund_names(
        self,
        prn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.products.ProductNameAlias]:
        """Get fund names by PRN.

        Args:
            prn: The fund's PRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of fund name aliases with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_fund_names(prn, page=p),
            parse_data_fn=lambda data: [types.products.ProductNameAlias.model_validate(item) for item in data],
            result_count=result_count,
        )

    @paginated()
    async def get_fund_subfunds(
        self,
        prn: str,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.products.SubFundDetails]:
        """Get fund sub-funds by PRN.

        Args:
            prn: The fund's PRN.
            result_count: Minimum number of results to return.

        Returns:
            A page of sub-fund details with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_fund_subfunds(prn, page=p),
            parse_data_fn=lambda data: [types.products.SubFundDetails.model_validate(item) for item in data],
            result_count=result_count,
        )

    # ------------------------------------------------------------------
    # Market endpoints
    # ------------------------------------------------------------------

    @paginated()
    async def get_regulated_markets(
        self,
        result_count: int = 1,
    ) -> types.pagination.MultipageList[types.markets.RegulatedMarket]:
        """Get regulated markets.

        Args:
            result_count: Minimum number of results to return.

        Returns:
            A page of regulated markets with pagination metadata.
        """
        return await self._fetch_paginated(
            fetch_page_fn=lambda p: self._client.get_regulated_markets(page=p),
            parse_data_fn=lambda data: [types.markets.RegulatedMarket.model_validate(item) for item in data],
            result_count=result_count,
        )
