"""Pagination types for FCA API responses.

Public types:
    NextPageToken: Opaque string cursor passed to ``Client.fetch_next_page``.
    PageTokenSerializer: Protocol for encrypting/decrypting pagination tokens.
    PaginationInfo: Pagination metadata returned alongside each page of results.
    MultipageList: Generic value object holding one batch of results plus a get_next handle.

Internal types (not part of the public API):
    _PageState: Self-contained, restartable pagination cursor encoded as JSON.
    PaginatedResultInfo: Parses raw FCA API response pagination metadata.
"""

import typing

import pydantic

from .. import exc
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


class _PageState(pydantic.BaseModel, frozen=True):
    """A self-contained, restartable pagination cursor encoded as JSON.

    Not part of the public API — callers only ever see ``NextPageToken`` (str).

    The state captures everything needed to resume a paginated request from a
    fresh process with no in-memory context:

    * ``endpoint`` — the name of the ``Client`` method that produced the page
      (used to re-dispatch on resume; validated against an allowlist).
    * ``params`` — the originating call's keyword arguments (query, filters,
      ``result_count``, path parameters, …), as JSON-safe values.
    * ``page`` — the 1-based FCA API page number to fetch next.

    A position-only state (``endpoint``/``params`` empty) is still valid: the
    originating endpoint resumes from the position, but cannot be replayed
    blindly via :meth:`Client.fetch_next_page`.
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
            "Opaque pagination cursor. Pass this value unchanged to "
            "``Client.fetch_next_page`` to retrieve the next page of results. Treat "
            "it as an opaque string — do not construct, parse, or modify it."
        )
    ),
]
"""An opaque string cursor for retrieving the next page of results.

Returned in ``PaginationInfo.next_page`` when more results exist. Pass it to
``Client.fetch_next_page`` to fetch the next batch (or call
``MultipageList.get_next``, which does this for you).

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
    ``MultipageList.get_next`` (or pass ``next_page`` to
    ``Client.fetch_next_page``) to retrieve the next page of items.

    Example::

        page = await client.search_frn("Barclays")

        while page.pagination.has_next:
            page = await page.get_next()
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
# Internal: client handle used by MultipageList.get_next
# ---------------------------------------------------------------------------


@typing.runtime_checkable
class _NextPageFetcher(typing.Protocol):
    """Minimal interface :meth:`MultipageList.get_next` needs from a client.

    ``Client`` satisfies this structurally; kept here to avoid importing the
    client into the types package.
    """

    async def fetch_next_page(self, next_page: str) -> typing.Any: ...


# ---------------------------------------------------------------------------
# Public: result page model
# ---------------------------------------------------------------------------


class MultipageList(pydantic.BaseModel, typing.Generic[T]):
    """A page of typed results from a paginated FCA API endpoint.

    Contains the items collected by one client call — at least ``result_count``
    items, or all remaining items if fewer exist — plus the pagination metadata
    needed to retrieve the next batch. Returned by all paginated methods on
    ``async_api.Client``. ``MultipageList`` itself is a plain value object: it
    holds the already-fetched ``data`` and a single :meth:`get_next` handle,
    and does not fetch lazily or merge across calls. Advance with
    :meth:`get_next` (or by passing ``pagination.next_page`` to
    :meth:`Client.fetch_next_page`).

    Type Parameters:
        T: The type of items in ``data``.

    Walking the whole result set with ``get_next``::

        page = await client.search_frn("Barclays")
        while True:
            for firm in page.data:
                ...  # process this batch's items
            if not page.pagination.has_next:
                break
            page = await page.get_next()

    Fetching a larger batch in one call::

        # Collect at least 100 items (may issue several underlying requests)
        page = await client.search_frn("Barclays", result_count=100)
        # page.data has >= 100 items (or all available if fewer exist)

    Resuming statelessly from a self-contained token (e.g. a fresh request in an
    async server or agent tool — only the token is needed, not the query)::

        page = await client.search_frn("Barclays")
        token = page.pagination.next_page  # opaque, restartable cursor

        # ... later, in a new process with only `token` ...
        page2 = await client.fetch_next_page(token)
    """

    model_config = pydantic.ConfigDict(frozen=True, arbitrary_types_allowed=True)

    data: typing.List[T] = pydantic.Field(description="The result items for this page.")
    pagination: PaginationInfo = pydantic.Field(
        description="Pagination state, including whether more results exist and how to fetch them."
    )

    _client: typing.Optional[_NextPageFetcher] = pydantic.PrivateAttr(default=None)
    """Client used to fetch the next batch via the self-contained ``next_page``
    token. Set by the client when the list is produced; ``None`` on
    manually-constructed or deserialized instances. Bind one with
    :meth:`with_client` to re-enable :meth:`get_next` on a reconstructed list.
    """

    def with_client(self, client: _NextPageFetcher) -> "MultipageList[T]":
        """Bind a client so :meth:`get_next` works on this (e.g. deserialized) list.

        Returns ``self`` for chaining. The token itself is self-contained, so
        the bound client only supplies the HTTP session — any ``Client`` will do.
        """
        self._client = client
        return self

    async def get_next(self) -> "MultipageList[T]":
        """Fetch the next batch from the same endpoint with the same arguments.

        Convenience wrapper over :meth:`Client.fetch_next_page` using this
        list's self-contained ``pagination.next_page`` token. The returned
        ``MultipageList`` is itself bound for further iteration.

        Raises:
            NoMorePagesError: If ``pagination.has_next`` is ``False`` — this
                list is already the last batch.
            RuntimeError: If no client is bound (e.g. a manually-constructed or
                deserialized list). Either call ``client.fetch_next_page(token)``
                directly, or bind one first via :meth:`with_client`.

        Example:
            Walk every batch::

                page = await client.search_frn("Barclays")
                while page.pagination.has_next:
                    page = await page.get_next()
                    for firm in page.data:
                        ...
        """
        if not self.pagination.has_next:
            raise exc.NoMorePagesError("This is the last page; no more results to fetch.")
        if self._client is None or self.pagination.next_page is None:
            raise RuntimeError(
                "MultipageList has no client bound — it was likely constructed manually "
                "or deserialized. Call `client.fetch_next_page(pagination.next_page)` "
                "directly, or bind a client with `.with_client(client)` first."
            )
        return await self._client.fetch_next_page(self.pagination.next_page)
