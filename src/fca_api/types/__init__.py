"""Pydantic models and type definitions for FCA API responses.

This package contains comprehensive type definitions for all FCA Financial
Services Register API responses. The types are built using Pydantic for
automatic validation, serialization, and IDE support.

Modules:
    - `base`: Base classes with common validation logic
    - `field_parsers`: Custom field parsing and validation functions
    - `firm`: Types for firm-related API responses
    - `individual`: Types for individual-related API responses
    - `markets`: Types for regulated market data
    - `pagination`: Pagination handling and multipage list types
    - `products`: Types for fund and product responses
    - `search`: Types for search result responses
    - `settings`: Configuration for model validation behavior

Key Features:
    - **Automatic validation**: All API responses are validated against schemas
    - **Type safety**: Full type hints for IDE support and static analysis
    - **Flexible parsing**: Handles API field name variations and formats
    - **Extra field handling**: Captures unexpected fields for future compatibility
    - **Consistent interfaces**: Common patterns across all response types

Usage:
    Types are automatically used by the high-level client::

        firm = await client.get_firm("123456")
        # `firm` is a validated `types.firm.FirmDetails` instance
        print(f"Name: {firm.name}")  # IDE autocomplete works
        print(f"Status: {firm.status}")  # Type-safe access

    Manual validation from raw data::

        raw_response = await raw_client.get_firm("123456")
        firm = types.firm.FirmDetails.model_validate(raw_response.data[0])

See Also:
    - `fca_api.async_api.Client`: High-level client that returns typed responses
    - `Pydantic Documentation <https://docs.pydantic.dev/>`_
"""

from . import base, field_parsers, firm, individual, markets, pagination, products, search, settings
