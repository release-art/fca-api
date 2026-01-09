"""Base class for FCA API types."""

import typing
import pydantic

class Base(pydantic.BaseModel):
    """Base class for FCA API types."""

    _expected_api_version: typing.Annotated[
        typing.ClassVar[str],
        pydantic.PrivateAttr(
            default="unset"
        ),
    ]