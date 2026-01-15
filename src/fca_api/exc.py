"""Exception classes for the FCA API client.

This module defines custom exceptions used throughout the FCA API client
to provide meaningful error information and enable proper error handling.

All exceptions inherit from `FcaBaseError` to allow catching all
API-related errors with a single except clause.

Example:
    Catching all API errors::

        try:
            firm = await client.get_firm("123456")
        except fca_api.exc.FcaBaseError as e:
            print(f"API error occurred: {e}")

    Catching specific error types::

        try:
            response = await client._client.get_firm("invalid")
        except fca_api.exc.FcaRequestError as e:
            print(f"HTTP request failed: {e}")
"""


class FcaBaseError(Exception):
    """Base class for all FCA API exceptions.

    This is the root exception class for all errors originating from
    the FCA API client. Use this for catching any API-related error.

    All other exception classes in this module inherit from this base class,
    allowing for both specific and general error handling patterns.

    Example:
        Catch any API error::

            try:
                result = await client.search_frn("test")
            except FcaBaseError as e:
                logger.error(f"FCA API error: {e}")
                raise
    """


class FcaRequestError(FcaBaseError):
    """Exception for low-level HTTP request errors.

    Raised when HTTP requests to the FCA API fail due to network issues,
    authentication problems, rate limiting, server errors, or other
    HTTP-level problems.

    This exception typically wraps underlying HTTP client errors and
    provides context about the failed request.

    Example:
        Handle HTTP-specific errors::

            try:
                response = await client._client.search_frn("test", page=1)
            except FcaRequestError as e:
                if "rate limit" in str(e).lower():
                    # Wait and retry
                    await asyncio.sleep(60)
                    response = await client._client.search_frn("test", page=1)
                else:
                    raise

    Note:
        This exception is primarily raised by the raw client layer.
        The high-level client may handle some of these errors internally.
    """
