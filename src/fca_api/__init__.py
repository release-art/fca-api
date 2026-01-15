"""Financial Conduct Authority (FCA) Financial Services Register API Client.

This package provides both high-level and low-level Python clients for accessing
the UK Financial Conduct Authority's Financial Services Register API. It offers:

- **High-level client** (`fca_api.async_api.Client`): Validated, typed interface with pagination support
- **Raw client** (`fca_api.raw_api.RawClient`): Direct API access with minimal abstraction
- **Type system**: Comprehensive Pydantic models for all API responses
- **Async-first design**: Built on httpx for modern async/await patterns

Example:
    Basic usage with the high-level client::

        import asyncio
        import fca_api

        async def main():
            async with fca_api.async_api.Client(
                credentials=("your_email@example.com", "your_api_key")
            ) as client:
                # Search for firms
                results = await client.search_frn("Barclays")
                async for firm in results:
                    print(f"{firm.name} - {firm.frn}")

        asyncio.run(main())

See Also:
    - `FCA Developer Portal <https://register.fca.org.uk/Developer/s/>`_
    - `API Documentation <https://register.fca.org.uk/Developer/s/>`_
"""

from . import __version__, async_api, const, exc, raw_api, raw_status_codes, types
