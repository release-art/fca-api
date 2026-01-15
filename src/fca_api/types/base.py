"""Base classes for FCA API type definitions.

This module provides the foundation classes for all FCA API response models.
These base classes handle common patterns like:

- **Field normalization**: Converting API field names to lowercase
- **Extra field handling**: Capturing unexpected fields for compatibility
- **Validation configuration**: Consistent validation behavior across types
- **Skip markers**: Ignoring fields marked as "[notinuse]" by the API

The base classes ensure consistent behavior across all API response types
while providing flexibility for handling API changes and variations.

Classes:
    - `Base`: Standard base class for most API types
    - `RelaxedBase`: Base class that captures extra/unknown fields

Example:
    Creating a custom API type::

        class MyFirmData(Base):
            name: str
            frn: str
            status: str

        # Validates and normalizes field names
        data = MyFirmData.model_validate({
            "Name": "Test Firm",     # -> "name"
            "FRN": "123456",        # -> "frn"
            "Status": "Active"      # -> "status"
        })

    Using RelaxedBase for unknown fields::

        class FlexibleType(RelaxedBase):
            required_field: str

        data = FlexibleType.model_validate({
            "required_field": "value",
            "unknown_field": "captured"
        })

        print(data.get_additional_fields())  # {"unknown_field": "captured"}
"""

import typing

import pydantic

from . import settings


class Base(pydantic.BaseModel):
    """Base class for FCA API response models.

    This base class provides common functionality for all FCA API types:

    - **Field name normalization**: Converts API field names to lowercase
    - **Skip unused fields**: Ignores fields marked with "[notinuse]"
    - **Consistent validation**: Uses package-wide validation settings
    - **Type safety**: Provides proper Pydantic model inheritance

    All API response models should inherit from this class to ensure
    consistent behavior and proper handling of API response variations.

    Features:
        - Automatic lowercase conversion of field names
        - Filtering of "[notinuse]" fields from API responses
        - Standardized validation configuration
        - Support for both strict and flexible validation modes

    Example:
        Define a custom API model::

            class FirmSummary(Base):
                name: str
                frn: str
                status: str

            # API response with mixed case field names
            api_data = {
                "Name": "Example Firm",
                "FRN": "123456",
                "Status": "Authorised",
                "Internal_Field[notinuse]": "ignored"
            }

            # Validation handles normalization automatically
            firm = FirmSummary.model_validate(api_data)
            print(firm.name)    # "Example Firm"
            print(firm.frn)     # "123456"
            print(firm.status)  # "Authorised"
            # "Internal_Field[notinuse]" is automatically ignored

    Note:
        The `model_validate` method is customized to handle FCA API
        response patterns. Use this instead of the standard Pydantic
        constructor when working with raw API data.
    """

    @classmethod
    def model_validate(cls, data: typing.Any) -> "Base":
        """Validate and create model instance from API response data.

        This method extends Pydantic's validation to handle FCA API
        response patterns including field name normalization and
        filtering of unused fields.

        Args:
            data: Raw data from API response, typically a dictionary
                with mixed-case field names and potential "[notinuse]" markers.

        Returns:
            Validated model instance with normalized field names.

        Example:
            Validate API response data::

                api_response = {
                    "FirmName": "Test Corp",
                    "FRN": "123456",
                    "Old_Field[notinuse]": "ignored"
                }

                firm = FirmModel.model_validate(api_response)
                # Field names normalized, unused fields filtered
        """
        if isinstance(data, dict):
            updated_data = {}
            for key, value in data.items():
                if isinstance(key, str):
                    key = key.lower().strip()
                    if "[notinuse]" in key:
                        # Skip fields that are marked as not in use
                        continue
                updated_data[key] = value
            data = updated_data
        if cls.model_config and cls.model_config.get("extra"):
            # Use model-specific extra settings if defined
            return super().model_validate(data)
        else:
            return super().model_validate(data, extra=settings.model_validate_extra)


class RelaxedBase(Base):
    """Base class for API types that capture additional/unknown fields.

    This class extends the standard `Base` class to capture and store
    any fields that are not explicitly defined in the model schema.
    This is useful for:

    - **Forward compatibility**: Capturing new API fields before updating schemas
    - **Debugging**: Seeing what unexpected data the API returns
    - **Flexible processing**: Accessing both known and unknown fields
    - **API evolution**: Handling API changes gracefully

    The extra fields are stored in Pydantic's `__pydantic_extra__` and
    can be accessed via the `get_additional_fields()` method.

    Example:
        Handle API responses with unknown fields::

            class FlexibleFirmData(RelaxedBase):
                name: str
                frn: str

            # API returns extra fields not in schema
            api_data = {
                "name": "Test Firm",
                "frn": "123456",
                "new_field_v2": "future_data",
                "experimental_flag": True
            }

            firm = FlexibleFirmData.model_validate(api_data)
            print(firm.name)  # "Test Firm"
            print(firm.frn)   # "123456"

            # Access additional fields
            extra = firm.get_additional_fields()
            print(extra)  # {"new_field_v2": "future_data", "experimental_flag": True}

    Use Cases:
        - Capturing new API fields during development
        - Building flexible data processing pipelines
        - Debugging unexpected API responses
        - Future-proofing against API changes

    Warning:
        While flexible, this approach can hide schema drift and API changes.
        Use primarily for development and debugging, not production parsing.
    """

    model_config = pydantic.ConfigDict(extra="allow")

    def get_additional_fields(self) -> dict[str, typing.Any]:
        """Get all additional fields not defined in the model schema.

        Returns:
            Dictionary containing all extra fields captured during validation
            that were not part of the model's defined fields.

        Example:
            Access unexpected API fields::

                firm = FlexibleFirmData.model_validate(api_response)

                # Check for new/unknown fields
                extra_fields = firm.get_additional_fields()
                if extra_fields:
                    print(f"API returned unexpected fields: {list(extra_fields.keys())}")

                    # Log for analysis
                    logger.info("Unknown API fields", extra=extra_fields)
        """
        return dict(self.__pydantic_extra__)
