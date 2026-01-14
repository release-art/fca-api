from typing import Annotated

import pydantic

from . import base


class FirmDetails(base.Base):
    frn: Annotated[str, pydantic.Field(alias="frn")]
    name: Annotated[
        str,
        pydantic.Field(
            description="Name of the company.",
            validation_alias=pydantic.AliasChoices("organisation name", "name"),
            serialization_alias="name",
        ),
    ]
    status: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The firm's status.",
        ),
    ]
    type: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="The type of the resource.",
            validation_alias=pydantic.AliasChoices("business type", "type"),
            serialization_alias="type",
        ),
    ]
    companies_house_number: Annotated[
        str,
        pydantic.Field(
            description="The firm's Companies House number.",
            validation_alias=pydantic.AliasChoices("companies house number", "companies_house_number"),
            serialization_alias="companies_house_number",
        ),
    ]
    client_money_permission: Annotated[
        str,
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
        pydantic.Field(
            description="Indicates whether the firm has client money permission.",
            validation_alias=pydantic.AliasChoices("client money permission", "client_money_permission"),
            serialization_alias="client_money_permission",
        ),
    ]

    # URLs
    address_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="The URL of the firm's address record in the FCA register.",
            validation_alias=pydantic.AliasChoices("address", "address_url"),
            serialization_alias="address_url",
        ),
    ]
    appointed_representative_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="The URL of the firm's appointed representative list in the FCA register.",
            validation_alias=pydantic.AliasChoices("appointed representative", "appointed_representative_url"),
            serialization_alias="appointed_representative_url",
        ),
    ]
    disciplinary_history_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="The URL of the firm's disciplinary history in the FCA register.",
            validation_alias=pydantic.AliasChoices("disciplinaryhistory", "disciplinary_history_url"),
            serialization_alias="disciplinary_history_url",
        ),
    ]
