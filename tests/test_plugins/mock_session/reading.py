"""Mock session that loads responses from cached files instead of making HTTP requests."""

from __future__ import annotations

import base64
import json
import pathlib
from typing import Any

import httpx

from fca_api.api import FinancialServicesRegisterApiSession

from . import cache_filename


class MockFinancialServicesRegisterApiSession(FinancialServicesRegisterApiSession):
    """Session that loads responses from cached files instead of making HTTP requests.

    This class extends the base session to provide completely network-less testing.
    Instead of making HTTP requests, it loads previously cached responses from disk.
    """

    def __init__(self, api_username: str, api_key: str, cache_dir: pathlib.Path) -> None:
        """Initialize the mock session.

        Parameters
        ----------
        api_username : str
            The API username (email used for API registration).
        api_key : str
            The API key from the developer portal.
        cache_dir : pathlib.Path
            Directory containing cached responses.
        """
        super().__init__(api_username, api_key)
        self.cache_dir = pathlib.Path(cache_dir)

    def _get_cache_filename(self, url: str, **kwargs: Any) -> pathlib.Path:
        """Generate a cache filename based on the request parameters.

        Parameters
        ----------
        url : str
            The request URL.
        **kwargs : Any
            Additional request parameters.

        Returns
        -------
        pathlib.Path
            Path to the cache file.
        """
        # Create a unique identifier from URL and request parameters
        # This must match the logic in CachingFinancialServicesRegisterApiSession
        return self.cache_dir / cache_filename.make("GET", url, dict(self.headers), **kwargs)

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        """Load cached response instead of making HTTP request.

        Parameters
        ----------
        url : str
            The request URL.
        **kwargs : Any
            Additional request parameters.

        Returns
        -------
        httpx.Response
            The cached HTTP response.

        Raises
        ------
        FileNotFoundError
            If no cached response is found for this request.
        """
        cache_file = self._get_cache_filename(url, **kwargs)

        if not cache_file.exists():
            raise FileNotFoundError(
                f"No cached response found for request. "
                f"Cache file: {cache_file}\\n"
                f"URL: {url}\\n"
                f"Params: {kwargs.get('params', 'None')}"
            )

        # Load cached response data
        with cache_file.open("r") as f:
            cache_data = json.load(f)

        # Create a mock HTTP response
        # We need to construct the response in a way that httpx.Response accepts
        request = httpx.Request("GET", url, params=kwargs.get("params"))

        response = httpx.Response(
            status_code=cache_data["status_code"],
            headers=cache_data["headers"] | {"content-encoding": "none"},
            content=base64.b64decode(cache_data["content"]),
            request=request,
        )

        return response
