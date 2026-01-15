"""Custom field parsers for FCA API types."""

import datetime

import pydantic


@pydantic.BeforeValidator
def ParseFcaDate(date_str: str) -> datetime.datetime | None:
    """Parse FCA date strings into datetime objects."""
    if not isinstance(date_str, str):
        raise TypeError(f"Expected a string, got {type(date_str).__name__}")
    date_str = date_str.strip()
    if not date_str:
        return None
    for dt_format in (
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%a %b %d %H:%M:%S %Z %Y",  # Found in FCA docs
        "%a %b %d %y",
    ):
        try:
            return datetime.datetime.strptime(date_str, dt_format)
        except ValueError:
            continue
    raise ValueError(f"Date {date_str!r} is not in a recognized format")


@pydantic.BeforeValidator
def StrOrNone(value: str) -> str | None:
    """Convert empty strings to None, otherwise strip whitespace."""
    if not value or not value.strip():
        return None
    if value.lower() in {"n/a", "na", "none"}:
        return None
    return value.strip()
