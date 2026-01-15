"""High-level Financial Services Register API client.

Performs data validation and transformation on top of the raw API client.
"""

import logging
import re
import typing

import httpx

from . import raw, types

logger = logging.getLogger(__name__)

T = typing.TypeVar("T")
BaseSubclassT = typing.TypeVar("BaseSubclassT", bound=types.base.Base)


class PaginatedResponseHandler(typing.Generic[T]):
    _fetch_page: typing.Callable[[int], typing.Awaitable[raw.FcaApiResponse]]
    _parse_data_fn: typing.Callable[[list[dict]], list[T]]

    def __init__(
        self,
        fetch_page: typing.Callable[[int], typing.Awaitable[raw.FcaApiResponse]],
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
        if res.result_info:
            result_info = types.pagination.PaginatedResultInfo.model_validate(res.result_info)
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
        await out._async_init()
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
        await out._async_init()
        return out

    async def search_prn(self, fund_name: str) -> types.pagination.MultipageList[types.search.FirmSearchResult]:
        """Search for a firm by its name."""
        out = types.pagination.MultipageList(
            fetch_page=lambda page_idx: self._paginated_search(
                lambda page_idx: self._client.search_prn(fund_name, page_idx), page_idx, types.search.FundSearchResult
            ),
        )
        await out._async_init()
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

    async def get_individual_controlled_functions(
        self, irn: str
    ) -> list[types.individual.IndividualControlledFunction]:
        """Get individual details by IRN.

        Args:
            irn: The individual's IRN.

        Returns:
            The individual's details.
        """
        res = await self._client.get_individual_controlled_functions(irn)
        data = res.data
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

    async def get_individual_disciplinary_history(
        self, irn: str
    ) -> types.pagination.MultipageList[types.individual.IndividualDisciplinaryRecord]:
        out = types.pagination.MultipageList(
            fetch_page=PaginatedResponseHandler(
                lambda page_idx: self._client.get_individual_disciplinary_history(irn, page=page_idx),
                lambda data: [types.individual.IndividualDisciplinaryRecord.model_validate(item) for item in data],
            ).fetch_page,
        )
        await out._async_init()
        return out