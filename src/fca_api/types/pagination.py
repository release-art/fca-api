"""Pagination types for FCA API responses.

Types:
    NextPageToken: An opaque string cursor passed between calls to page through results.
    PageTokenSerializer: Protocol for encrypting/decrypting pagination tokens.
    PaginationInfo: Pagination metadata returned alongside each page of results.
    MultipageList: A generic value object containing one page of results.

Internal types (not part of the public API):
    _PageState: Encodes endpoint identity, bound kwargs, and next page number into/from a NextPageToken.
    PaginatedResultInfo: Parses raw FCA API response pagination metadata.
"""

import dataclasses
import json
import typing

import pydantic

from . import settings

T = typing.TypeVar("T")


# ---------------------------------------------------------------------------
# Internal: raw FCA API pagination metadata (used by async_api to parse responses)
# ---------------------------------------------------------------------------


class PaginatedResultInfo(pydantic.BaseModel):
    """Pagination metadata from FCA API responses.

    Represents the ``ResultInfo`` section of raw FCA API responses. Used
    internally by the async client to determine whether further pages exist.

    Attributes:
        next: URL for the next page (None on the last page).
        previous: URL for the previous page (None on the first page).
        page: Current 1-based page number.
        per_page: Number of items per page.
        total_count: Total items across all pages (may be approximate).
    """

    next: typing.Optional[pydantic.HttpUrl] = None
    previous: typing.Optional[pydantic.HttpUrl] = None
    page: int
    per_page: int
    total_count: int

    @property
    def total_pages(self) -> int:
        """Total pages required to hold all items."""
        return (self.total_count + self.per_page - 1) // self.per_page

    @classmethod
    def model_validate(cls, data: dict) -> "PaginatedResultInfo":
        return super().model_validate(
            {key.lower().strip(): value for (key, value) in data.items()},
            extra=settings.model_validate_extra,
        )


# ---------------------------------------------------------------------------
# Internal: page state codec
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class _PageState:
    """Encodes everything needed to resume a paginated call as a portable JSON string.

    Not part of the public API — callers only ever see ``NextPageToken`` (str).

    The state carries:

    * ``endpoint``: name of the ``Client`` method that produced this token, so
      ``Client.next_page`` can dispatch back to the right endpoint.
    * ``args``: keyword arguments to re-apply on the next call (everything the
      original method received except ``next_page``).
    * ``page``: the 1-based FCA API page number to fetch next.
    """

    endpoint: str
    args: typing.Dict[str, typing.Any]
    page: int

    def encode(self) -> str:
        return json.dumps({"endpoint": self.endpoint, "args": self.args, "page": self.page})

    @classmethod
    def decode(cls, token: str) -> "_PageState":
        data = json.loads(token)
        return cls(endpoint=str(data["endpoint"]), args=dict(data["args"]), page=int(data["page"]))


# ---------------------------------------------------------------------------
# Public: pagination token type
# ---------------------------------------------------------------------------

NextPageToken = typing.Annotated[
    str,
    pydantic.Field(
        description=(
            "Opaque pagination cursor. Pass this value unchanged to the same endpoint "
            "to retrieve the next page of results. Treat it as an opaque string — "
            "do not construct, parse, or modify it."
        )
    ),
]
"""An opaque string cursor for retrieving the next page of results.

Returned in ``PaginationInfo.next_page`` when more results exist. Pass it
back to the same endpoint method (as the ``next_page`` argument) to fetch
the next batch, or pass the whole page to ``Client.next_page`` to do the
same without naming the endpoint again.

The internal format is an implementation detail and may change. Always treat
this value as opaque.
"""


# ---------------------------------------------------------------------------
# Public: token serializer protocol
# ---------------------------------------------------------------------------


@typing.runtime_checkable
class PageTokenSerializer(typing.Protocol):
    """Protocol for encrypting and decrypting pagination tokens.

    Implement this interface to protect ``next_page`` tokens from tampering
    or inspection when they leave the service boundary (e.g. returned to API
    callers and submitted back on a subsequent request).

    Pass an instance to ``async_api.Client`` at construction time::

        class HmacSerializer:
            def serialize(self, token: str) -> str:
                # sign / encrypt the raw token
                ...

            def deserialize(self, token: str) -> str:
                # verify / decrypt back to the raw token
                ...

        client = Client(
            credentials=("email", "key"),
            page_token_serializer=HmacSerializer(),
        )

    When a serializer is configured:

    * Tokens returned by endpoint methods are passed through ``serialize``
      before being placed in ``PaginationInfo.next_page``.
    * Tokens received by endpoint methods are passed through ``deserialize``
      before being decoded internally.
    """

    def serialize(self, token: str) -> str:
        """Transform a raw pagination token for external use (e.g. encrypt or sign)."""
        ...

    def deserialize(self, token: str) -> str:
        """Recover the raw pagination token from an external value (e.g. decrypt or verify)."""
        ...


# ---------------------------------------------------------------------------
# Public: pagination metadata model
# ---------------------------------------------------------------------------


class PaginationInfo(pydantic.BaseModel):
    """Pagination state for a result set returned by the FCA API.

    Returned alongside every page of results from the async client. Use
    ``next_page`` in a subsequent call to the same endpoint to retrieve
    the next batch of items, or pass the whole page to ``Client.next_page``.

    Example::

        page = await client.search_frn("Barclays", result_count=25)

        while page.pagination.has_next:
            page = await client.next_page(page)
    """

    model_config = pydantic.ConfigDict(frozen=True)

    has_next: bool = pydantic.Field(description="True if more results are available beyond this page.")
    next_page: typing.Optional[NextPageToken] = pydantic.Field(
        default=None,
        description=("Cursor to pass to the same endpoint to fetch the next page. None when has_next is False."),
    )
    size: typing.Optional[int] = pydantic.Field(
        default=None,
        description=(
            "Estimated total number of items in the collection as reported by the FCA API. May be approximate."
        ),
    )


# ---------------------------------------------------------------------------
# Public: result page model
# ---------------------------------------------------------------------------


class MultipageList(pydantic.BaseModel, typing.Generic[T]):
    """A page of typed results from a paginated FCA API endpoint.

    Contains the fetched data items and the pagination metadata needed to
    retrieve subsequent pages. Returned by all paginated methods on
    ``async_api.Client``.

    Type Parameters:
        T: The type of items in ``data``.

    Fetching pages::

        # First page — default result_count fetches one API page
        page = await client.search_frn("Barclays")
        print(f"Got {len(page.data)} of ~{page.pagination.size} total results")

        # Subsequent pages — either call the endpoint again with the cursor...
        while page.pagination.has_next:
            page = await client.search_frn(
                "Barclays",
                next_page=page.pagination.next_page,
                result_count=25,
            )

        # ...or let the client re-dispatch via the token:
        while page.pagination.has_next:
            page = await client.next_page(page)

    Fetching a larger batch in one call::

        # Request at least 100 items (may trigger multiple underlying API calls)
        page = await client.search_frn("Barclays", result_count=100)
        # page.data has >= 100 items (or all available items if fewer exist)
    """

    model_config = pydantic.ConfigDict(frozen=True)

    data: typing.List[T] = pydantic.Field(description="The result items for this page.")
    pagination: PaginationInfo = pydantic.Field(
        description=("Pagination state, including whether more results exist and how to fetch them.")
    )
