"""Search result types for FCA API responses.

This module defines Pydantic models for the different types of search results
returned by the FCA Financial Services Register API. These models provide
type-safe access to search result data with automatic validation.

Classes:
    - `FirmSearchResult`: Results from firm name searches
    - `IndividualSearchResult`: Results from individual name searches
    - `FundSearchResult`: Results from fund/product name searches

Each search result type contains core identification fields (reference numbers,
names, status) plus type-specific additional information.

Example:
    Working with search results::

        # Firm search results
        firms = await client.search_frn("Barclays")
        async for firm in firms:
            print(f"FRN: {firm.frn}")
            print(f"Name: {firm.name}")
            print(f"Status: {firm.status}")
            print(f"Type: {firm.type}")
            if firm.url:
                print(f"Details: {firm.url}")

        # Individual search results
        individuals = await client.search_irn("John Smith")
        async for person in individuals:
            print(f"IRN: {person.irn}")
            print(f"Name: {person.name}")
            print(f"Status: {person.status}")

        # Fund search results
        funds = await client.search_prn("Vanguard")
        async for fund in funds:
            print(f"PRN: {fund.prn}")
            print(f"Name: {fund.name}")
            print(f"Status: {fund.status}")

Note:
    Search results provide summary information. Use the reference numbers
    (FRN, IRN, PRN) with the detailed get methods to retrieve complete
    information about specific entities.

See Also:
    - `fca_api.async_api.Client.search_frn`: Search for firms
    - `fca_api.async_api.Client.search_irn`: Search for individuals
    - `fca_api.async_api.Client.search_prn`: Search for funds
"""

from typing import Annotated

import pydantic

from . import base


class FirmSearchResult(base.Base):
    """Search result for a firm from the FCA Financial Services Register.

    Represents a single firm found in search results, containing core
    identification and status information. This is returned by firm
    name searches and provides the essential data needed to identify
    and access detailed firm information.

    Attributes:
        url: Direct link to the firm's page in the FCA register (may be None)
        frn: The firm's unique Financial Reference Number (6-7 digits)
        status: Current regulatory status (e.g., "Authorised", "Cancelled")
        type: Type of business or organization (e.g., "Limited Company")
        name: The firm's registered name
        address: The firm's registered address (may be None)

    Example:
        Access firm search result data::

            firms = await client.search_frn("Barclays Bank")
            if len(firms) > 0:
                firm = firms[0]

                print(f"Found: {firm.name}")
                print(f"FRN: {firm.frn}")
                print(f"Status: {firm.status}")
                print(f"Type: {firm.type}")

                if firm.address:
                    print(f"Address: {firm.address}")

                # Get detailed information
                details = await client.get_firm(firm.frn)

    Note:
        The `url` field may be None for some results. The `frn` field
        is the key identifier for retrieving detailed firm information
        using `client.get_firm()`.
    """

    url: Annotated[
        pydantic.HttpUrl | None,
        pydantic.Field(
            description="The URL of the firm's record in the FCA register.",
        ),
    ]
    frn: Annotated[
        str,
        pydantic.Field(
            description="The firm's Financial Reference Number (FRN).",
            validation_alias=pydantic.AliasChoices("reference number", "frn"),
            serialization_alias="frn",
        ),
    ]
    status: Annotated[
        str,
        pydantic.Field(
            description="The firm's status.",
            to_lower=True,
            trim_whitespace=True,
        ),
    ]
    type: Annotated[
        str,
        pydantic.Field(
            description="The type of the resource.",
            validation_alias=pydantic.AliasChoices("type of business or individual", "type"),
            serialization_alias="type",
            to_lower=True,
            trim_whitespace=True,
        ),
    ]
    name: Annotated[
        str,
        pydantic.Field(
            description="The firm's name.",
            trim_whitespace=True,
        ),
    ]


class IndividualSearchResult(base.Base):
    """Search result for an individual from the FCA register.

    Represents a single individual found in search results, containing core
    identification and status information. This is returned by individual
    name searches and provides the essential data needed to identify and
    access detailed individual information.

    Attributes:
        url: Direct link to the individual's page in the FCA register (may be None)
        irn: The individual's unique Individual Reference Number (IRN)
        name: The individual's full name as shown in the register
        status: Current regulatory status of the individual
        type: Type of individual entry (for example, "approved person")

    Example:
        Access individual search result data::

            individuals = await client.search_irn("Jane Smith")
            if len(individuals) > 0:
                person = individuals[0]

                print(f"Found: {person.name}")
                print(f"IRN: {person.irn}")
                print(f"Status: {person.status}")
                print(f"Type: {person.type}")

                if person.url:
                    print(f"Details: {person.url}")

    Note:
        The ``irn`` field is the key identifier for retrieving detailed
        individual information using ``client.get_individual()``.
    """

    url: Annotated[
        pydantic.HttpUrl | None,
        pydantic.Field(
            description="The URL of the individual's record in the FCA register.",
        ),
    ]
    irn: Annotated[
        str,
        pydantic.Field(
            description="The individual's Reference Number (IRN).",
            validation_alias=pydantic.AliasChoices("reference number", "irn"),
            serialization_alias="irn",
        ),
    ]
    name: Annotated[
        str,
        pydantic.Field(
            description="The individual's name.",
            trim_whitespace=True,
        ),
    ]
    status: Annotated[
        str,
        pydantic.Field(
            description="The individual's status.",
        ),
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
    ]
    type: Annotated[
        str,
        pydantic.Field(
            description="The individual's type.",
            validation_alias=pydantic.AliasChoices("type of business or individual", "type"),
            serialization_alias="type",
        ),
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
    ]


class FundSearchResult(base.Base):
    """Search result for a fund or other financial product.

    Represents a single product found in search results, containing core
    identification and status information. This is returned by product
    name searches and provides the essential data needed to identify and
    access detailed product information.

    Attributes:
        url: Direct link to the product's page in the FCA register (may be None)
        prn: The product's unique Product Reference Number (PRN)
        status: Current regulatory status of the product
        type: Type of product (for example, "UCITS", "AIF")
        name: The product's name

    Example:
        Access product search result data::

            funds = await client.search_prn("Vanguard")
            if len(funds) > 0:
                product = funds[0]

                print(f"Found: {product.name}")
                print(f"PRN: {product.prn}")
                print(f"Status: {product.status}")
                print(f"Type: {product.type}")

                if product.url:
                    print(f"Details: {product.url}")

    Note:
        The ``prn`` field is the key identifier for retrieving detailed
        product information using ``client.get_fund()``.
    """

    url: Annotated[
        pydantic.HttpUrl | None,
        pydantic.Field(
            description="The URL of the product's record in the FCA register.",
        ),
    ]
    prn: Annotated[
        str,
        pydantic.Field(
            description="The product's reference number (PRN).",
            validation_alias=pydantic.AliasChoices("reference number", "prn"),
            serialization_alias="prn",
        ),
    ]
    status: Annotated[
        str,
        pydantic.Field(
            description="The product's status.",
        ),
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
    ]
    type: Annotated[
        str,
        pydantic.Field(
            description="The type of the resource.",
            validation_alias=pydantic.AliasChoices("type of business or individual", "type"),
            serialization_alias="type",
        ),
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
    ]
    name: Annotated[
        str,
        pydantic.Field(
            description="The product's name.",
        ),
    ]
