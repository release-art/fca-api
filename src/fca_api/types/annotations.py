"""Custom annotations for FCA API types."""

import enum

from pydantic.dataclasses import dataclass


@enum.unique
class FcaApiField(enum.StrEnum):
    """Custom metadata markers for FCA API fields."""

    InternalUrl = "internal_url"  # Marker for fields that contain internal URLs, which may require special handling.


@dataclass(frozen=True, slots=True)
class FcaApiFieldInfo:
    """Custom field information for FCA API types."""

    marks: frozenset[FcaApiField]
