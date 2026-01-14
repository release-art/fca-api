"""Base class for FCA API types."""

import typing

import pydantic


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
        return super().model_validate(data)
