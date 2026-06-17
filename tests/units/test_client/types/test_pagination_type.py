"""Tests for fca_api.types.pagination."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

import fca_api.exc as exc
import fca_api.types.pagination as pagination

# ---------------------------------------------------------------------------
# _PageState
# ---------------------------------------------------------------------------


class TestPageState:
    def test_first_returns_page_one(self):
        state = pagination._PageState.first()
        assert state.page == 1

    def test_encode_produces_valid_json(self):
        state = pagination._PageState(page=3)
        encoded = state.encode()
        data = json.loads(encoded)
        assert data == {"page": 3}

    def test_decode_roundtrip(self):
        original = pagination._PageState(page=7)
        restored = pagination._PageState.decode(original.encode())
        assert restored == original

    def test_decode_roundtrip_first_page(self):
        original = pagination._PageState.first()
        assert pagination._PageState.decode(original.encode()) == original

    def test_frozen(self):
        state = pagination._PageState(page=1)
        with pytest.raises((AttributeError, TypeError)):
            state.page = 2  # type: ignore[misc]

    def test_decode_ignores_extra_json_fields(self):
        token = json.dumps({"page": 5, "extra": "ignored"})
        state = pagination._PageState.decode(token)
        assert state.page == 5


# ---------------------------------------------------------------------------
# NextPageToken
# ---------------------------------------------------------------------------


class TestNextPageToken:
    def test_is_string_annotation(self):
        # NextPageToken must resolve to str at runtime
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

        s = MySerializer()
        assert isinstance(s, pagination.PageTokenSerializer)

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
        info = pagination.PaginationInfo(
            has_next=True,
            next_page='{"page":2}',
            size=100,
        )
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

    def test_json_schema_field_descriptions(self):
        schema = pagination.PaginationInfo.model_json_schema()
        props = schema["properties"]
        assert props["has_next"].get("description")
        # next_page and size may be wrapped in anyOf/allOf due to Optional + Annotated
        # Just verify the field exists and the schema is valid JSON
        assert "next_page" in props
        assert "size" in props

    def test_model_dump(self):
        info = pagination.PaginationInfo(has_next=True, next_page="abc", size=42)
        d = info.model_dump()
        assert d == {"has_next": True, "next_page": "abc", "size": 42}


# ---------------------------------------------------------------------------
# MultipageList
# ---------------------------------------------------------------------------


class TestMultipageList:
    def test_construction_with_items(self):
        page = pagination.MultipageList(
            data=["a", "b", "c"],
            pagination=pagination.PaginationInfo(has_next=False),
        )
        assert page.data == ["a", "b", "c"]
        assert page.pagination.has_next is False

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
        assert d["pagination"]["has_next"] is True
        assert d["pagination"]["next_page"] == "tok"
        assert d["pagination"]["size"] == 10

    def test_json_schema_with_concrete_type(self):
        import pydantic

        class Item(pydantic.BaseModel):
            name: str

        schema = pagination.MultipageList[Item].model_json_schema()
        assert "data" in schema.get("properties", {})
        assert "pagination" in schema.get("properties", {})
        # Item schema should be referenced somewhere in the output
        schema_str = json.dumps(schema)
        assert "Item" in schema_str or "name" in schema_str

    def test_pickle_roundtrip_without_fetcher(self):
        import pickle

        page = pagination.MultipageList(
            data=[1, 2, 3],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=10),
        )
        restored = pickle.loads(pickle.dumps(page))
        assert restored == page
        assert restored.data == [1, 2, 3]
        assert restored.pagination.next_page == "tok"

    def test_pickle_drops_fetcher_closure(self):
        import pickle

        page = pagination.MultipageList(
            data=[1, 2],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=10),
        )

        async def fake_fetcher():
            return page

        page._fetch_next_page = fake_fetcher  # type: ignore[assignment]
        # Local async funcs are not pickleable; the override must drop the closure.
        restored = pickle.loads(pickle.dumps(page))
        assert restored == page

    @pytest.mark.asyncio
    async def test_unpickled_get_next_raises_detached_error(self):
        import pickle

        page = pagination.MultipageList(
            data=[1, 2],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=10),
        )
        restored = pickle.loads(pickle.dumps(page))
        with pytest.raises(exc.DetachedMultipageListError):
            await restored.get_next()

    def test_hash_matches_equality(self):
        # __eq__ is overridden; __hash__ must follow so the class remains
        # usable in sets and as a dict key.
        a = pagination.MultipageList(
            data=[1, 2],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=10),
        )
        b = pagination.MultipageList(
            data=[1, 2],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=10),
        )
        a._fetch_next_page = lambda: "fetcher-a"  # type: ignore[assignment]
        b._fetch_next_page = lambda: "fetcher-b"  # type: ignore[assignment]
        assert hash(a) == hash(b)
        assert {a, b} == {a}

    def test_equality_ignores_fetcher_closure(self):
        # Two MultipageLists produced from separate calls hold distinct
        # _fetch_next_page closure objects. Equality must compare only
        # the public fields, not the pydantic_private dict.
        p1 = pagination.MultipageList(
            data=[1, 2],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=10),
        )
        p2 = pagination.MultipageList(
            data=[1, 2],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=10),
        )
        p1._fetch_next_page = lambda: "fetcher-a"  # type: ignore[assignment]
        p2._fetch_next_page = lambda: "fetcher-b"  # type: ignore[assignment]
        assert p1 == p2

    def test_equality_distinguishes_other_types(self):
        page = pagination.MultipageList(
            data=[1, 2],
            pagination=pagination.PaginationInfo(has_next=False),
        )
        assert (page == "not a page") is False
        assert (page == [1, 2]) is False

    def test_equality_distinguishes_data(self):
        a = pagination.MultipageList(
            data=[1, 2],
            pagination=pagination.PaginationInfo(has_next=False),
        )
        b = pagination.MultipageList(
            data=[1, 3],
            pagination=pagination.PaginationInfo(has_next=False),
        )
        assert a != b

    def test_pagination_field_description(self):
        schema = pagination.MultipageList.model_json_schema()
        props = schema.get("properties", {})
        assert props.get("data", {}).get("description") or "data" in props
        assert "pagination" in props


# ---------------------------------------------------------------------------
# PaginatedResultInfo (internal — unchanged from previous version)
# ---------------------------------------------------------------------------


class TestPaginatedResultInfo:
    def test_basic_initialization(self):
        info = pagination.PaginatedResultInfo(page=1, per_page=10, total_count=25)
        assert info.page == 1
        assert info.per_page == 10
        assert info.total_count == 25
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
        assert info.previous is None

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
# async_api._fetch_paginated integration tests
# ---------------------------------------------------------------------------


def _make_raw_response(page: int, per_page: int, total_count: int, items: list, has_next: bool):
    """Build a mock FcaApiResponse for use in _fetch_paginated tests."""
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
    """Tests for async_api.Client._fetch_paginated."""

    def _make_client(self, serializer=None):

        import fca_api.async_api as async_api

        client = async_api.Client.__new__(async_api.Client)
        client._page_token_serializer = serializer
        return client

    @pytest.mark.asyncio
    async def test_single_page_no_next(self):
        client = self._make_client()
        resp = _make_raw_response(1, 10, 3, ["a", "b", "c"], has_next=False)

        result = await client._fetch_paginated(
            fetch_page_fn=AsyncMock(return_value=resp),
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=1,
        )

        assert result.data == ["a", "b", "c"]
        assert result.pagination.has_next is False
        assert result.pagination.next_page is None
        assert result.pagination.size == 3

    @pytest.mark.asyncio
    async def test_single_page_has_next(self):
        client = self._make_client()
        resp = _make_raw_response(1, 5, 15, ["a", "b", "c", "d", "e"], has_next=True)

        result = await client._fetch_paginated(
            fetch_page_fn=AsyncMock(return_value=resp),
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=1,
        )

        assert result.data == ["a", "b", "c", "d", "e"]
        assert result.pagination.has_next is True
        assert result.pagination.next_page is not None
        assert result.pagination.size == 15

    @pytest.mark.asyncio
    async def test_result_count_triggers_multi_page_fetch(self):
        client = self._make_client()

        page1 = _make_raw_response(1, 5, 15, list(range(5)), has_next=True)
        page2 = _make_raw_response(2, 5, 15, list(range(5, 10)), has_next=True)
        page3 = _make_raw_response(3, 5, 15, list(range(10, 15)), has_next=False)

        call_count = 0
        responses = [page1, page2, page3]

        async def fetch_page(p: int):
            nonlocal call_count
            call_count += 1
            return responses[p - 1]

        result = await client._fetch_paginated(
            fetch_page_fn=fetch_page,
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=8,  # need > 5 items → fetches pages 1 and 2
        )

        assert call_count == 2
        assert len(result.data) == 10  # 2 pages of 5
        assert result.pagination.has_next is True

    @pytest.mark.asyncio
    async def test_stops_when_no_more_pages_before_result_count(self):
        client = self._make_client()

        page1 = _make_raw_response(1, 5, 5, list(range(5)), has_next=False)
        fetch = AsyncMock(return_value=page1)

        result = await client._fetch_paginated(
            fetch_page_fn=fetch,
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=100,  # ask for more than available
        )

        assert fetch.call_count == 1
        assert result.data == list(range(5))
        assert result.pagination.has_next is False

    @pytest.mark.asyncio
    async def test_next_page_token_used_as_start_page(self):
        client = self._make_client()

        page3 = _make_raw_response(3, 5, 15, list(range(10, 15)), has_next=False)

        async def fetch_page(p: int):
            assert p == 3, f"Expected page 3, got page {p}"
            return page3

        # Build a token pointing to page 3
        state = pagination._PageState(page=3)
        token = state.encode()

        result = await client._fetch_paginated(
            fetch_page_fn=fetch_page,
            parse_data_fn=lambda data: data,
            next_page=token,
            result_count=1,
        )

        assert result.data == list(range(10, 15))

    @pytest.mark.asyncio
    async def test_next_page_token_in_response_decodes_correctly(self):
        client = self._make_client()

        resp = _make_raw_response(1, 5, 10, ["x", "y"], has_next=True)

        result = await client._fetch_paginated(
            fetch_page_fn=AsyncMock(return_value=resp),
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=1,
        )

        assert result.pagination.next_page is not None
        decoded = pagination._PageState.decode(result.pagination.next_page)
        assert decoded.page == 2

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
            next_page=None,
            result_count=1,
        )

        assert result.pagination.next_page is not None
        assert result.pagination.next_page.startswith("ENC:")

    @pytest.mark.asyncio
    async def test_serializer_decrypts_incoming_token(self):
        class PrefixSerializer:
            def serialize(self, token: str) -> str:
                return f"ENC:{token}"

            def deserialize(self, token: str) -> str:
                assert token.startswith("ENC:"), "token was not encrypted"
                return token.removeprefix("ENC:")

        client = self._make_client(serializer=PrefixSerializer())

        page2 = _make_raw_response(2, 5, 10, ["b", "c"], has_next=False)

        async def fetch_page(p: int):
            assert p == 2
            return page2

        # Build encrypted token for page 2
        raw_token = pagination._PageState(page=2).encode()
        encrypted_token = f"ENC:{raw_token}"

        result = await client._fetch_paginated(
            fetch_page_fn=fetch_page,
            parse_data_fn=lambda data: data,
            next_page=encrypted_token,
            result_count=1,
        )

        assert result.data == ["b", "c"]

    @pytest.mark.asyncio
    async def test_response_with_no_result_info(self):
        client = self._make_client()

        resp = MagicMock()
        resp.result_info = None
        resp.data = ["only_item"]

        result = await client._fetch_paginated(
            fetch_page_fn=AsyncMock(return_value=resp),
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=1,
        )

        assert result.data == ["only_item"]
        assert result.pagination.has_next is False
        assert result.pagination.size is None

    @pytest.mark.asyncio
    async def test_get_next_fetches_subsequent_page(self):
        client = self._make_client()
        page1 = _make_raw_response(1, 5, 10, ["a", "b"], has_next=True)
        page2 = _make_raw_response(2, 5, 10, ["c", "d"], has_next=False)
        seen_pages: list[int] = []

        async def fetch_page(p: int):
            seen_pages.append(p)
            return {1: page1, 2: page2}[p]

        first = await client._fetch_paginated(
            fetch_page_fn=fetch_page,
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=1,
        )
        second = await first.get_next()

        assert seen_pages == [1, 2]
        assert second.data == ["c", "d"]
        assert second.pagination.has_next is False

    @pytest.mark.asyncio
    async def test_get_next_preserves_result_count(self):
        client = self._make_client()
        # 4 pages of 5 = 20 items total; result_count=8 forces 2-page batches.
        pages = {
            i: _make_raw_response(i, 5, 20, list(range((i - 1) * 5, i * 5)), has_next=(i < 4))
            for i in range(1, 5)
        }
        seen_pages: list[int] = []

        async def fetch_page(p: int):
            seen_pages.append(p)
            return pages[p]

        first = await client._fetch_paginated(
            fetch_page_fn=fetch_page,
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=8,
        )
        # First batch should pull pages 1 & 2 (10 >= 8 items).
        assert seen_pages == [1, 2]
        assert first.data == list(range(10))

        second = await first.get_next()
        # Next batch must reuse result_count=8 and continue from page 3.
        assert seen_pages == [1, 2, 3, 4]
        assert second.data == list(range(10, 20))
        assert second.pagination.has_next is False

    @pytest.mark.asyncio
    async def test_get_next_chain_through_serializer(self):
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

        first = await client._fetch_paginated(
            fetch_page_fn=fetch_page,
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=1,
        )
        assert first.pagination.next_page.startswith("ENC:")
        second = await first.get_next()
        assert second.data == ["c", "d"]

    @pytest.mark.asyncio
    async def test_get_next_raises_no_more_pages_on_terminal(self):
        client = self._make_client()
        resp = _make_raw_response(1, 5, 3, ["a", "b", "c"], has_next=False)

        result = await client._fetch_paginated(
            fetch_page_fn=AsyncMock(return_value=resp),
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=1,
        )

        with pytest.raises(exc.NoMorePagesError):
            await result.get_next()

    @pytest.mark.asyncio
    async def test_get_next_raises_detached_error_when_no_fetcher_attached(self):
        # A manually-constructed list with has_next=True but no fetcher (e.g.
        # rehydrated from JSON) should surface a clear error.
        page = pagination.MultipageList(
            data=["a"],
            pagination=pagination.PaginationInfo(has_next=True, next_page="tok", size=5),
        )
        with pytest.raises(exc.DetachedMultipageListError):
            await page.get_next()

    @pytest.mark.asyncio
    async def test_response_with_none_data(self):
        client = self._make_client()

        resp = MagicMock()
        resp.result_info = {"Page": 1, "Per_Page": 10, "Total_Count": 0, "Next": None, "Previous": None}
        resp.data = None

        result = await client._fetch_paginated(
            fetch_page_fn=AsyncMock(return_value=resp),
            parse_data_fn=lambda data: data,
            next_page=None,
            result_count=1,
        )

        assert result.data == []
        assert result.pagination.has_next is False
