import datetime
from typing import Annotated, Optional

import pydantic

from . import base, field_parsers


class ProductDetails(base.Base):
    """Core details for a financial product (for example a fund).

    Captures key attributes of a product as presented in the FCA register,
    including scheme type, operator and links to related resources such as
    the operator firm, sub-funds and CIS depositary.
    """

    type: Annotated[
        str,
        pydantic.Field(
            description="The type of resource represented.",
            validation_alias=pydantic.AliasChoices("product type", "product_type"),
            serialization_alias="product_type",
        ),
    ]
    status: Annotated[
        str,
        pydantic.Field(
            description="Current status of the product.",
        ),
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
    ]
    cis_depositary_name: Annotated[
        Optional[str],
        pydantic.Field(
            description="Name of the CIS depositary for the product, if applicable.",
            validation_alias=pydantic.AliasChoices("cis depositary name", "cis_depositary_name"),
            serialization_alias="cis_depositary_name",
        ),
        field_parsers.StrOrNone,
    ]
    operator_name: Annotated[
        str,
        pydantic.Field(
            description="Name of the operator of the product.",
            validation_alias=pydantic.AliasChoices("operator name", "operator_name"),
            serialization_alias="operator_name",
        ),
    ]
    effective_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="The date the product details became effective.",
            validation_alias=pydantic.AliasChoices("effective date", "effective_date"),
            serialization_alias="effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    icvc_registration_no: Annotated[
        Optional[str],
        pydantic.Field(
            description="The ICVC registration number of the product, if applicable.",
            validation_alias=pydantic.AliasChoices("icvc registration no", "icvc_registration_no"),
            serialization_alias="icvc_registration_no",
        ),
        field_parsers.StrOrNone,
        pydantic.StringConstraints(
            to_upper=True,
            strip_whitespace=True,
        ),
    ]
    mmf_nav_type: Annotated[
        Optional[str],
        pydantic.Field(
            description="The MMF NAV type of the product, if applicable.",
            validation_alias=pydantic.AliasChoices("mmf nav type", "mmf_nav_type"),
            serialization_alias="mmf_nav_type",
        ),
        field_parsers.StrOrNone,
    ]
    scheme_type: Annotated[
        str,
        pydantic.Field(
            description="The scheme type of the product, if applicable.",
            validation_alias=pydantic.AliasChoices("scheme type", "scheme_type"),
            serialization_alias="scheme_type",
        ),
        pydantic.StringConstraints(
            to_upper=True,
            strip_whitespace=True,
        ),
    ]
    mmf_term_type: Annotated[
        Optional[str],
        pydantic.Field(
            description="The MMF term type of the product, if applicable.",
            validation_alias=pydantic.AliasChoices("mmf term type", "mmf_term_type"),
            serialization_alias="mmf_term_type",
        ),
        field_parsers.StrOrNone,
    ]

    # URLs
    operator_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to the operator of the product.",
            validation_alias=pydantic.AliasChoices("operator", "operator_url"),
            serialization_alias="operator_url",
        ),
    ]
    sub_funds_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to the sub-funds of the product.",
            validation_alias=pydantic.AliasChoices("sub-funds", "sub_funds_url"),
            serialization_alias="sub_funds_url",
        ),
    ]
    other_name_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to the other names of the product.",
            validation_alias=pydantic.AliasChoices("other name", "other_name_url"),
            serialization_alias="other_name_url",
        ),
    ]
    cis_depositary_url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to the CIS depositary of the product.",
            validation_alias=pydantic.AliasChoices("cis depositary", "cis_depositary_url"),
            serialization_alias="cis_depositary_url",
        ),
    ]


class ProductNameAlias(base.Base):
    """An alternate or secondary name for a financial product.

    The FCA register can list multiple names for the same product over time;
    this model records the name and the period for which it was effective.
    """

    name: Annotated[
        str,
        pydantic.Field(
            description="The alternate or secondary name of the product.",
            validation_alias=pydantic.AliasChoices("product other name", "name"),
            serialization_alias="name",
        ),
    ]
    effective_from: Annotated[
        datetime.datetime,
        pydantic.Field(
            description="The date from which the alternate or secondary name is effective.",
            validation_alias=pydantic.AliasChoices("effective from", "effective_from"),
            serialization_alias="effective_from",
        ),
        field_parsers.ParseFcaDate,
    ]
    effective_to: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="The date until which the alternate or secondary name is effective.",
            validation_alias=pydantic.AliasChoices("effective to", "effective_to"),
            serialization_alias="effective_to",
        ),
        field_parsers.ParseFcaDate,
    ]


class SubFundDetails(base.Base):
    """Details of a sub-fund within a financial product.

    Sub-funds inherit many characteristics from the parent product but have
    their own name, type and detail page in the register.
    """

    name: Annotated[
        str,
        pydantic.Field(
            description="The name of the sub-fund.",
        ),
    ]

    type: Annotated[
        str,
        pydantic.Field(
            description="The type of the sub-fund.",
            validation_alias=pydantic.AliasChoices("sub-fund type", "type"),
            serialization_alias="type",
        ),
        pydantic.StringConstraints(
            to_upper=True,
            strip_whitespace=True,
        ),
    ]

    url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to the sub-fund details.",
        ),
    ]
