"""Custom field parsers for FCA API types."""

import datetime


def parse_date(date_str: str) -> datetime.datetime | None:
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
