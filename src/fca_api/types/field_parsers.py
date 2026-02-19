"""Custom field parsers and field types for FCA API models."""

import datetime

import pydantic


@pydantic.BeforeValidator
def ParseFcaDate(date_str: str | None) -> datetime.datetime | None:
    """Parse FCA date strings into ``datetime`` objects.

    The FCA API returns dates in a variety of formats. This helper tries
    several known patterns and returns a naive ``datetime`` instance on
    success. Blank strings are treated as missing values and mapped to
    ``None``.

    Raises:
        TypeError: If the input is not a string.
        ValueError: If the value cannot be parsed using any known format.
    """
    if date_str is None:
        return None
    elif not isinstance(date_str, str):
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
    """Normalise optional string fields from the FCA API.

    Empty strings, whitespace-only values and common "not available" markers
    such as ``"n/a"``, ``"na"`` and ``"none"`` are converted to ``None``.
    All other non-empty values are stripped of leading and trailing
    whitespace.
    """
    if not value or not value.strip():
        return None
    if value.strip().lower() in {"n/a", "na", "none"}:
        return None
    return value.strip()


@pydantic.BeforeValidator
def FixIncompleteUrl(value: str) -> str | None:
    """Fix incomplete URLs from FCA API.

    The FCA API sometimes returns URLs without protocol prefix
    (e.g., 'www.example.com' instead of 'https://www.example.com').
    This validator adds 'https://' prefix when missing.

    Empty strings and common "not available" markers are converted to None.
    """
    if not value or not value.strip():
        return None
    value = value.strip()
    if value.lower() in {"n/a", "na", "none"}:
        return None
    # Add https:// if no protocol specified
    if "://" not in value:
        return f"https://{value}"
    else:
        assert value.startswith(("http://", "https://")), "URL must start with http:// or https://"
    return value
