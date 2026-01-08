import enum
import gzip
import json
import pathlib
import typing

import httpx

from . import cache_filename


@enum.unique
class CacheMode(enum.StrEnum):
    READ = "read"
    WRITE = "write"


class CachingSession(httpx.AsyncClient):
    """A test-only session that caches responses to disk for reuse."""

    cache_dir: pathlib.Path
    cache_mode: CacheMode

    def __init__(
        self,
        headers: dict,
        cache_dir: pathlib.Path,
        cache_mode: typing.Literal["read", "write"] = "read",
    ) -> None:
        super().__init__(headers=headers)
        self.cache_dir = pathlib.Path(cache_dir)
        self.cache_mode = CacheMode(cache_mode)

    def _get_cache_filename(self, url: str, **kwargs: typing.Any) -> pathlib.Path:
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
        return self.cache_dir / cache_filename.make("GET", url, headers={}, **kwargs)

    async def get(self, url: str, **kwargs: typing.Any) -> httpx.Response:
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

        if self.cache_mode == CacheMode.READ:
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

            if json_content := cache_data["content"].get("json"):
                content_payload = json.dumps(json_content).encode("utf-8")
            else:
                raise NotImplementedError("Only JSON content is supported in the mock session.")
            response = httpx.Response(
                status_code=cache_data["status_code"],
                headers=cache_data["headers"] | {"content-encoding": "gzip"},
                content=gzip.compress(content_payload),
                request=request,
            )
        elif self.cache_mode == CacheMode.WRITE:
            if not cache_file.parent.exists():
                cache_file.parent.mkdir(parents=True, exist_ok=True)

            response = await super().get(url, **kwargs)
            cache_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": {
                    "json": response.json()  # Assume JSON content for simplicity
                },
                "url": str(response.url),
                "request": {
                    "url": str(url),
                    "params": kwargs.get("params"),
                    "headers": dict(self.headers)
                    | {
                        # Mask private headers
                        "x-auth-email": "user@example.com",
                        "x-auth-key": "00617470e8144a09",
                    },
                },
            }

            with cache_file.open("w") as f:
                json.dump(cache_data, f, indent=2, sort_keys=True)
        else:
            raise NotImplementedError(f"Unexpected cache mode for reading: {self.cache_mode}")

        return response
