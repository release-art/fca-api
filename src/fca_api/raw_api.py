"""
This module implements the low-level Financial Services Register API
client.

It provides direct access to the FS Register API endpoints with minimal
abstraction/data validation.
"""

import contextlib
import typing
import warnings
from typing import Literal, Union
from urllib.parse import urlencode

import httpx

from . import const, exc, raw_status_codes


@contextlib.asynccontextmanager
async def _noop_limiter() -> typing.AsyncGenerator[None, None]:
    yield None


LimiterContextT = typing.Callable[[], typing.AsyncContextManager[None]]
T = typing.TypeVar("T")
UNSET = object()


class FcaApiResponse(httpx.Response, typing.Generic[T]):
    """A simple :py:class:`httpx.Response`-based wrapper for the API responses."""

    _fca_data_override: T = UNSET

    def __init__(self, response: httpx.Response) -> None:
        """Initialiser requiring a :py:class:`httpx.Response` object.

        Parameters
        ----------
        response : httpx.Response
            The response from the original request.
        """
        self.__dict__.update(**response.__dict__)

    @property
    def fca_api_status(self) -> str:
        """:py:class:`str`: The status message of the API response.

        Returns
        -------
        str
            The status message of the API response.
        """
        return self.json().get("Status")

    @property
    def result_info(self) -> dict:
        """:py:class:`dict`: The pagination information in the API response.

        Returns
        -------
        dict
            The pagination information in the API response.
        """
        return self.json().get("ResultInfo")

    @property
    def message(self) -> str:
        """:py:class:`str`: The status message in the API response.

        Returns
        -------
        str
            The status message in the API response.
        """
        return self.json().get("Message")

    @property
    def data(self) -> T:
        """:py:class:`dict` or :py:class:`list`: The data in the API response.

        Returns
        -------
        T
            The data in the API response - will usually be either a
            :py:class:`dict` or a :py:class:`list` of dicts.
        """
        if self._fca_data_override is not UNSET:
            return self._fca_data_override
        return self.json().get("Data")

    def override_data(self, new_data: T) -> None:
        """Override the data property with new data.

        Parameters
        ----------
        new_data : T
            The new data to set.
        """
        self._fca_data_override = new_data


