class FcaBaseError(Exception):
    """Base class for all API exceptions."""


class FcaRequestError(FcaBaseError):
    """A low-level HTTP request error."""
