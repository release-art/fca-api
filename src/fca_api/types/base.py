"""Base class for FCA API types."""

import typing

import pydantic

from . import settings


class Base(pydantic.BaseModel):
    """Base class for FCA API types."""

    @classmethod
    def model_validate(cls, data: typing.Any) -> "Base":
        """A customised validation method that normalizes keys to lowercase if a dict is passed."""
        if isinstance(data, dict):
            updated_data = {}
            for key, value in data.items():
                if isinstance(key, str):
                    key = key.lower().strip()
                updated_data[key] = value
            data = updated_data
        if cls.model_config and cls.model_config.get("extra"):
            # Use model-specific extra settings if defined
            return super().model_validate(data)
        else:
            return super().model_validate(data, extra=settings.model_validate_extra)


class RelaxedBase(Base):
    """A base class for FCA API types accumulates any unexpected fields."""

    model_config = pydantic.ConfigDict(extra="allow")

    def get_additional_fields(self) -> dict[str, typing.Any]:
        return dict(self.__pydantic_extra__)
