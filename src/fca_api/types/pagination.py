"""Pagination types for FCA API responses.

Public:
    NextPageToken — opaque cursor passed to ``Client.fetch_next_page``.
    PageTokenSerializer — optional hook for signing/encrypting tokens.
    PaginationInfo — pagination metadata returned with each page.
    MultipageList — one page of typed results.

Internal:
    _PageState — JSON-encoded cursor (endpoint + arguments + page number).
    PaginatedResultInfo — parses the ``ResultInfo`` block from raw responses.
"""

import typing

import pydantic

from . import settings

T = typing.TypeVar("T")


# ---------------------------------------------------------------------------
# Internal: raw FCA API pagination metadata (used by async_api to parse responses)
# ---------------------------------------------------------------------------


class PaginatedResultInfo(pydantic.BaseModel):
    """Parsed ``ResultInfo`` block from a raw FCA API response.

    Attributes:
        next: URL of the next page (None on the last page).
        previous: URL of the previous page (None on the first page).
        page: Current 1-based page number.
        per_page: Items per page.
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


class _PageState(pydantic.BaseModel, frozen=True):
    """Internal cursor backing :data:`NextPageToken`.

    Encodes everything needed to resume a paginated request from a fresh
    process: the originating ``Client`` method name, its JSON-safe keyword
    arguments, and the 1-based page number to fetch next. A state with empty
    ``endpoint``/``params`` carries position only and cannot be dispatched via
    :meth:`Client.fetch_next_page`.
    """

    page: int = 1
    endpoint: str = ""
    params: typing.Dict[str, typing.Any] = pydantic.Field(default_factory=dict)

    def encode(self) -> str:
        return self.model_dump_json()

    @classmethod
    def decode(cls, token: str) -> "_PageState":
        return cls.model_validate_json(token)

    @classmethod
    def first(cls) -> "_PageState":
        return cls(page=1)


# ---------------------------------------------------------------------------
# Public: pagination token type
# ---------------------------------------------------------------------------

NextPageToken = typing.Annotated[
    str,
    pydantic.Field(
        description=(
            "Opaque pagination cursor. Pass unchanged to ``Client.fetch_next_page`` "
            "to retrieve the next page; do not construct, parse, or modify it."
        )
    ),
]
"""Opaque cursor for the next page. Format is internal and may change."""


# ---------------------------------------------------------------------------
# Public: token serializer protocol
# ---------------------------------------------------------------------------


@typing.runtime_checkable
class PageTokenSerializer(typing.Protocol):
    """Optional hook for signing or encrypting ``next_page`` tokens.

    Implement to protect tokens crossing a trust boundary (e.g. returned to an
    external caller and resubmitted later). When a serializer is configured on
    the ``Client``, outgoing tokens pass through :meth:`serialize` and incoming
    tokens through :meth:`deserialize`.

    Example::

        class HmacSerializer:
            def serialize(self, token: str) -> str: ...
            def deserialize(self, token: str) -> str: ...

        client = Client(credentials=("email", "key"), page_token_serializer=HmacSerializer())
    """

    def serialize(self, token: str) -> str:
        """Transform a raw token for external use (e.g. sign or encrypt)."""
        ...

    def deserialize(self, token: str) -> str:
        """Recover the raw token from its external form (e.g. verify or decrypt)."""
        ...


# ---------------------------------------------------------------------------
# Public: pagination metadata model
# ---------------------------------------------------------------------------


class PaginationInfo(pydantic.BaseModel):
    """Pagination state attached to every paginated result.

    Pass ``next_page`` to :meth:`Client.fetch_next_page` to advance::

        while page.pagination.has_next:
            page = await client.fetch_next_page(page.pagination.next_page)
    """

    model_config = pydantic.ConfigDict(frozen=True)

    has_next: bool = pydantic.Field(description="True if more results are available beyond this page.")
    next_page: typing.Optional[NextPageToken] = pydantic.Field(
        default=None,
        description="Cursor to pass to Client.fetch_next_page to fetch the next page. None when has_next is False.",
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
    """One page of typed results plus pagination state.

    Type Parameters:
        T: Type of items in ``data``.

    Walk the full result set::

        page = await client.search_frn("Barclays")
        while True:
            for firm in page.data:
                ...
            if not page.pagination.has_next:
                break
            page = await client.fetch_next_page(page.pagination.next_page)

    Collect at least N items in one call (may issue several requests)::

        page = await client.search_frn("Barclays", result_count=100)
    """

    model_config = pydantic.ConfigDict(frozen=True)

    data: typing.Tuple[T, ...] = pydantic.Field(description="The result items for this page. Immutable.")
    pagination: PaginationInfo = pydantic.Field(
        description="Pagination state, including whether more results exist and how to fetch them."
    )
