"""Tests for fca_api.types.pagination and the pagination machinery in async_api."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

import fca_api.async_api as async_api
import fca_api.exc as exc
import fca_api.types.pagination as pagination
from fca_api._paginate import _resume_ctx, _ResumeState, current_resume_state, paginated

# ---------------------------------------------------------------------------
# _PageState
# ---------------------------------------------------------------------------


class TestPageState:
    def test_encode_produces_valid_json(self):
        state = pagination._PageState(endpoint="search_frn", params={"firm_name": "Barclays"}, page=3)
        encoded = state.encode()
        assert json.loads(encoded) == {
            "page": 3,
            "endpoint": "search_frn",
            "params": {"firm_name": "Barclays"},
        }

    def test_decode_roundtrip(self):
        original = pagination._PageState(
            endpoint="get_firm_passport_permissions",
            params={"frn": "12345", "country": "FR", "result_count": 10},
            page=7,
        )
        assert pagination._PageState.decode(original.encode()) == original

    def test_first_factory(self):
        assert pagination._PageState.first() == pagination._PageState(page=1)

    def test_decode_roundtrip_position_only(self):
        # endpoint/params default empty — represents a position-only state.
        original = pagination._PageState(page=4)
        restored = pagination._PageState.decode(original.encode())
        assert restored == original
        assert restored.endpoint == ""
        assert restored.params == {}

    def test_frozen(self):
        state = pagination._PageState(endpoint="search_frn", params={}, page=1)
        import pydantic

        with pytest.raises((AttributeError, TypeError, pydantic.ValidationError)):
            state.page = 2  # type: ignore[misc]


# ---------------------------------------------------------------------------
# NextPageToken
# ---------------------------------------------------------------------------


class TestNextPageToken:
    def test_is_string_annotation(self):
        import typing

        args = typing.get_args(pagination.NextPageToken)
        assert args[0] is str

    def test_has_description_in_field_metadata(self):
        import typing

        args = typing.get_args(pagination.NextPageToken)
        field_info = args[1]
        assert hasattr(field_info, "description")
        assert "opaque" in field_info.description.lower() or "cursor" in field_info.description.lower()


# ---------------------------------------------------------------------------
# PageTokenSerializer
# ---------------------------------------------------------------------------


class TestPageTokenSerializer:
    def test_any_matching_object_satisfies_protocol(self):
        class MySerializer:
            def serialize(self, token: str) -> str:
                return f"enc:{token}"

            def deserialize(self, token: str) -> str:
                return token.removeprefix("enc:")

        assert isinstance(MySerializer(), pagination.PageTokenSerializer)

    def test_object_missing_method_does_not_satisfy_protocol(self):
        class Incomplete:
            def serialize(self, token: str) -> str:
                return token

        assert not isinstance(Incomplete(), pagination.PageTokenSerializer)

    def test_serialize_deserialize_roundtrip(self):
        class DoubleSerializer:
            def serialize(self, token: str) -> str:
                return token * 2

            def deserialize(self, token: str) -> str:
                assert len(token) % 2 == 0
                return token[: len(token) // 2]

        s = DoubleSerializer()
        raw = '{"page":4}'
        assert s.deserialize(s.serialize(raw)) == raw


# ---------------------------------------------------------------------------
# PaginationInfo
# ---------------------------------------------------------------------------


class TestPaginationInfo:
    def test_has_next_true_with_token(self):
        info = pagination.PaginationInfo(has_next=True, next_page='{"page":2}', size=100)
        assert info.has_next is True
        assert info.next_page == '{"page":2}'
        assert info.size == 100

    def test_has_next_false_no_token(self):
        info = pagination.PaginationInfo(has_next=False)
        assert info.has_next is False
        assert info.next_page is None
        assert info.size is None

    def test_frozen(self):
        import pydantic

        info = pagination.PaginationInfo(has_next=False)
        with pytest.raises((AttributeError, TypeError, pydantic.ValidationError)):
            info.has_next = True  # type: ignore[misc]

    def test_json_schema_has_all_fields(self):
        schema = pagination.PaginationInfo.model_json_schema()
        props = schema["properties"]
        assert "has_next" in props
        assert "next_page" in props
        assert "size" in props

    def test_model_dump(self):
        info = pagination.PaginationInfo(has_next=True, next_page="abc", size=42)
        assert info.model_dump() == {"has_next": True, "next_page": "abc", "size": 42}


# ---------------------------------------------------------------------------
# MultipageList — value object + get_next / with_client
# ---------------------------------------------------------------------------


class TestMultipageList:
    def test_construction_with_items(self):
        page = pagination.MultipageList(
            data=["a", "b", "c"],
            pagination=pagination.PaginationInfo(has_next=False),
        )
        assert page.data == ["a", "b", "c"]

    def test_construction_empty(self):
        page = pagination.MultipageList(
            data=[],
            pagination=pagination.PaginationInfo(has_next=False, size=0),
        )
        assert page.data == []
        assert page.pagination.size == 0

    def test_frozen(self):
        import pydantic

        page = pagination.MultipageList(
            data=[1, 2],
            pagination=pagination.PaginationInfo(has_next=False),
        )
        with pytest.raises((AttributeError, TypeError, pydantic.ValidationError)):
            page.data = [3, 4]  # type: ignore[misc]

    def test_model_dump(self):
        page = pagination.MultipageList(
            data=[1, 2],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=10),
        )
        d = page.model_dump()
        assert d["data"] == [1, 2]
        assert d["pagination"]["next_page"] == "tok"

    def test_pickle_roundtrip(self):
        import pickle

        page = pagination.MultipageList(
            data=[1, 2, 3],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=10),
        )
        restored = pickle.loads(pickle.dumps(page))
        assert restored == page

    @pytest.mark.asyncio
    async def test_get_next_raises_no_more_pages_when_terminal(self):
        page = pagination.MultipageList(
            data=["a"],
            pagination=pagination.PaginationInfo(has_next=False),
        )
        with pytest.raises(exc.NoMorePagesError):
            await page.get_next()

    @pytest.mark.asyncio
    async def test_get_next_raises_when_no_client_bound(self):
        # Manually-constructed (or deserialized) list has no client.
        page = pagination.MultipageList(
            data=["a"],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=5),
        )
        with pytest.raises(RuntimeError, match="no client bound"):
            await page.get_next()

    @pytest.mark.asyncio
    async def test_get_next_delegates_to_client_fetch_next_page(self):
        sentinel_next_page = pagination.MultipageList(
            data=["x"], pagination=pagination.PaginationInfo(has_next=False)
        )

        class StubClient:
            captured: list = []

            async def fetch_next_page(self, next_page):
                self.captured.append(next_page)
                return sentinel_next_page

        page = pagination.MultipageList(
            data=["a"],
            pagination=pagination.PaginationInfo(has_next=True, next_page="my-token", size=2),
        )
        client = StubClient()
        result = await page.with_client(client).get_next()
        assert result is sentinel_next_page
        assert client.captured == ["my-token"]

    def test_with_client_returns_self(self):
        page = pagination.MultipageList(
            data=[],
            pagination=pagination.PaginationInfo(has_next=False),
        )

        class StubClient:
            async def fetch_next_page(self, next_page):
                return page

        assert page.with_client(StubClient()) is page


# ---------------------------------------------------------------------------
# PaginatedResultInfo (internal — unchanged)
# ---------------------------------------------------------------------------


class TestPaginatedResultInfo:
    def test_basic_initialization(self):
        info = pagination.PaginatedResultInfo(page=1, per_page=10, total_count=25)
        assert info.page == 1
        assert info.next is None
        assert info.previous is None

    def test_with_urls(self):
        info = pagination.PaginatedResultInfo(
            page=2,
            per_page=10,
            total_count=25,
            next="https://api.example.com/page/3",
            previous="https://api.example.com/page/1",
        )
        assert str(info.next) == "https://api.example.com/page/3"
        assert str(info.previous) == "https://api.example.com/page/1"

    def test_total_pages_exact_division(self):
        assert pagination.PaginatedResultInfo(page=1, per_page=10, total_count=30).total_pages == 3

    def test_total_pages_with_remainder(self):
        assert pagination.PaginatedResultInfo(page=1, per_page=10, total_count=25).total_pages == 3

    def test_total_pages_single_page(self):
        assert pagination.PaginatedResultInfo(page=1, per_page=10, total_count=5).total_pages == 1

    def test_total_pages_empty(self):
        assert pagination.PaginatedResultInfo(page=1, per_page=10, total_count=0).total_pages == 0

    def test_model_validate_key_normalization(self):
        raw = {
            "Page ": 1,
            " Per_Page": 10,
            "TOTAL_COUNT   ": 25,
            " Next  ": "https://api.example.com/next",
            "Previous": None,
        }
        info = pagination.PaginatedResultInfo.model_validate(raw)
        assert info.page == 1
        assert info.per_page == 10
        assert info.total_count == 25
        assert str(info.next) == "https://api.example.com/next"

    def test_model_validate_missing_required_fields(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            pagination.PaginatedResultInfo.model_validate({})

    def test_model_validate_invalid_url(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            pagination.PaginatedResultInfo.model_validate(
                {"page": 1, "per_page": 10, "total_count": 25, "next": "not-a-valid-url"}
            )

    def test_total_pages_zero_per_page_raises(self):
        info = pagination.PaginatedResultInfo(page=1, per_page=0, total_count=25)
        with pytest.raises(ZeroDivisionError):
            _ = info.total_pages


# ---------------------------------------------------------------------------
# @paginated decorator + resume contextvar
# ---------------------------------------------------------------------------


class TestPaginatedDecorator:
    @pytest.mark.asyncio
    async def test_publishes_endpoint_and_params(self):
        captured: dict = {}

        @paginated()
        async def my_endpoint(self, firm_name: str, result_count: int = 1):
            state = current_resume_state()
            captured["endpoint"] = state.endpoint
            captured["params"] = state.params
            return _StubMultipageList()

        await my_endpoint("self-stub", "Acme", result_count=5)
        assert captured["endpoint"] == "my_endpoint"
        assert captured["params"] == {"firm_name": "Acme", "result_count": 5}

    @pytest.mark.asyncio
    async def test_excludes_self_by_default(self):
        captured: dict = {}

        @paginated()
        async def my_endpoint(self, q: str):
            captured["params"] = current_resume_state().params
            return _StubMultipageList()

        await my_endpoint("self-stub", q="hi")
        assert "self" not in captured["params"]
        assert captured["params"] == {"q": "hi"}

    @pytest.mark.asyncio
    async def test_resets_contextvar_on_return(self):
        @paginated()
        async def my_endpoint(self):
            return _StubMultipageList()

        await my_endpoint("self-stub")
        assert current_resume_state() == _ResumeState()  # empty / no active call

    @pytest.mark.asyncio
    async def test_resets_contextvar_on_exception(self):
        @paginated()
        async def my_endpoint(self):
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError):
            await my_endpoint("self-stub")
        assert current_resume_state() == _ResumeState()

    @pytest.mark.asyncio
    async def test_binds_self_as_client_on_result(self):
        sentinel_self = MagicMock()

        @paginated()
        async def my_endpoint(self):
            return _StubMultipageList()

        result = await my_endpoint(sentinel_self)
        assert result._client is sentinel_self


class _StubMultipageList:
    """Minimal stand-in for MultipageList that accepts ``_client`` assignment."""

    _client = None


# ---------------------------------------------------------------------------
# async_api._fetch_paginated — uses contextvars for resume state and outgoing token
# ---------------------------------------------------------------------------


def _make_raw_response(page: int, per_page: int, total_count: int, items: list, has_next: bool):
    resp = MagicMock()
    next_url = f"https://example.com/?pgnp={page + 1}" if has_next else None
    resp.result_info = {
        "Page": page,
        "Per_Page": per_page,
        "Total_Count": total_count,
        "Next": next_url,
        "Previous": None,
    }
    resp.data = items
    return resp


class TestFetchPaginated:
    def _make_client(self, serializer=None):
        client = async_api.Client.__new__(async_api.Client)
        client._page_token_serializer = serializer
        return client

    def _with_resume(self, *, outgoing=None, incoming=None):
        """Push outgoing and incoming resume states onto the contextvars.

        Returns a (reset_outgoing, reset_incoming) pair the test must call to
        restore — done via try/finally in each test that uses it.
        """
        out_token = _resume_ctx.set(outgoing) if outgoing is not None else None
        in_token = async_api._resume_from_ctx.set(incoming) if incoming is not None else None
        return out_token, in_token

    def _reset_resume(self, tokens):
        out_token, in_token = tokens
        if out_token is not None:
            _resume_ctx.reset(out_token)
        if in_token is not None:
            async_api._resume_from_ctx.reset(in_token)

    @pytest.mark.asyncio
    async def test_single_page_no_next(self):
        client = self._make_client()
        resp = _make_raw_response(1, 10, 3, ["a", "b", "c"], has_next=False)

        result = await client._fetch_paginated(
            fetch_page_fn=AsyncMock(return_value=resp),
            parse_data_fn=lambda data: data,
            result_count=1,
        )

        assert result.data == ["a", "b", "c"]
        assert result.pagination.has_next is False
        assert result.pagination.next_page is None
        assert result.pagination.size == 3

    @pytest.mark.asyncio
    async def test_outgoing_token_carries_endpoint_and_params_from_resume_ctx(self):
        client = self._make_client()
        resp = _make_raw_response(1, 5, 10, ["x", "y"], has_next=True)

        tokens = self._with_resume(outgoing=_ResumeState(endpoint="search_frn", params={"firm_name": "Acme"}))
        try:
            result = await client._fetch_paginated(
                fetch_page_fn=AsyncMock(return_value=resp),
                parse_data_fn=lambda data: data,
                result_count=1,
            )
        finally:
            self._reset_resume(tokens)

        assert result.pagination.next_page is not None
        decoded = pagination._PageState.decode(result.pagination.next_page)
        assert decoded.page == 2
        assert decoded.endpoint == "search_frn"
        assert decoded.params == {"firm_name": "Acme"}

    @pytest.mark.asyncio
    async def test_incoming_token_resumes_from_correct_page(self):
        client = self._make_client()
        page3 = _make_raw_response(3, 5, 15, list(range(10, 15)), has_next=False)

        async def fetch_page(p: int):
            assert p == 3, f"Expected page 3, got {p}"
            return page3

        tokens = self._with_resume(incoming=pagination._PageState(page=3))
        try:
            result = await client._fetch_paginated(
                fetch_page_fn=fetch_page,
                parse_data_fn=lambda data: data,
                result_count=1,
            )
        finally:
            self._reset_resume(tokens)

        assert result.data == list(range(10, 15))

    @pytest.mark.asyncio
    async def test_result_count_triggers_multi_page_fetch(self):
        client = self._make_client()
        responses = [
            _make_raw_response(1, 5, 15, list(range(5)), has_next=True),
            _make_raw_response(2, 5, 15, list(range(5, 10)), has_next=True),
            _make_raw_response(3, 5, 15, list(range(10, 15)), has_next=False),
        ]
        call_count = 0

        async def fetch_page(p: int):
            nonlocal call_count
            call_count += 1
            return responses[p - 1]

        result = await client._fetch_paginated(
            fetch_page_fn=fetch_page,
            parse_data_fn=lambda data: data,
            result_count=8,
        )

        assert call_count == 2
        assert len(result.data) == 10
        assert result.pagination.has_next is True

    @pytest.mark.asyncio
    async def test_stops_when_no_more_pages_before_result_count(self):
        client = self._make_client()
        page1 = _make_raw_response(1, 5, 5, list(range(5)), has_next=False)
        fetch = AsyncMock(return_value=page1)

        result = await client._fetch_paginated(
            fetch_page_fn=fetch,
            parse_data_fn=lambda data: data,
            result_count=100,
        )

        assert fetch.call_count == 1
        assert result.data == list(range(5))
        assert result.pagination.has_next is False

    @pytest.mark.asyncio
    async def test_serializer_encrypts_outgoing_token(self):
        class PrefixSerializer:
            def serialize(self, token: str) -> str:
                return f"ENC:{token}"

            def deserialize(self, token: str) -> str:
                return token.removeprefix("ENC:")

        client = self._make_client(serializer=PrefixSerializer())
        resp = _make_raw_response(1, 5, 10, ["a"], has_next=True)

        result = await client._fetch_paginated(
            fetch_page_fn=AsyncMock(return_value=resp),
            parse_data_fn=lambda data: data,
            result_count=1,
        )
        assert result.pagination.next_page is not None
        assert result.pagination.next_page.startswith("ENC:")

    @pytest.mark.asyncio
    async def test_response_with_no_result_info(self):
        client = self._make_client()
        resp = MagicMock()
        resp.result_info = None
        resp.data = ["only_item"]

        result = await client._fetch_paginated(
            fetch_page_fn=AsyncMock(return_value=resp),
            parse_data_fn=lambda data: data,
            result_count=1,
        )
        assert result.data == ["only_item"]
        assert result.pagination.has_next is False
        assert result.pagination.size is None

    @pytest.mark.asyncio
    async def test_response_with_none_data(self):
        client = self._make_client()
        resp = MagicMock()
        resp.result_info = {"Page": 1, "Per_Page": 10, "Total_Count": 0, "Next": None, "Previous": None}
        resp.data = None

        result = await client._fetch_paginated(
            fetch_page_fn=AsyncMock(return_value=resp),
            parse_data_fn=lambda data: data,
            result_count=1,
        )
        assert result.data == []
        assert result.pagination.has_next is False


# ---------------------------------------------------------------------------
# Client.fetch_next_page — token dispatcher with allowlist
# ---------------------------------------------------------------------------


class TestFetchNextPage:
    def _make_client(self, serializer=None):
        client = async_api.Client.__new__(async_api.Client)
        client._page_token_serializer = serializer
        return client

    @pytest.mark.asyncio
    async def test_dispatches_back_to_originating_endpoint(self):
        client = self._make_client()
        pages = {
            1: _make_raw_response(1, 2, 4, ["a", "b"], has_next=True),
            2: _make_raw_response(2, 2, 4, ["c", "d"], has_next=False),
        }
        seen: list[int] = []

        async def fetch_page(p: int):
            seen.append(p)
            return pages[p]

        # search_frn is on the allowlist; we monkeypatch the instance to use
        # our fake fetch_page rather than the real raw client.
        @paginated()
        async def search_frn(self, firm_name: str, result_count: int = 1):
            assert firm_name == "Barclays"
            return await self._fetch_paginated(
                fetch_page_fn=fetch_page,
                parse_data_fn=lambda data: data,
                result_count=result_count,
            )

        client.search_frn = search_frn.__get__(client, async_api.Client)  # type: ignore[attr-defined]

        first = await client.search_frn(firm_name="Barclays")
        assert seen == [1]
        assert first.pagination.has_next is True
        # _client must be bound by the decorator
        assert first._client is client

        second = await client.fetch_next_page(first.pagination.next_page)
        assert seen == [1, 2]
        assert second.data == ["c", "d"]
        assert second.pagination.has_next is False

    @pytest.mark.asyncio
    async def test_result_count_preserved_across_dispatch(self):
        client = self._make_client()
        pages = {
            i: _make_raw_response(i, 5, 20, list(range((i - 1) * 5, i * 5)), has_next=(i < 4)) for i in range(1, 5)
        }
        seen: list[int] = []

        async def fetch_page(p: int):
            seen.append(p)
            return pages[p]

        @paginated()
        async def search_frn(self, firm_name: str, result_count: int = 1):
            return await self._fetch_paginated(
                fetch_page_fn=fetch_page,
                parse_data_fn=lambda data: data,
                result_count=result_count,
            )

        client.search_frn = search_frn.__get__(client, async_api.Client)  # type: ignore[attr-defined]

        first = await client.search_frn(firm_name="Acme", result_count=8)
        assert seen == [1, 2]
        second = await client.fetch_next_page(first.pagination.next_page)
        # result_count=8 reused → pulls 3 & 4
        assert seen == [1, 2, 3, 4]
        assert second.data == list(range(10, 20))

    @pytest.mark.asyncio
    async def test_get_next_via_bound_client(self):
        client = self._make_client()
        pages = {
            1: _make_raw_response(1, 2, 4, ["a", "b"], has_next=True),
            2: _make_raw_response(2, 2, 4, ["c", "d"], has_next=False),
        }

        async def fetch_page(p: int):
            return pages[p]

        @paginated()
        async def search_frn(self, firm_name: str, result_count: int = 1):
            return await self._fetch_paginated(
                fetch_page_fn=fetch_page,
                parse_data_fn=lambda data: data,
                result_count=result_count,
            )

        client.search_frn = search_frn.__get__(client, async_api.Client)  # type: ignore[attr-defined]

        first = await client.search_frn(firm_name="X")
        second = await first.get_next()  # sugar over fetch_next_page
        assert second.data == ["c", "d"]

    @pytest.mark.asyncio
    async def test_rejects_endpoint_not_in_allowlist(self):
        client = self._make_client()

        # Build a state pointing at a non-resumable method.
        bad_token = client._encode_next_page(
            pagination._PageState(endpoint="aclose", params={}, page=2)
        )
        with pytest.raises(ValueError, match="resumable endpoint"):
            await client.fetch_next_page(bad_token)

    @pytest.mark.asyncio
    async def test_rejects_position_only_token(self):
        # Tokens whose endpoint is empty (e.g. legacy / hand-built) cannot
        # be replayed via fetch_next_page.
        client = self._make_client()
        bare_token = client._encode_next_page(pagination._PageState(page=2))
        with pytest.raises(ValueError):
            await client.fetch_next_page(bare_token)

    @pytest.mark.asyncio
    async def test_dispatch_through_serializer(self):
        class PrefixSerializer:
            def serialize(self, token: str) -> str:
                return f"ENC:{token}"

            def deserialize(self, token: str) -> str:
                assert token.startswith("ENC:"), "token was not encrypted"
                return token.removeprefix("ENC:")

        client = self._make_client(serializer=PrefixSerializer())
        pages = {
            1: _make_raw_response(1, 2, 4, ["a", "b"], has_next=True),
            2: _make_raw_response(2, 2, 4, ["c", "d"], has_next=False),
        }

        async def fetch_page(p: int):
            return pages[p]

        @paginated()
        async def search_frn(self, firm_name: str, result_count: int = 1):
            return await self._fetch_paginated(
                fetch_page_fn=fetch_page,
                parse_data_fn=lambda data: data,
                result_count=result_count,
            )

        client.search_frn = search_frn.__get__(client, async_api.Client)  # type: ignore[attr-defined]

        first = await client.search_frn(firm_name="X")
        assert first.pagination.next_page.startswith("ENC:")
        second = await client.fetch_next_page(first.pagination.next_page)
        assert second.data == ["c", "d"]

    @pytest.mark.asyncio
    async def test_resumable_endpoints_allowlist_matches_decorated_methods(self):
        # Catch drift: every method decorated with @paginated must be in the
        # allowlist, and the allowlist must not name methods that don't exist
        # or aren't decorated.
        import inspect

        decorated: set[str] = set()
        for name, member in inspect.getmembers(async_api.Client):
            if inspect.iscoroutinefunction(member) and getattr(member, "__wrapped__", None) is not None:
                # @paginated wraps with functools.wraps so __wrapped__ points at the original
                decorated.add(name)

        allowlist = async_api.Client._RESUMABLE_ENDPOINTS
        # Every allowlisted name must be a real method on Client.
        for name in allowlist:
            assert hasattr(async_api.Client, name), f"allowlist names a missing method: {name}"
        # No decorated paginated method should be silently absent from the allowlist
        # (would mean a real endpoint that fetch_next_page won't resume).
        missing = decorated - allowlist
        assert not missing, f"@paginated methods missing from _RESUMABLE_ENDPOINTS: {missing}"
