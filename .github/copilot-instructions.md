# FCA API Library - AI Coding Agent Instructions

## Project Overview
This is an async Python client for the UK Financial Conduct Authority's Financial Services Register API. It provides two layers:
- **Raw client** (`src/fca_api/raw.py`): Direct API access with minimal abstraction
- **High-level client** (`src/fca_api/api.py`): Validated, typed interface with pagination support

The codebase features comprehensive Sphinx-compatible docstrings following Google/NumPy style throughout all user-facing modules, with extensive type hints and usage examples.

## Architecture Patterns

### Two-Layer Client Design
- `raw.RawClient`: Handles HTTP requests, authentication, rate limiting
- `api.Client`: Wraps raw client with Pydantic validation and pagination
- Always use `api.Client` for new features unless direct HTTP control is needed
- Both clients support async context manager pattern with `__aenter__`/`__aexit__`

### Async-First Design
- All API methods are `async def` using `httpx.AsyncClient`
- Use `async with` context managers for client lifecycle (preferred pattern)
- Manual session management requires calling `aclose()` for cleanup
- Test fixtures use `@pytest_asyncio.fixture` for async setup

### Documentation Standards
- All user-facing code has comprehensive Sphinx-compatible docstrings
- Follow Google/NumPy docstring style with Args/Returns/Example sections
- Include usage examples in docstrings for complex patterns
- Type hints are mandatory for all public APIs
- Exception handling is documented with Raises sections

### Custom Pagination System
- `MultipageList[T]` in `src/fca_api/types/pagination.py` handles lazy-loading API pages
- Implements `__len__`, `__getitem__`, and `__aiter__` for seamless iteration  
- Call `._async_init()` after creation to fetch first page metadata (note: corrected from typo)

```python
# Usage pattern in api.Client methods
async def search_frn(self, firm_name: str) -> types.pagination.MultipageList[types.search.FirmSearchResult]:
    out = types.pagination.MultipageList(
        fetch_page=lambda page_idx: self._paginated_search(...)
    )
    await out._async_init()  # Critical: initializes pagination metadata
    return out
```

### Type System & Validation
- All types in `src/fca_api/types/` inherit from `pydantic.BaseModel` 
- Each type defines `_expected_api_version` class attribute for version checking
- Base classes in `types/base.py` provide common validation patterns
- Search result types in `types/search.py` for all query responses
- Use `_check_api_version()` in high-level client methods for version validation

## Development Workflow

### Build System: PDM + Make
- Use `pdm` for dependency management, not pip
- `bin/test.sh` runs pytest with coverage - pass test paths/selectors to restrict runs
- Makefile handles version extraction and common tasks

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
        yield fca_api.async_api.Client(credentials=api_session)

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