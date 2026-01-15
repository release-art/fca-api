"""Search return types for the FCA API."""

from typing import Annotated

import pydantic

from . import base


class FirmSearchResult(base.Base):
    """A model representing a firm search result."""

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
    """A model representing an individual search result."""

    _expected_api_version = "FSR-API-04-01-00"

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
    """A model representing a fund search result."""

    _expected_api_version = "FSR-API-04-01-00"

    url: Annotated[
        pydantic.HttpUrl | None,
        pydantic.Field(
            description="The URL of the firm's record in the FCA register.",
        ),
    ]
    prn: Annotated[
        str,
        pydantic.Field(
            description="The fund's Financial Reference Number (FRN).",
            validation_alias=pydantic.AliasChoices("reference number", "prn"),
            serialization_alias="prn",
        ),
    ]
    status: Annotated[
        str,
        pydantic.Field(
            description="The firm's status.",
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
            description="The firm's name.",
        ),
    ]
