import datetime
from typing import Annotated, Literal, Optional

import pydantic

from . import base, field_parsers


class Individual(base.Base):
    """Individual (physical person) details."""

    irn: Annotated[
        str,
        pydantic.Field(
            description="Individual Reference Number (IRN) assigned by the FCA.",
            example="BXK69703",
        ),
        pydantic.StringConstraints(
            to_upper=True,
            strip_whitespace=True,
        ),
    ]
    full_name: Annotated[
        str,
        pydantic.Field(
            description="Full name of the individual.",
            validation_alias=pydantic.AliasChoices("full name", "full_name"),
            serialization_alias="full_name",
        ),
    ]
    commonly_used_name: Annotated[
        Optional[str],
        pydantic.Field(
            description="Commonly used name of the individual, if any.",
            validation_alias=pydantic.AliasChoices("commonly used name", "commonly_used_name"),
            serialization_alias="commonly_used_name",
        ),
        field_parsers.StrOrNone,
    ]
    disciplinary_history: Annotated[
        Optional[pydantic.HttpUrl],
        pydantic.Field(
            description="URL to the individual's disciplinary history, if any.",
            validation_alias=pydantic.AliasChoices("disciplinary history", "disciplinary_history"),
            serialization_alias="disciplinary_history",
        ),
    ]
    status: Annotated[
        str,
        pydantic.Field(
            description="Current status of the individual with the FCA.",
        ),
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
    ]
    current_roles_and_activities: Annotated[
        Optional[pydantic.HttpUrl],
        pydantic.Field(
            description="URL to the individual's current roles and activities, if available.",
            validation_alias=pydantic.AliasChoices("current roles & activities", "current_roles_and_activities"),
            serialization_alias="current_roles_and_activities",
        ),
    ]


class IndividualControlledFunction(base.Base):
    """Individual Controlled Function details."""

    type: Annotated[
        Literal["current", "previous"],
        pydantic.Field(
            description="Type of controlled function - current or previous.",
            validation_alias=pydantic.AliasChoices("fca_api_lst_type", "type"),
            serialization_alias="type",
        ),
    ]
    name: Annotated[
        str,
        pydantic.Field(
            description="Name of the controlled function.",
        ),
    ]
    restriction: Annotated[
        Optional[str],
        pydantic.Field(
            description="Any restrictions associated with the controlled function.",
        ),
        field_parsers.StrOrNone,
    ]
    restriction_start_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="Start date of any restriction associated with the controlled function.",
            validation_alias=pydantic.AliasChoices("suspension / restriction start date", "restriction_start_date"),
            serialization_alias="restriction_start_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    restriction_end_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="End date of any restriction associated with the controlled function.",
            validation_alias=pydantic.AliasChoices("suspension / restriction end date", "restriction_end_date"),
            serialization_alias="restriction_end_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    customer_engagement_method: Annotated[
        str,
        pydantic.Field(
            description="Method of customer engagement for the controlled function.",
            validation_alias=pydantic.AliasChoices("customer engagement method", "customer_engagement_method"),
            serialization_alias="customer_engagement_method",
        ),
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
    ]
    effective_date: Annotated[
        datetime.datetime,
        pydantic.Field(
            description="Effective date of the controlled function.",
            validation_alias=pydantic.AliasChoices("effective date", "effective_date"),
            serialization_alias="effective_date",
        ),
        field_parsers.ParseFcaDate,
    ]
    firm_name: Annotated[
        str,
        pydantic.Field(
            description="Name of the firm associated with the controlled function.",
            validation_alias=pydantic.AliasChoices("firm name", "firm_name"),
            serialization_alias="firm_name",
        ),
    ]
    end_date: Annotated[
        Optional[datetime.datetime],
        pydantic.Field(
            description="End date of any restriction associated with the controlled function.",
            validation_alias=pydantic.AliasChoices("end date", "end_date"),
            serialization_alias="end_date",
            default=None,
        ),
        field_parsers.ParseFcaDate,
    ]

    url: Annotated[
        pydantic.HttpUrl,
        pydantic.Field(
            description="URL to the controlled function details.",
        ),
    ]


class IndividualDisciplinaryRecord(base.Base):
    """Individual Disciplinary Record details."""

    type_of_action: Annotated[
        str,
        pydantic.Field(
            description="Type of disciplinary action taken.",
            validation_alias=pydantic.AliasChoices("typeofaction", "type_of_action"),
            serialization_alias="type_of_action",
        ),
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
    ]
    enforcement_type: Annotated[
        str,
        pydantic.Field(
            description="Type of disciplinary action taken.",
            validation_alias=pydantic.AliasChoices("enforcementtype", "enforcement_type"),
            serialization_alias="enforcement_type",
        ),
        pydantic.StringConstraints(
            to_lower=True,
            strip_whitespace=True,
        ),
    ]
    type_of_description: Annotated[
        str,
        pydantic.Field(
            description="Description of the disciplinary action taken.",
            validation_alias=pydantic.AliasChoices("typeofdescription", "type_of_description"),
            serialization_alias="type_of_description",
        ),
        pydantic.StringConstraints(
            strip_whitespace=True,
        ),
    ]
    action_effective_from: Annotated[
        datetime.datetime,
        pydantic.Field(
            description="Date when the disciplinary action became effective.",
            validation_alias=pydantic.AliasChoices("actioneffectivefrom", "action_effective_from"),
            serialization_alias="action_effective_from",
        ),
        field_parsers.ParseFcaDate,
    ]
