from typing import Annotated, Optional

import pydantic

from . import base, field_parsers


class IndividualDetails(base.Base):
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
            description="URL to the individual's disciplinary history, if any.",
            validation_alias=pydantic.AliasChoices("current roles & activities", "disciplinary_history"),
            serialization_alias="disciplinary_history",
        ),
    ]
