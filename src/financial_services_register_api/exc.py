__all__ = [
    "FinancialServicesRegisterApiClientError",
    "FinancialServicesRegisterApiError",
    "FinancialServicesRegisterApiRequestError",
    "FinancialServicesRegisterApiResponseError",
]


class FinancialServicesRegisterApiError(Exception):
    """Base class for all API exceptions."""


class FinancialServicesRegisterApiRequestError(FinancialServicesRegisterApiError):
    """Base class all API request exceptions."""


class FinancialServicesRegisterApiResponseError(FinancialServicesRegisterApiError):
    """Base class all API response exceptions."""


class FinancialServicesRegisterApiClientError(FinancialServicesRegisterApiError):
    """Base class for an API client exceptions."""
