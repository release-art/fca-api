"""High-level Financial Services Register API client.

Performs data validation and transformation on top of the raw API client.
"""
import typing
from . import raw, exc

class Client:
    """High-level Financial Services Register API client.

    This client wraps the low-level raw client to provide data validation
    and transformation for easier consumption.
    """

    def __init__(self, *, api_key: str) -> None:
        """Initialize the high-level FCA API client.

        Args:
            api_key: The API key to use for authentication.
        """
        self._raw_client = raw.RawClient(api_key=api_key)

    # Additional high-level methods would go here, utilizing self._raw_client
    # and performing necessary data validation and transformation.