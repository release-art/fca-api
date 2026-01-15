"""Global type settings"""

import typing

# This is a centralised way to control Pydantic model settings across the codebase.
# Release the library with 'allow' or 'ignore' to be more permissive
# Develop with 'forbid' to be notified of missed fields.
model_validate_extra: typing.Literal["allow", "ignore", "forbid"] = "ignore"
