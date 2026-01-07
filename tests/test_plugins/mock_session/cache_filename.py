"""Convert session request params to cache filename used in tests."""

import hashlib
import json
import logging
import pathlib
import re
import typing
from typing import Any
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)
G_CUR_TEST_PREFIX: typing.Optional[pathlib.PurePath] = None


def make(method: typing.Literal["GET", "POST"], url: str, headers: dict, **kwargs: Any) -> pathlib.PurePath:
    """Generate a cache filename based on the request parameters.

    Creates human-readable cache filenames by:
    - Using the last URL path segment as a directory name
    - Creating descriptive filenames based on request parameters
    - Adding a hash suffix for uniqueness

    Parameters
    ----------
    method : typing.Literal["GET", "POST"]
        The HTTP method.
    url : str
        The request URL.
    headers : dict
        The request headers.
    **kwargs : Any
        Additional request parameters.

    Returns
    -------
    pathlib.PurePath
        Path to the cache file with directory structure.
    """
    # Parse the URL to extract components
    parsed_url = urlparse(url)
    path_parts = [part for part in parsed_url.path.split("/") if part]

    # Use the last path segment as directory name, or 'root' if no path
    name_parts = []
    if path_parts:
        for part in reversed(path_parts):
            if not part.isdigit():
                name_parts.insert(0, part)
                if len(name_parts) >= 2:
                    break

    if not name_parts:
        name_parts.append("root")

    name_prefix = "_".join(name_parts).lower()

    # Clean directory name (remove special characters)
    name_prefix = re.sub(r"[^\w\-_]", "_", name_prefix)

    # Build human-readable filename components
    filename_parts = [name_prefix]

    # Add method
    filename_parts.append(method.lower())

    # Add query parameters if present
    query_params = parse_qs(parsed_url.query)
    if query_params:
        for key, values in sorted(query_params.items()):
            if values:
                # Clean parameter values for filename safety
                clean_value = re.sub(r"[^\w\-_]", "_", str(values[0]))[:20]  # Limit length
                filename_parts.append(f"{key}_{clean_value}")

    # Add additional params from kwargs
    request_params = kwargs.get("params", {})
    if request_params:
        for key, value in sorted(request_params.items()):
            if value:
                clean_value = re.sub(r"[^\w\-_]", "_", str(value))[:20]  # Limit length
                filename_parts.append(f"{key}_{clean_value}")

    # Create base filename
    if filename_parts:
        base_filename = "_".join(filename_parts)
    else:
        base_filename = "request"

    # Create a hash for uniqueness (shorter than before, but still unique)
    cache_key_data = {
        "url": str(url),
        "params": kwargs.get("params"),
        "headers": dict(headers)
        | {
            # Remove any headers that may vary between requests
            "user-agent": "test",
            "connection": "close",
            "accept-encoding": "gzip, deflate, br",
            "x-auth-email": "unknown",
            "x-auth-key": "unknown",
        },
        "method": method,
    }
    cache_key = json.dumps(cache_key_data, sort_keys=True)
    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()[:8]  # Use first 8 chars

    # Combine into final filename
    final_filename = f"{base_filename}_{cache_hash}.json"

    assert G_CUR_TEST_PREFIX is not None, "G_CUR_TEST_PREFIX must be set before calling make()"
    out = G_CUR_TEST_PREFIX / final_filename
    logger.info(f"Generated cache filename: {out}")
    return out
