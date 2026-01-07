"""Caching session that performs live HTTP requests and stores responses to disk."""

from __future__ import annotations

import json
import pathlib
from typing import Any

import httpx

from financial_services_register_api.api import FinancialServicesRegisterApiSession

from . import cache_filename


class CachingFinancialServicesRegisterApiSession(FinancialServicesRegisterApiSession):
    """Session that performs live HTTP requests and caches responses to disk.

    This class extends the base session to add caching functionality.
    All HTTP requests are performed normally, but responses are also
    stored to disk for later use by the mock session.
    """

    def __init__(self, api_username: str, api_key: str, cache_dir: pathlib.Path) -> None:
        """Initialize the caching session.

        Parameters
        ----------
        api_username : str
            The API username (email used for API registration).
        api_key : str
            The API key from the developer portal.
        cache_dir : pathlib.Path
            Directory to store cached responses.
        """
        super().__init__(api_username, api_key)
        self.cache_dir = pathlib.Path(cache_dir).resolve()
        assert self.cache_dir.is_dir(), f"Cache directory does not exist: {self.cache_dir}"

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Perform GET request and cache the response.

        Parameters
        ----------
        url : str
            The request URL.
        **kwargs : Any
            Additional request parameters.

        Returns
        -------
        httpx.Response
            The HTTP response.
        """
        logged_request_headers = dict(self.headers)
        # Remove any private headers from the recorded request
        logged_request_headers |= {
            "x-auth-email": "user@example.com",
            "x-auth-key": "00617470e8144a09",
        }
        # Perform the actual HTTP request
        response = await super().get(url, **kwargs)

        # Cache the response
        cache_file = self.cache_dir / cache_filename.make("GET", url, logged_request_headers, **kwargs)
        if not cache_file.parent.exists():
            cache_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            cache_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
                "url": str(response.url),
                "request": {
                    "url": str(url),
                    "params": kwargs.get("params"),
                    "headers": logged_request_headers,
                },
            }

            with cache_file.open("w") as f:
                json.dump(cache_data, f, indent=2, sort_keys=True)

        except Exception:
            # If caching fails, continue with the response anyway
            # We don't want caching issues to break the actual functionality
            pass

        return response
