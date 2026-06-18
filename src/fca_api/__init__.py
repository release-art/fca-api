"""Async Python client for the UK FCA Financial Services Register API.

Use :class:`fca_api.async_api.Client` for typed responses and cursor pagination,
or :class:`fca_api.raw_api.RawClient` for direct access to the raw JSON.

Example::

    import asyncio
    import fca_api

    async def main():
        async with fca_api.async_api.Client(
            credentials=("your_email@example.com", "your_api_key")
        ) as client:
            page = await client.search_frn("Barclays")
            for firm in page.data:
                print(f"{firm.name} - {firm.frn}")

    asyncio.run(main())

See `FCA Developer Portal <https://register.fca.org.uk/Developer/s/>`_.
"""

from . import __version__, async_api, const, exc, raw_api, raw_status_codes, types
