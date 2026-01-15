"""Constants and enumerations for the FCA API client.

This module defines constants, enums, and configuration values used
throughout the FCA API client. It provides type-safe access to:

- **Resource type information** for firms, individuals, and funds
- **API configuration** including versions and base URLs
- **Endpoint mappings** for different resource types

The enums provide both type safety and convenient access to API
configuration without hardcoding strings throughout the codebase.

Example:
    Using resource types::

        from fca_api.const import ResourceTypes

        # Get all supported resource types
        all_types = ResourceTypes.all_types()
        print(all_types)  # ['firm', 'individual', 'fund']

        # Get resource info by type name
        firm_info = ResourceTypes.from_type_name('firm')
        print(firm_info.endpoint_base)  # 'Firm'

    Using API constants::

        from fca_api.const import ApiConstants

        print(ApiConstants.API_VERSION.value)  # 'V0.1'
        print(ApiConstants.BASEURL.value)      # 'https://register.fca.org.uk/services/V0.1'
"""

import dataclasses
import enum


@dataclasses.dataclass(frozen=True)
class ResourceTypeInfo:
    """Information about a specific resource type in the FCA API.

    This dataclass stores the mapping between user-friendly type names
    and the actual API endpoint paths used by the FCA Financial Services
    Register API.

    Attributes:
        type_name: The lowercase, user-friendly name for the resource type
            (e.g., 'firm', 'individual', 'fund')
        endpoint_base: The API endpoint base path for this resource type
            (e.g., 'Firm', 'Individuals', 'CIS')

    Example:
        Creating resource type info::

            firm_info = ResourceTypeInfo(
                type_name='firm',
                endpoint_base='Firm'
            )

            # Use in URL construction
            url = f"/V0.1/{firm_info.endpoint_base}/123456"
    """

    type_name: str
    endpoint_base: str


@enum.unique
class ResourceTypes(enum.Enum):
    """Enumeration of supported resource types in the FCA API.

    This enum provides type-safe access to information about the three
    main resource types supported by the Financial Services Register API:
    firms, funds, and individuals.

    Each enum member contains a `ResourceTypeInfo` object with the
    type name and corresponding API endpoint base path.

    Attributes:
        FIRM: Information for firm resources (FRN-based)
        FUND: Information for fund/CIS resources (PRN-based)
        INDIVIDUAL: Information for individual resources (IRN-based)

    Example:
        Access resource type information::

            # Get firm resource info
            firm_info = ResourceTypes.FIRM.value
            print(firm_info.type_name)      # 'firm'
            print(firm_info.endpoint_base)  # 'Firm'

            # Use in API calls
            endpoint = f"/{firm_info.endpoint_base}/123456"
    """

    FIRM = ResourceTypeInfo(type_name="firm", endpoint_base="Firm")
    FUND = ResourceTypeInfo(type_name="fund", endpoint_base="CIS")
    INDIVIDUAL = ResourceTypeInfo(type_name="individual", endpoint_base="Individuals")

    @classmethod
    def all_resource_types(cls) -> list[ResourceTypeInfo]:
        """Return a list of all resource type info objects.

        Returns:
            A list containing `ResourceTypeInfo` objects for all supported
            resource types in the API.

        Example:
            Get all resource types::

                all_resources = ResourceTypes.all_resource_types()
                for resource in all_resources:
                    print(f"{resource.type_name} -> {resource.endpoint_base}")
        """
        return [rt.value for rt in cls]

    @classmethod
    def all_types(cls) -> list[str]:
        """Return a list of all resource type names.

        Returns:
            A list of lowercase type name strings for all supported
            resource types.

        Example:
            Get type names for validation::

                valid_types = ResourceTypes.all_types()
                user_input = "firm"
                if user_input in valid_types:
                    print("Valid resource type")
        """
        return [rt.type_name for rt in cls.all_resource_types()]

    @classmethod
    def from_type_name(cls, type_name: str) -> ResourceTypeInfo:
        """Return the ResourceTypeInfo for the given type name.

        Args:
            type_name: The lowercase resource type name to look up
                (e.g., 'firm', 'individual', 'fund').

        Returns:
            The corresponding `ResourceTypeInfo` object.

        Raises:
            ValueError: If the type name is not recognized.

        Example:
            Look up resource info by name::

                try:
                    info = ResourceTypes.from_type_name('firm')
                    print(f"Endpoint: {info.endpoint_base}")
                except ValueError:
                    print("Unknown resource type")
        """
        for rt in cls:
            if rt.value.type_name == type_name:
                return rt.value
        raise ValueError(f"Unknown resource type name: {type_name}")


@enum.unique
class ApiConstants(enum.Enum):  # noqa: N801
    """API-level constants for the FCA Financial Services Register.

    This enum contains configuration constants used throughout the client,
    including API version, base URLs, and documentation links.

    These constants should be used instead of hardcoded strings to ensure
    consistency and make version updates easier.

    Attributes:
        API_VERSION: The API version string used in URLs
        BASEURL: The complete base URL for API endpoints
        DEVELOPER_PORTAL: URL to the FCA developer documentation

    Example:
        Use constants in configuration::

            from fca_api.const import ApiConstants

            print(f"API Version: {ApiConstants.API_VERSION.value}")
            print(f"Base URL: {ApiConstants.BASEURL.value}")
            print(f"Documentation: {ApiConstants.DEVELOPER_PORTAL.value}")

            # Build API endpoint URLs
            endpoint = f"{ApiConstants.BASEURL.value}/Search"
    """

    API_VERSION = "V0.1"
    BASEURL = f"https://register.fca.org.uk/services/{API_VERSION}"
    DEVELOPER_PORTAL = "https://register.fca.org.uk/Developer/s/"
