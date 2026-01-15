# fca-api

[![CI](https://github.com/release-art/fca-api/actions/workflows/ci.yml/badge.svg)](https://github.com/release-art/fca-api/actions/workflows/ci.yml)
[![CodeQL](https://github.com/release-art/fca-api/actions/workflows/codeql.yml/badge.svg)](https://github.com/release-art/fca-api/actions/workflows/codeql.yml)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![PyPI version](https://img.shields.io/pypi/v/fca-api?logo=python&color=41bb13)](https://pypi.org/project/fca-api)

A comprehensive async Python client library for the UK Financial Conduct Authority's [Financial Services Register](https://register.fca.org.uk/s/) [RESTful API](https://register.fca.org.uk/Developer/s/).

## Overview

This package provides both high-level and low-level asynchronous interfaces to interact with the FCA's Financial Services Register API. It offers type-safe, well-documented access to query information about:

- **Financial firms** and their comprehensive details
- **Individual professionals** in the financial services industry  
- **Investment funds** and collective investment schemes
- **Regulatory permissions** and restrictions
- **Disciplinary actions** and enforcement history
- **Regulated markets** and trading venues

> **Note:** This is an async fork of the [`financial-services-register-api`](https://github.com/sr-murthy/financial-services-register-api) package, completely rewritten for modern async/await patterns with comprehensive type safety and documentation.

## Requirements

- Python 3.11 or higher
- httpx library for async HTTP requests
- pydantic for data validation and parsing

## Installation

Install from PyPI using pip:

```bash
pip install fca-api
```

## Quick Start

Here's a simple example to get you started with the high-level client:

```python
import asyncio
import fca_api

async def main():
    # Using async context manager (recommended)
    async with fca_api.async_api.Client(
        credentials=("your.email@example.com", "your_api_key")
    ) as client:
        
        # Search for firms by name
        firms = await client.search_frn("Barclays")
        print(f"Found {len(firms)} firms matching 'Barclays'")
        
        # Iterate through paginated results
        async for firm in firms:
            print(f"• {firm.name} (FRN: {firm.frn}) - Status: {firm.status}")
        
        # Get detailed information about a specific firm
        if len(firms) > 0:
            firm_details = await client.get_firm(firms[0].frn)
            print(f"\nFirm Details:")
            print(f"Name: {firm_details.name}")
            print(f"Status: {firm_details.status}")
            print(f"Effective Date: {firm_details.effective_date}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Architecture

The library provides two complementary interfaces:

### High-Level Client (`fca_api.async_api.Client`)
- **Type-safe**: All responses are validated with Pydantic models
- **Pagination**: Automatic lazy-loading pagination with `async for` support
- **Convenient**: Intuitive methods like `search_frn()`, `get_firm()`, etc.
- **Error handling**: Meaningful exceptions and validation

### Raw Client (`fca_api.raw_api.RawClient`) 
- **Direct access**: Minimal abstraction over HTTP API
- **Flexible**: For advanced use cases and custom processing
- **Performance**: Lower overhead for bulk operations
- **Testing**: Ideal for debugging and API exploration

## Key Features

- **Asynchronous Operations**: Built with async/await for efficient concurrent requests
- **Comprehensive Documentation**: Extensive docstrings and examples for all methods
- **Type Safety**: Full type annotation support with Pydantic validation
- **Smart Pagination**: Lazy-loading pagination with automatic page fetching
- **Robust Error Handling**: Meaningful exceptions with detailed context
- **High Performance**: Optimized for both single queries and bulk operations
- **Well Tested**: Comprehensive test suite with response caching
- **Extensible**: Clean architecture for custom extensions

## Usage Examples

### Searching and Pagination

```python
import fca_api

async with fca_api.async_api.Client(credentials=("email", "key")) as client:
    # Search returns a lazy-loading paginated list
    results = await client.search_frn("revolution")
    
    # Check total results without loading all pages
    print(f"Total results: {len(results)}")
    
    # Access specific items by index (loads pages as needed)
    first_result = results[0]
    
    # Iterate through all results efficiently
    async for firm in results:
        print(f"{firm.name} - {firm.status}")
    
    # Or load all pages at once for bulk processing
    await results.fetch_all_pages()
```

### Firm Information

```python
# Get comprehensive firm details
firm = await client.get_firm("123456")  # Using FRN
print(f"Firm: {firm.name}")
print(f"Status: {firm.status}")

# Get related information
addresses = await client.get_firm_addresses("123456")
permissions = await client.get_firm_permissions("123456")
individuals = await client.get_firm_individuals("123456")

async for address in addresses:
    print(f"Address: {', '.join(address.address_lines)}")
```

### Individual and Fund Searches

```python
# Search for individuals
individuals = await client.search_irn("John Smith")
async for person in individuals:
    print(f"{person.name} (IRN: {person.irn})")

# Search for funds/products
funds = await client.search_prn("Vanguard")
async for fund in funds:
    print(f"{fund.name} (PRN: {fund.prn})")
```

### Error Handling

```python
import fca_api.exc

try:
    firm = await client.get_firm("invalid_frn")
except fca_api.exc.FcaRequestError as e:
    print(f"API request failed: {e}")
except fca_api.exc.FcaBaseError as e:
    print(f"General API error: {e}")
```

### Rate Limiting

```python
from asyncio_throttle import Throttler

# Limit to 10 requests per second
throttler = Throttler(rate_limit=10)

async with fca_api.async_api.Client(
    credentials=("email", "key"),
    api_limiter=throttler
) as client:
    # All requests will be automatically rate limited
    results = await client.search_frn("test")
```

## Raw Client Usage

For advanced use cases or when you need direct API access:

```python
import fca_api.raw

client = fca_api.raw_api.RawClient(
    credentials=("email", "key")
)

# Direct API calls return raw responses
response = await client.search_frn("Barclays", page=0)

if response.fca_api_status == "Success":
    for item in response.data:
        print(f"Raw data: {item}")
        
print(f"Pagination info: {response.result_info}")
```

## Documentation

The library includes comprehensive documentation:

- **In-code documentation**: All classes and methods have detailed docstrings
- **Type hints**: Complete type information for IDE support
- **Examples**: Practical examples in every docstring
- **API reference**: Auto-generated from docstrings (Sphinx-compatible)

Access documentation in your IDE or Python REPL:

```python
import fca_api
help(fca_api.async_api.Client)           # High-level client
help(fca_api.async_api.Client.search_frn) # Specific method
help(fca_api.types.firm.FirmDetails) # Response types
```

For complete API reference and advanced usage, visit the [full documentation](https://docs.release.art/fca-api/).

## Contributing

Contributions are welcome! Please see [contributing guidelines](https://docs.release.art/fca-api/sources/contributing.html) on how to contribute to this project.

## License

This project is licensed under the Mozilla Public License 2.0. See the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please:

1. Check the comprehensive in-code documentation with `help()`
2. Review the [complete documentation](https://docs.release.art/fca-api/)
3. Search existing [GitHub issues](https://github.com/release-art/fca-api/issues)
4. Create a new issue if your problem hasn't been addressed

## API Authentication

To use this library, you need API credentials from the FCA Developer Portal:

1. Visit [FCA Developer Portal](https://register.fca.org.uk/Developer/s/)
2. Register for an account
3. Generate API credentials (email and API key)
4. Use these credentials when initializing the client

**Note**: Keep your API credentials secure and never commit them to version control.