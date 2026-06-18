"""Search result models for firms, individuals, and funds.

Returned from :meth:`Client.search_frn`, :meth:`Client.search_irn`, and
:meth:`Client.search_prn`. Pass the reference number (FRN/IRN/PRN) to the
corresponding ``get_*`` method for full details.
"""

from typing import Annotated

import pydantic

from . import annotations, base


class FirmSearchResult(base.Base):
    """A firm record from a firm-name search.

    Use ``frn`` with :meth:`Client.get_firm` for full firm details.
    """

    url: Annotated[
        pydantic.HttpUrl | None,
        pydantic.Field(
            description="The URL of the firm's record in the FCA register.",
        ),
        annotations.FcaApiFieldInfo(marks=[annotations.FcaApiField.InternalUrl]),
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
    """An individual record from an individual-name search.

    Use ``irn`` with :meth:`Client.get_individual` for full details.
    """

    url: Annotated[
        pydantic.HttpUrl | None,
        pydantic.Field(
            description="The URL of the individual's record in the FCA register.",
        ),
        annotations.FcaApiFieldInfo(marks=[annotations.FcaApiField.InternalUrl]),
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
        annotations.FcaApiFieldInfo(marks=[annotations.FcaApiField.InternalUrl]),
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
