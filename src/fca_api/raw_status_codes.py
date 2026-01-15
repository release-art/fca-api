"""A library of known raw status codes from the FCA API."""

import dataclasses
import warnings


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Code:
    value: str
    is_error: bool  # True if an exception should be raised for this code
    description: str


ALL_KNOWN_CODES: tuple[Code, ...] = (
    # Login
    Code(
        value="FSR-API-01-01-00",
        is_error=False,
        description="Request Successful",
    ),
    Code(
        value="FSR-API-01-01-11",
        is_error=True,
        description="Unauthorised",
    ),
    Code(
        value="FSR-API-01-01-21",
        is_error=True,
        description="API and Email key not found",
    ),
    # Firm Details
    Code(
        value="FSR-API-02-01-00",
        is_error=False,
        description="Request Successful",
    ),
    Code(
        value="FSR-API-02-01-11",
        is_error=True,
        description="Firm not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-01-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    # Firm Names
    Code(
        value="FSR-API-02-04-00",
        is_error=False,
        description="Ok. Found Brand Names - Request Successful",
    ),
    Code(
        value="FSR-API-02-04-11",
        is_error=True,
        description="Brand Name not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-04-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    Code(
        value="FSR-API-02-04-22",
        is_error=True,
        description="Page Not found",
    ),
    # Firm Address
    Code(
        value="FSR-API-02-02-00",
        is_error=False,
        description="Ok. Firm Address Found - Request Successful",
    ),
    Code(
        value="FSR-API-02-02-11",
        is_error=True,
        description="Address not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-02-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    # Firm Control Function
    Code(
        value="FSR-API-02-12-00",
        is_error=False,
        description="SUCCESS : Control Function Found - Request Successful",
    ),
    Code(
        value="FSR-API-02-12-11",
        is_error=True,
        description="ERROR : Control Function not Found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-12-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    Code(
        value="FSR-API-02-12-22",
        is_error=True,
        description="Page Not found",
    ),
    # Firm Individual
    Code(
        value="FSR-API-02-05-00",
        is_error=False,
        description="Ok. Firm Individuals found - Request Successful",
    ),
    Code(
        value="FSR-API-02-05-11",
        is_error=True,
        description="Individual not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-05-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    # Firm Permission
    Code(
        value="FSR-API-02-03-00",
        is_error=False,
        description="Ok. Firm permission found - Request Successful",
    ),
    Code(
        value="FSR-API-02-03-11",
        is_error=True,
        description="Permission not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-03-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    Code(
        value="FSR-API-02-03-31",
        is_error=True,
        description="Invalid parameter - Garbage value in the URL",
    ),
    # Firm Requirement
    Code(
        value="FSR-API-02-06-00",
        is_error=False,
        description="Ok. Firm Requirements found - Request Successful",
    ),
    Code(
        value="FSR-API-02-06-11",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    Code(
        value="FSR-API-02-06-21",
        is_error=True,
        description="Firm Requirements not found - When SOQL returns no record",
    ),
    # Firm Requirements Investment Types
    Code(
        value="FSR-API-02-13-00",
        is_error=False,
        description="Ok. Investment Types found - Request Successful",
    ),
    Code(
        value="FSR-API-02-13-11",
        is_error=True,
        description="Investment Types not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-13-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN or Requirement Reference is correct",
    ),
    # Firm Regulator
    Code(
        value="FSR-API-02-09-00",
        is_error=False,
        description="Ok. Firm Regulator found - Request Successful",
    ),
    Code(
        value="FSR-API-02-09-11",
        is_error=True,
        description="Regulators not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-09-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    # Firm Passport
    Code(
        value="FSR-API-02-07-00",
        is_error=False,
        description="Ok. Firm Passport found - Request Successful",
    ),
    Code(
        value="FSR-API-02-07-11",
        is_error=True,
        description="Passport not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-07-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    # Firm Passport Permission
    Code(
        value="FSR-API-02-08-00",
        is_error=False,
        description="Ok. Passport permission found - Request Successful",
    ),
    Code(
        value="FSR-API-02-08-11",
        is_error=True,
        description="Passport permission not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-08-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    # Firm Waiver
    Code(
        value="FSR-API-02-14-00",
        is_error=False,
        description="Ok. Waiver information found - Request Successful",
    ),
    Code(
        value="FSR-API-02-14-11",
        is_error=True,
        description="Waiver information not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-14-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    # Firm Exclusion
    Code(
        value="FSR-API-02-10-00",
        is_error=False,
        description="Ok. Exclusions information found - Request Successful",
    ),
    Code(
        value="FSR-API-02-10-11",
        is_error=True,
        description="Exclusions information not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-10-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    # Firm DisciplinaryHistory
    Code(
        value="FSR-API-02-11-00",
        is_error=False,
        description="Ok. Disciplinary history information found - Request Successful",
    ),
    Code(
        value="FSR-API-02-11-11",
        is_error=True,
        description="Disciplinary history information not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-02-11-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the FRN is correct",
    ),
    # Individual
    Code(
        value="FSR-API-03-01-00",
        is_error=False,
        description="Request Successful",
    ),
    Code(
        value="FSR-API-03-01-11",
        is_error=True,
        description="Individual not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-03-01-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the IRN is correct",
    ),
    # Individual CF (Individual Control Function)
    Code(
        value="FSR-API-03-02-00",
        is_error=False,
        description="Ok. Indiv CF Found - Request Successful",
    ),
    Code(
        value="FSR-API-03-02-11",
        is_error=True,
        description="Individual Control function not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-03-02-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the IRN is correct",
    ),
    # Individual Disciplinary History
    Code(
        value="FSR-API-03-03-00",
        is_error=False,
        description="Ok. Disciplinary history information found - Request Successful",
    ),
    Code(
        value="FSR-API-03-03-11",
        is_error=True,
        description="Disciplinary history information not found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-03-03-21",
        is_error=True,
        description="Bad request. Invalid Input - If we cannot confirm if the IRN is correct",
    ),
    Code(
        value="FSR-API-03-03-22",
        is_error=True,
        description="Page not found",
    ),
    # Search
    Code(
        value="FSR-API-04-01-00",
        is_error=False,
        description="Ok. Search successful - Request Successful",
    ),
    Code(
        value="FSR-API-04-01-11",
        is_error=False,
        description="No search result found - When SOQL returns no record",
    ),
    Code(
        value="FSR-API-04-01-21",
        is_error=True,
        description="Bad request. Invalid Input - Search Parameter has random string like * or '",
    ),
    # Firm Appointed Representatives
    Code(
        value="FSR-API-05-04-00",
        is_error=False,
        description="Ok. Appointed Representative Found",
    ),
    Code(
        value="FSR-API-05-04-21",
        is_error=True,
        description="Bad Request: Invalid Input",
    ),
    Code(
        value="FSR-API-05-04-11",
        is_error=True,
        description="Appointed Representative not found",
    ),
    Code(
        value="FSR-API-02-07-22",
        is_error=False,
        description="Page Not Found",
    ),
    # Get Fund details
    Code(
        value="FSR-API-05-01-00",
        is_error=False,
        description="Ok. Product Found",
    ),
    Code(
        value="FSR-API-05-01-11",
        is_error=True,
        description="Product not found",
    ),
    # Get subfund details
    Code(
        value="FSR-API-05-03-00",
        is_error=False,
        description="Ok. Sub Fund Found",
    ),
    # Product other name
    Code(
        value="FSR-API-05-02-00",
        is_error=False,
        description="Ok. Product Other Name Found",
    ),
    Code(
        value="FSR-API-05-02-11",
        is_error=True,
        description="Product Other Name not found",
    ),
    # Generic Error Messages
    Code(
        value="FSR-API-99-01-01",
        is_error=True,
        description="System Error - Any System Error - e.g NumberFormatException, NullPointerException etc.",
    ),
    Code(
        value="FSR-API-99-99-99",
        is_error=True,
        description="Exception- Any random error - Catch All",
    ),
)

ALL_KNOWN_CODES_DICT: dict[str, Code] = {code.value.lower().strip(): code for code in ALL_KNOWN_CODES}


def find_code(value: str) -> Code | None:
    """Find a known status code by its value.

    Parameters:
        value: The status code value to look for.

    Returns:
        The matching Code object, or None if not found.
    """
    if value is None:
        return None
    elif not isinstance(value, str):
        raise TypeError(f"Value must be a string. Got: {value!r}")
    out = ALL_KNOWN_CODES_DICT.get(value.lower().strip(), None)
    if out is None:
        warnings.warn(f"Unknown FCA API status code encountered: {value!r}", UserWarning, stacklevel=2)
    return out