class RawClient:
    """Low-level client for the Financial Services Register API (V0.1).

    This client provides direct access to the FS Register API endpoints
    with minimal abstraction/data validation.

    Consult the API documentation for further details.

    https://register.fca.org.uk/Developer/s/
    """

    #: All instances must have this private attribute to store API session state
    _api_session: httpx.AsyncClient
    _api_limiter: LimiterContextT

    def __init__(
        self,
        credentials: Union[
            typing.Tuple[str, str],
            httpx.AsyncClient,
        ],
        api_limiter: typing.Optional[LimiterContextT] = None,
    ) -> None:
        """Initialiser accepting either API credentials or a pre-configured
        session.

        Parameters
        ----------
            credentials:
                Connection credentials.
                Supports two forms:
                1. A tuple of (api_username: str, api_key: str)
                2. An instance of httpx.Client (with correct headers set)
            api_limiter: Function returning async context, optional
                An optional asynchronous callable to be used as a rate limiter
                for API calls. If not provided, no rate limiting is applied.

                Suggested package:
                    https://pypi.org/project/asyncio-throttle/
        """
        if isinstance(credentials, httpx.AsyncClient):
            self._api_session = credentials
        elif isinstance(credentials, tuple | list) and len(credentials) == 2:
            api_username, api_key = credentials
            self._api_session = httpx.AsyncClient(
                headers={
                    "ACCEPT": "application/json",
                    "X-AUTH-EMAIL": api_username,
                    "X-AUTH-KEY": api_key,
                }
            )
        else:
            raise ValueError(
                "credentials must be either a tuple of (api_username: str, api_key: str) "
                "or an instance of httpx.AsyncClient."
                f"Got {type(credentials)} instead."
            )
        if api_limiter is None:
            self._api_limiter = _noop_limiter
        else:
            self._api_limiter = api_limiter

    @property
    def api_session(self) -> httpx.AsyncClient:
        """:py:class:`httpx.AsyncClient`: The API session instance.

        Returns
        -------
        httpx.AsyncClient
        """
        return self._api_session

    @property
    def api_version(self) -> str:
        """:py:class:`str`: The API version being used by the client.

        Returns
        -------
        str
            The API version being used by the client.
        """
        return const.ApiConstants.API_VERSION.value

    async def common_search(
        self,
        resource_name: str,
        resource_type: Literal["firm", "individual", "fund"],
        page: int | None = None,
    ) -> FcaApiResponse[list[dict[str, typing.Any]]]:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing the results of a search using the FS
        Register API common search API endpoint.

        Directly calls the API common search endpoint:
        ::

            /V0.1/Search?q=resource_name>&type=resource_type

        to perform a case-insensitive search in the FS Register on the given
        resource name (or name substring) and resource type (``"firm"``,
        ``"individual"``, ``"fund"``).

        Returns an
        :py:class:`~fca_api.raw_api.FcaApiResponse`
        object if the API call completes without exceptions or errors.

        Parameters
        ----------
        resource_name : str
            The name (or name substring) of a resource to search for in the
            FS Register, e.g. ``"ABC Company"``, ``"John Smith"``,
            ``"International Super Fund"``.

        resource_type : str
            The resource type to search for - according to the API this must
            be one of the following strings: ``"firm"``, ``"individual"``, or
            ``"fund"``.

        Returns
        -------
        FcaApiResponse[list[dict[str, typing.Any]]]
            Wrapper of the API response object - there may be no data in
            the response if no matching resources are found.

        Raises
        ------
        FcaRequestError
            If there was a :py:class:`httpx.RequestError` in making the original
            request.
        """
        assert page is None or page > 0, f"Invalid page number: {page}"
        if not resource_name:
            raise ValueError("Resource name must be a non-empty string.")
        if not resource_type:
            raise ValueError("Resource type must be a non-empty string.")
        search_req = {"q": resource_name, "type": resource_type}
        if page is not None:
            assert isinstance(page, int) and page >= 1, page
            search_req["pgnp"] = page
        search_str = urlencode(search_req)
        url = f"{const.ApiConstants.BASEURL.value}/Search?{search_str}"
        try:
            async with self._api_limiter():
                response = await self.api_session.get(url)
        except httpx.RequestError as e:
            raise exc.FcaRequestError(e) from None
        out = FcaApiResponse(response)
        if not out.is_success:
            raise exc.FcaRequestError(
                f"API search request failed with status code {out.status_code}: "
                f"{out.reason_phrase}. Please check the search parameters and try again."
            )

        fca_status_code = out.fca_api_status
        fca_code_info = raw_status_codes.find_code(fca_status_code)
        if fca_code_info is None:
            warnings.warn(
                f"Received unknown FCA API status code: {fca_status_code}. "
                "Please ensure that your client is up to date.",
                stacklevel=2,
            )
        elif fca_code_info.is_error:
            raise exc.FcaRequestError(
                f"API search request failed with FCA API status code {fca_status_code}: {out.message}"
            )

        if not out.data:
            # No results found - ensure that an empty list is returned (the API returns None sometimes)
            out.override_data([])
        elif not isinstance(out.data, list):
            raise exc.FcaRequestError(
                "API search response data is not a list as expected. Please check the search parameters and try again."
            )

        return out

    async def search_frn(self, firm_name: str, page: int | None = None) -> FcaApiResponse[list[dict[str, str]]]:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`: Returns a response containing
        firm records matching the given firm name.

        Calls the common_search method to perform the search.

        Returns a FcaApiResponse containing the api response with matching
        firm records.

        Parameters
        ----------
        firm_name : str
            The firm name (case insensitive).

            Returns an API response with all matching form records.

        Returns
        -------
        FcaApiResponse[list[dict[str, str]]]
            A response containing a list of matching firm records.
        """
        return await self.common_search(firm_name, const.ResourceTypes.FIRM.value.type_name, page=page)

    async def _get_resource_info(
        self,
        resource_ref_number: str,
        resource_type: str,
        modifiers: tuple[str] = None,
        page: int | None = None,
    ) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        A private, base handler for resource information API handlers.

        Is the base handler for the following resource informational API
        endpoints (in alphabetical order):
        ::

            /V0.1/CIS/{PRN}
            /V0.1/CIS/{PRN}/Names
            /V0.1/CIS/{PRN}/Subfund
            /V0.1/Firm/{FRN}
            /V0.1/Firm/{FRN}/Address
            /V0.1/Firm/{FRN}/AR
            /V0.1/Firm/{FRN}/CF
            /V0.1/Firm/{FRN}/DisciplinaryHistory
            /V0.1/Firm/{FRN}/Exclusions
            /V0.1/Firm/{FRN}/Individuals
            /V0.1/Firm/{FRN}/Names
            /V0.1/Firm/{FRN}/Passports
            /V0.1/Firm/{FRN}/Passports/{Country}/Permission
            /V0.1/Firm/{FRN}/Permissions
            /V0.1/Firm/{FRN}/Regulators
            /V0.1/Firm/{FRN}/Requirements
            /V0.1/Firm/{FRN}/Requirements/{ReqRef}/InvestmentTypes
            /V0.1/Firm/{FRN}/Waiver
            /V0.1/Individuals/{IRN}
            /V0.1/Individuals/{IRN}/CF
            /V0.1/Individuals/{IRN}/DisciplinaryHistory

        where ``{FRN}``, ``{IRN}``, and ``{PRN}`` denote unique firm reference
        numbers (FRN), individual reference numbers (IRN), and product
        reference numbers (PRN).

        The ``resource_ref_number`` must be a valid unique resource identifier
        and ``resource_type`` should be a valid resource type, as given by one
        of the strings ``'firm'``, ``'individual'``, or ``'fund'``.

        .. note::

           This is a private method and is **not** intended for direct use by
           end users.

        Returns an
        :py:class:`~fca_api.raw_api.FcaApiResponse`.

        The optional modifiers, given as a tuple of strings, should represent a
        valid ordered combination of actions and/or properties related to the
        given resource as identified by the resource ref. number.

        The modifier strings should **NOT** contain any leading or trailing
        forward slashes (``"/"``) as this can lead to badly formed URLs
        and to responses with no data - in any case, any leading or trailing
        forward slashes are stripped before the request.

        Parameters
        ----------
        resource_ref_number : str
            The resource reference number.

        resource_type : str
            The resource type - should be one of the strings ``'firm'``,
            ``'individual'``, or ``'fund'``.

        modifiers : tuple, default=None
            Optional tuple of strings indicating a valid ordered combination of
            resource and/or action modifiers for the resource in question.
            Should **NOT** have leading or trailing forward slashes (``"/"``).

        Raises
        ------
        FcaRequestError
            If there was a request exception.

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the resource ref. number isn't found.
        """
        if resource_type not in const.ResourceTypes.all_types():
            raise ValueError('Resource type must be one of the strings ``"firm"``, ``"fund"``, or ``"individual"``')

        query_params = {}
        assert page is None or page > 0, f"Invalid page number: {page}"
        if page is not None:
            assert isinstance(page, int) and page >= 1, page
            query_params["pgnp"] = page

        resource_type_info = const.ResourceTypes.from_type_name(resource_type)
        resource_endpoint_base = resource_type_info.endpoint_base

        url = f"{const.ApiConstants.BASEURL.value}/{resource_endpoint_base}/{resource_ref_number}"

        if modifiers:
            url += f"/{'/'.join(modifiers)}"

        if query_params:
            search_str = urlencode(query_params)
            url += f"?{search_str}"

        try:
            async with self._api_limiter():
                response = await self.api_session.get(url)
        except httpx.RequestError as e:
            raise exc.FcaRequestError(e) from None

        out = FcaApiResponse(response)
        if not out.is_success:
            raise exc.FcaRequestError(
                f"API search request failed with status code {out.status_code}: "
                f"{out.reason_phrase}. Please check the search parameters and try again."
            )

        fca_status_code = out.fca_api_status
        fca_code_info = raw_status_codes.find_code(fca_status_code)
        if fca_code_info is None:
            warnings.warn(
                f"Received unknown FCA API status code: {fca_status_code}. "
                "Please ensure that your client is up to date.",
                stacklevel=2,
            )
        elif fca_code_info.is_error:
            raise exc.FcaRequestError(
                f"API search request failed with FCA API status code {fca_status_code}: {out.message}"
            )
        return out

    async def get_firm(self, frn: str) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing firm details, given its firm reference
        number (FRN)

        Handler for the top-level firm details API endpoint:
        ::

            /V0.1/Firm/{FRN}

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(frn, const.ResourceTypes.FIRM.value.type_name)

    async def get_firm_names(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing the alternative or secondary trading name
        details of a firm, given its firm reference number (FRN).

        Handler for the firm names API endpoint:
        ::

            /V0.1/Firm/{FRN}/Names

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Names",),
            page=page,
        )

    async def get_firm_addresses(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing the address details of a firm, given its
        firm reference number (FRN).

        Handler for the firm address details API endpoint:
        ::

            /V0.1/Firm/{FRN}/Address

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Address",),
            page=page,
        )

    async def get_firm_controlled_functions(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing the controlled functions associated with a
        firm, given its firm reference number (FRN).

        Handler for the firm controlled functions API endpoint:
        ::

            /V0.1/Firm/{FRN}/CF

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("CF",),
            page=page,
        )

    async def get_firm_individuals(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing the individuals associated with a firm,
        given its firm reference number (FRN).

        Handler for the firm individuals API endpoint:
        ::

            /V0.1/Firm/{FRN}/Individuals

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Individuals",),
            page=page,
        )

    async def get_firm_permissions(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing the permissions associated with a firm,
        given its firm reference number (FRN).

        Handler for the firm permissions API endpoint:
        ::

            /V0.1/Firm/{FRN}/Permissions

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Permissions",),
            page=page,
        )

    async def get_firm_requirements(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing the requirements associated with a firm,
        given its firm reference number (FRN).

        Handler for the firm requirements API endpoint:
        ::

            /V0.1/Firm/{FRN}/Requirements

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Requirements",),
            page=page,
        )

    async def get_firm_requirement_investment_types(
        self, frn: str, req_ref: str, page: int | None = None
    ) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing any investment types listed for a specific
        requirement associated with a firm, given its firm reference number
        (FRN).

        Handler for the firm requirement investment types API endpoint:
        ::

            /V0.1/Firm/{FRN}/Requirements/<ReqRef>/InvestmentTypes

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        req_ref : str
            The requirement reference number as a string.

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Requirements", req_ref, "InvestmentTypes"),
            page=page,
        )

    async def get_firm_regulators(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing the regulators associated with a firm,
        given its firm reference number (FRN).

        Handler for the firm regulators API endpoint:
        ::

            /V0.1/Firm/{FRN}/Regulators

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Regulators",),
            page=page,
        )

    async def get_firm_passports(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing the passports associated with a firm,
        given its firm reference number (FRN).

        Handler for the firm passports API endpoint:
        ::

            /V0.1/Firm/{FRN}/Passports

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Passports",),
            page=page,
        )

    async def get_firm_passport_permissions(self, frn: str, country: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing country-specific passport permissions for
        a firm and a country, given its firm reference number (FRN) and country
        name.

        Handler for the firm passport permissions API endpoint:
        ::

            /V0.1/Firm/{FRN}/Requirements/{Country}/Permission

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        country : str
            The country name.

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Passports", country, "Permission"),
            page=page,
        )

    async def get_firm_waivers(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing any waivers applying to a firm, given its
        firm reference number (FRN).

        Handler for the firm waivers API endpoint:
        ::

            /V0.1/Firm/{FRN}/Waivers

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Waivers",),
            page=page,
        )

    async def get_firm_exclusions(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing any exclusions applying to a firm, given
        its firm reference number (FRN).

        Handler for the firm exclusions API endpoint:
        ::

            /V0.1/Firm/{FRN}/Exclusions

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("Exclusions",),
            page=page,
        )

    async def get_firm_disciplinary_history(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing the disciplinary history of a firm, given
        its firm reference number (FRN).

        Handler for the firm disciplinary history API endpoint:
        ::

            /V0.1/Firm/{FRN}/DisciplinaryHistory

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("DisciplinaryHistory",),
            page=page,
        )

    async def get_firm_appointed_representatives(self, frn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`:
        Returns a response containing information on the appointed
        representatives of a firm, given its firm reference number (FRN).

        Handler for the firm appointed representatives API endpoint:
        ::

            /V0.1/Firm/{FRN}/AR

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the FRN is found, otherwise with no data.

        Parameters
        ----------
        frn : str
            The firm reference number (FRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the FRN isn't found.
        """
        return await self._get_resource_info(
            frn,
            const.ResourceTypes.FIRM.value.type_name,
            modifiers=("AR",),
            page=page,
        )

    async def search_irn(self, individual_name: str, page: int | None = None) -> FcaApiResponse[list[dict[str, str]]]:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`: Returns a response containing
        individual records matching the given individual name.

        Returns a FcaApiResponse containing the api response with matching
        individual records.

        Parameters
        ----------
        individual_name : str
            The individual name (case insensitive). The name needs to be precise
            enough to guarantee a unique return value, otherwise a JSON array
            of all matching records are returned.

        Returns
        -------
        FcaApiResponse[list[dict[str, str]]]
            A response containing a list of matching individual records.
        """
        return await self.common_search(
            individual_name,
            const.ResourceTypes.INDIVIDUAL.value.type_name,
            page=page,
        )

    async def get_individual(self, irn: str) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse` :
        Returns a response containing individual details, given their individual
        reference number (IRN)

        Handler for top-level individual details API endpoint:
        ::

            /V0.1/Individuals/{IRN}

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the IRN is found, otherwise with no data.

        Parameters
        ----------
        irn : str
            The individual reference number (IRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the IRN isn't found.
        """
        return await self._get_resource_info(irn, const.ResourceTypes.INDIVIDUAL.value.type_name)

    async def get_individual_controlled_functions(self, irn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse` :
        Returns a response containing the controlled functions associated with
        an individual, given their individual reference number (FRN).

        Handler for the individual controlled functions API endpoint:
        ::

            /V0.1/Firm/{IRN}/CF

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the IRN is found, otherwise with no data.

        Parameters
        ----------
        irn : str
            The individual reference number (IRN).

        Returns
        -------
        FcaApiResponse
            Wrapepr of the API response object - there may be no data in
            the response if the IRN isn't found.
        """
        return await self._get_resource_info(
            irn,
            const.ResourceTypes.INDIVIDUAL.value.type_name,
            modifiers=("CF",),
            page=page,
        )

    async def get_individual_disciplinary_history(self, irn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse` :
        Returns a response containing the disciplinary history of an
        individual, given their individual reference number (FRN).

        Handler for the individual disciplinary history API endpoint:
        ::

            /V0.1/Firm/{IRN}/DisciplinaryHistory

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the IRN is found, otherwise with no data.

        Parameters
        ----------
        irn : str
            The individual reference number (IRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the IRN isn't found.
        """
        return await self._get_resource_info(
            irn,
            const.ResourceTypes.INDIVIDUAL.value.type_name,
            modifiers=("DisciplinaryHistory",),
            page=page,
        )

    async def search_prn(self, fund_name: str, page: int | None = None) -> FcaApiResponse[list[dict[str, str]]]:
        """:py:class:`~fca_api.raw_api.FcaApiResponse`: Returns a response containing
        fund records matching the given fund name.

        Returns a FcaApiResponse containing the api response with matching
        fund records.

        Parameters
        ----------
        fund_name : str
            The fund name (case insensitive). The name needs to be precise
            enough to guarantee a unique return value, otherwise a JSON array
            of all matching records are returned.

        Returns
        -------
        FcaApiResponse[list[dict[str, str]]]
            A response containing a list of matching fund records.
        """
        return await self.common_search(fund_name, const.ResourceTypes.FUND.value.type_name, page=page)

    async def get_fund(self, prn: str) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse` :
        Returns a response containing fund (or collective investment scheme
        (CIS)) details, given its product reference number (PRN)

        Handler for top-level fund details API endpoint:
        ::

            /V0.1/CIS/{PRN}

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the PRN is found, otherwise with no data.

        Parameters
        ----------
        prn : str
            The product reference number (PRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the PRN isn't found.
        """
        return await self._get_resource_info(prn, const.ResourceTypes.FUND.value.type_name)

    async def get_fund_names(self, prn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse` :
        Returns a response containing the alternative or secondary trading name
        details of a fund (or collective investment scheme (CIS)), given its
        product reference number (PRN).

        Handler for top-level fund names API endpoint:
        ::

            /V0.1/CIS/{PRN}/Names

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the PRN is found, otherwise with no data.

        Parameters
        ----------
        prn : str
            The product reference number (PRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the PRN isn't found.
        """
        return await self._get_resource_info(
            prn,
            const.ResourceTypes.FUND.value.type_name,
            modifiers=("Names",),
            page=page,
        )

    async def get_fund_subfunds(self, prn: str, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse` :
        Returns a response containing the subfund details of a fund (or
        collective investment scheme (CIS)), given its product reference number
        (PRN).

        Handler for top-level subfund details API endpoint:
        ::

            /V0.1/CIS/{PRN}/Subfund

        Returns a
        :py:class:`~fca_api.raw_api.FcaApiResponse`,
        with data if the PRN is found, otherwise with no data.

        Parameters
        ----------
        prn : str
            The product reference number (PRN).

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the PRN isn't found.
        """
        return await self._get_resource_info(
            prn,
            const.ResourceTypes.FUND.value.type_name,
            modifiers=("Subfund",),
            page=page,
        )

    async def get_regulated_markets(self, page: int | None = None) -> FcaApiResponse:
        """:py:class:`~fca_api.raw_api.FcaApiResponse` :
        Returns a response containing details of all current regulated markets,
        as defined in UK and EU / EEA financial services legislation.

        For further information consult the API documentation:

        https://register.fca.org.uk/Developer/s/

        or the FCA glossary:

        https://www.handbook.fca.org.uk/handbook/glossary/G978.html?date=2007-01-20

        Returns
        -------
        FcaApiResponse
            Wrapper of the API response object - there may be no data in
            the response if the common search query produces no results.
        """
        if page not in (None, 1):
            raise NotImplementedError("Pagination is not supported for regulated markets at this time.")
        url = f"{const.ApiConstants.BASEURL.value}/CommonSearch?{urlencode({'q': 'RM'})}"

        async with self._api_limiter():
            response = await self.api_session.get(url)
        return FcaApiResponse(response)
