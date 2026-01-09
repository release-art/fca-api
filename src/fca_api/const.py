import dataclasses
import enum


@dataclasses.dataclass(frozen=True)
class ResourceTypeInfo:
    """A dataclass to store resource type information."""

    type_name: str
    endpoint_base: str


@enum.unique
class ResourceTypes(enum.Enum):
    """An enum to store resource type information."""

    FIRM = ResourceTypeInfo(type_name="firm", endpoint_base="Firm")
    FUND = ResourceTypeInfo(type_name="fund", endpoint_base="CIS")
    INDIVIDUAL = ResourceTypeInfo(type_name="individual", endpoint_base="Individuals")

    @classmethod
    def all_resource_types(cls) -> list[ResourceTypeInfo]:
        """Return a list of all resource type info objects."""
        return [rt.value for rt in cls]

    @classmethod
    def all_types(cls) -> list[str]:
        """Return a list of all resource type names."""
        return [rt.type_name for rt in cls.all_resource_types()]

    @classmethod
    def from_type_name(cls, type_name: str) -> ResourceTypeInfo:
        """Return the ResourceTypeInfo for the given type name, or None if not found."""
        for rt in cls:
            if rt.value.type_name == type_name:
                return rt.value
        raise ValueError(f"Unknown resource type name: {type_name}")


@enum.unique
class ApiConstants(enum.Enum):  # noqa: N801
    """An enum to store FS Register API-level constants."""

    API_VERSION = "V0.1"
    BASEURL = f"https://register.fca.org.uk/services/{API_VERSION}"
    DEVELOPER_PORTAL = "https://register.fca.org.uk/Developer/s/"
