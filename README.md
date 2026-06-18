# fca-api

[![CI](https://github.com/release-art/fca-api/actions/workflows/ci.yml/badge.svg)](https://github.com/release-art/fca-api/actions/workflows/ci.yml)
[![CodeQL](https://github.com/release-art/fca-api/actions/workflows/codeql.yml/badge.svg)](https://github.com/release-art/fca-api/actions/workflows/codeql.yml)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![PyPI version](https://img.shields.io/pypi/v/fca-api?logo=python&color=41bb13)](https://pypi.org/project/fca-api)

An async Python client for the UK Financial Conduct Authority's [Financial Services Register](https://register.fca.org.uk/s/) [RESTful API](https://register.fca.org.uk/Developer/s/).

Covers firms, individuals, funds, permissions, disciplinary history, and regulated markets, with Pydantic-typed responses and cursor-based pagination.

## Requirements

- Python 3.11+
- `httpx`, `pydantic`

## Installation

```bash
pip install fca-api
```

## Quick Start

```python
import asyncio
import fca_api

async def main():
    async with fca_api.async_api.Client(
        credentials=("your.email@example.com", "your_api_key")
    ) as client:
        page = await client.search_frn("Barclays")
        for firm in page.data:
            print(f"{firm.name} (FRN: {firm.frn}) — {firm.status}")

        if page.data:
            details = await client.get_firm(page.data[0].frn)
            print(details.name, details.status, details.effective_date)

if __name__ == "__main__":
    asyncio.run(main())
```

## Two clients

- **`fca_api.async_api.Client`** — Pydantic-typed responses, cursor pagination, the default choice.
- **`fca_api.raw_api.RawClient`** — thin wrapper around the HTTP endpoints; raw JSON in, raw JSON out.

## Usage Examples

### Pagination

```python
async with fca_api.async_api.Client(credentials=("email", "key")) as client:
    page = await client.search_frn("revolution")
    while True:
        for firm in page.data:
            print(f"{firm.name} — {firm.status}")
        if not page.pagination.has_next:
            break
        page = await client.fetch_next_page(page.pagination.next_page)

    # Or collect at least N items in one call:
    page = await client.search_frn("revolution", result_count=100)
```

The `next_page` token is self-contained — it embeds the endpoint and arguments,
so a separate process can resume with only the token in hand. See
`PageTokenSerializer` if you want to sign or encrypt tokens crossing a trust boundary.

### Firm information

```python
firm = await client.get_firm("123456")
print(firm.name, firm.status)

addresses = await client.get_firm_addresses("123456")
for address in addresses.data:
    print(", ".join(address.address_lines))
```

### Individual and fund searches

```python
people = await client.search_irn("John Smith")
for person in people.data:
    print(f"{person.name} (IRN: {person.irn})")

funds = await client.search_prn("Vanguard")
for fund in funds.data:
    print(f"{fund.name} (PRN: {fund.prn})")
```

### Error handling

```python
import fca_api.exc

try:
    firm = await client.get_firm("invalid_frn")
except fca_api.exc.FcaRequestError as e:
    print(f"API request failed: {e}")
```

### Rate limiting

Pass any async context manager factory as `api_limiter`; the client enters it
around each request.

```python
from asyncio_throttle import Throttler

async with fca_api.async_api.Client(
    credentials=("email", "key"),
    api_limiter=Throttler(rate_limit=10),
) as client:
    page = await client.search_frn("test")
```

### Raw client

```python
async with fca_api.raw_api.RawClient(credentials=("email", "key")) as client:
    response = await client.search_frn("Barclays")
    for item in response.data or []:
        print(item)
    print(response.result_info)
```

## Documentation

Full reference at [docs.release.art/fca-api](https://docs.release.art/fca-api/).
Every public class and method carries a docstring; use `help()` in the REPL or
your IDE.

## Authentication

Get credentials from the [FCA Developer Portal](https://register.fca.org.uk/Developer/s/)
(free registration). Keep them out of version control.

## License

Mozilla Public License 2.0 — see [LICENSE](LICENSE).