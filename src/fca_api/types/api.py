"""Search return types for the FCA API."""

from typing import Annotated

import pydantic

from . import base


class FirmSearchResult(base.Base):
    """A model representing a firm search result."""

    _expected_api_version = "FSR-API-04-01-11"

    url: Annotated[
        pydantic.HttpUrl | None,
        pydantic.Field(
            description="The URL of the firm's record in the FCA register.",
            validation_alias=pydantic.AliasChoices("URL", "url"),
            serialization_alias="url",
        ),
    ]
    frn: Annotated[
        str,
        pydantic.Field(
            description="The firm's Financial Reference Number (FRN).",
            validation_alias=pydantic.AliasChoices("Reference Number", "frn"),
            serialization_alias="frn",
        ),
    ]
    status: Annotated[
        str,
        pydantic.Field(
            description="The firm's status.",
            validation_alias=pydantic.AliasChoices("Status", "status"),
            serialization_alias="status",
            to_lower=True,
            trim_whitespace=True,
        ),
    ]
    type: Annotated[
        str,
        pydantic.Field(
            description="The type of the resource.",
            validation_alias=pydantic.AliasChoices("Type of business or Individual", "type"),
            serialization_alias="type",
            to_lower=True,
            trim_whitespace=True,
        ),
    ]
    name: Annotated[
        str,
        pydantic.Field(
            description="The firm's name.",
            validation_alias=pydantic.AliasChoices("Name", "name"),
            serialization_alias="name",
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
            validation_alias=pydantic.AliasChoices("URL", "url"),
            serialization_alias="url",
        ),
    ]
    irn: Annotated[
        str,
        pydantic.Field(
            description="The individual's Reference Number (IRN).",
            validation_alias=pydantic.AliasChoices("Reference Number", "irn"),
            serialization_alias="irn",
        ),
    ]
    name: Annotated[
        str,
        pydantic.Field(
            description="The individual's name.",
            validation_alias=pydantic.AliasChoices("Name", "name"),
            serialization_alias="name",
            trim_whitespace=True,
        ),
    ]


class FundSearchResult(base.Base):
    """A model representing a fund search result."""

    _expected_api_version = "FSR-API-04-01-00"

    url: Annotated[
        pydantic.HttpUrl | None,
        pydantic.Field(
            description="The URL of the firm's record in the FCA register.",
            validation_alias=pydantic.AliasChoices("URL", "url"),
            serialization_alias="url",
        ),
    ]
    prn: Annotated[
        str,
        pydantic.Field(
            description="The fund's Financial Reference Number (FRN).",
            validation_alias=pydantic.AliasChoices("Reference Number", "prn"),
            serialization_alias="prn",
        ),
    ]
    status: Annotated[
        str,
        pydantic.Field(
            description="The firm's status.",
            validation_alias=pydantic.AliasChoices("Status", "status"),
            serialization_alias="status",
            to_lower=True,
            trim_whitespace=True,
        ),
    ]
    type: Annotated[
        str,
        pydantic.Field(
            description="The type of the resource.",
            validation_alias=pydantic.AliasChoices("Type of business or Individual", "type"),
            serialization_alias="type",
            to_lower=True,
            trim_whitespace=True,
        ),
    ]
    name: Annotated[
        str,
        pydantic.Field(
            description="The firm's name.",
            validation_alias=pydantic.AliasChoices("Name", "name"),
            serialization_alias="name",
            trim_whitespace=True,
        ),
    ]
