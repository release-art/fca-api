from typing import Annotated, Optional

import pydantic

from . import base, field_parsers


class RegulatedMarket(base.Base):
    """Details of a regulated market on the FCA register.

    This model is used by high-level helpers such as
    ``Client.get_regulated_markets`` to provide a typed view over the
    regulated markets dataset.
    """

    name: Annotated[
        str,
        pydantic.Field(
            description="The name of the regulated market.",
        ),
    ]
    trading_name: Annotated[
        Optional[str],
        pydantic.Field(
            description="The trading name of the regulated market.",
            validation_alias=pydantic.AliasChoices("tradingname", "trading_name"),
            serialization_alias="trading_name",
        ),
        field_parsers.StrOrNone,
    ]
    type: Annotated[
        str,
        pydantic.Field(
            description="The type of regulated market.",
            validation_alias=pydantic.AliasChoices("type of business or individual", "type"),
            serialization_alias="type",
        ),
    ]
    status: Annotated[
        str,
        pydantic.Field(
            description="The status of the regulated market.",
        ),
        pydantic.StringConstraints(
            to_upper=True,
            strip_whitespace=True,
        ),
    ]
    reference_number: Annotated[
        Optional[str],
        pydantic.Field(
            description="The reference number of the regulated market.",
            validation_alias=pydantic.AliasChoices("reference number", "reference_number"),
            serialization_alias="reference_number",
        ),
        pydantic.StringConstraints(
            to_upper=True,
            strip_whitespace=True,
        ),
        field_parsers.StrOrNone,
    ]

    # urls
    firm_url: Annotated[
        Optional[pydantic.HttpUrl],
        pydantic.Field(
            description="URL to the regulated market's firm details.",
            validation_alias=pydantic.AliasChoices("firmurl", "firm_url"),
            serialization_alias="firm_url",
        ),
    ]
