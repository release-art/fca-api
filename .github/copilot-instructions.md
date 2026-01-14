# FCA API Library - AI Coding Agent Instructions

## Project Overview
This is an async Python client for the UK Financial Conduct Authority's Financial Services Register API. It provides two layers:
- **Raw client** (`src/fca_api/raw.py`): Direct API access with minimal abstraction
- **High-level client** (`src/fca_api/api.py`): Validated, typed interface with pagination support

## Architecture Patterns

### Two-Layer Client Design
- `raw.RawClient`: Handles HTTP requests, authentication, rate limiting
- `api.Client`: Wraps raw client with Pydantic validation and pagination
- Always use `api.Client` for new features unless direct HTTP control is needed

### Async-First Design
- All API methods are `async def` using `httpx.AsyncClient`
- Use `async with` context managers for client lifecycle
- Test fixtures use `@pytest_asyncio.fixture` for async setup

### Custom Pagination System
- `MultipageList[T]` in `src/fca_api/types/pagination.py` handles lazy-loading API pages
- Implements `__len__`, `__getitem__`, and `__aiter__` for seamless iteration
- Call `._asyinc_init()` after creation to fetch first page metadata

```python
# Usage pattern in api.Client methods
async def search_frn(self, firm_name: str) -> types.pagination.MultipageList[types.api.FirmSearchResult]:
    out = types.pagination.MultipageList(
        fetch_page=lambda page_idx: self._paginated_search(...)
    )
    await out._asyinc_init()  # Critical: initializes pagination metadata
    return out
```

## Development Workflow

### Build System: PDM + Make
- Use `pdm` for dependency management, not pip
- `bin/test.sh` to run pytest with coverage. You can pass test paths/selectors to it (or any other additional pytest arguments) to restrict or customize the test run.
<!-- - `make docs` builds Sphinx documentation -->

### Sophisticated Testing Infrastructure
- **Two-tier testing**: `test_raw/` for HTTP layer, `test_client/` for high-level API
- **Response caching system**: `CachingSession` eliminates live API calls during tests
- Cache files in `tests/units/*/resources/` organized by test class/method hierarchy
- Cache modes: `readonly` (CI), `writeonly` (record), `fetch_missing` (development)
- Authentication via `X-AUTH-EMAIL`/`X-AUTH-KEY` headers (FCA API requirement)
- Intelligent cache filenames from URL paths and parameters for human readability

```python
# Test client setup pattern - automatically handles caching
@pytest_asyncio.fixture
async def test_client(caching_session_subclass, test_api_username, test_api_key, test_resources_path):
    async with caching_session_subclass(
        headers={"X-AUTH-EMAIL": test_api_username, "X-AUTH-KEY": test_api_key},
        cache_dir=test_resources_path,
        cache_mode="fetch_missing",
    ) as api_session:
        yield fca_api.api.Client(credentials=api_session)

# Test structure follows strict patterns
class TestFirmSearch:  # Creates TestFirmSearch/ directory
    @pytest.mark.asyncio
    async def test_multipage_results(self, test_client):  # Creates test_multipage_results/ subdir
        # Cache files automatically stored by method name
        response = await test_client.search_frn("revolution")
        assert len(response) > 50  # Test pagination metadata
        async for item in response:  # Test async iteration
            assert item.name
```

### Testing Conventions
- All tests use `@pytest.mark.asyncio` for async methods
- Mock with `mocker.create_autospec()` for precise HTTP client control
- Test both positive (results found) and negative (empty results) scenarios
- Validate pagination behavior: `len()`, indexing, and `async for` iteration
- Error testing: HTTP failures, malformed responses, invalid parameters

### Type System
- All types in `src/fca_api/types/` inherit from `pydantic.BaseModel`
- Each type defines `_expected_api_version` class attribute
- Base classes in `types/base.py` provide common validation patterns
- API response types in `types/api.py` for search results

## Key Conventions

### Resource Type System
- `const.ResourceTypes` enum defines firm/fund/individual patterns
- Each has `type_name` and `endpoint_base` for URL construction
- Use `ResourceTypes.from_type_name()` for lookup by string

### Error Handling
- Custom exceptions in `src/fca_api/exc.py` inherit from `FcaBaseError`
- API version mismatches trigger `RuntimeWarning`, not exceptions
- Use `_check_api_version()` in high-level client methods

### Version Management
- Version defined in `src/fca_api/__version__.py`
- Extracted by Makefile: `grep __version__ src/fca_api/__version__.py | cut -d '=' -f 2 | xargs`

## Critical Implementation Details

### Authentication Flow
The client accepts either:
1. Tuple of `(username, api_key)` - creates internal httpx client
2. Pre-configured `httpx.AsyncClient` - for testing with mock sessions

### Rate Limiting
- `api_limiter` parameter accepts async context manager for rate limiting
- Defaults to no-op limiter if not provided
- Implement custom limiters following `LimiterContextT` type

When adding new search methods, follow the `_paginated_search` pattern with proper type validation and pagination initialization.