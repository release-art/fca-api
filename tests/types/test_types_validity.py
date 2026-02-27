"""Tests for FCA API types."""

import collections
import itertools
import types
import typing

import pydantic

import fca_api


def get_all_aliases(
    field_name: str, alias: str | None, alias_group: str | pydantic.AliasPath | pydantic.AliasChoices | None
) -> set[str]:
    """Get all aliases for a field."""
    aliases = set()  # fca_api doesn't enable validate_by_name / serialize_by_name.
    if alias:
        aliases.add(alias)
    if alias_group:
        if hasattr(alias_group, "convert_to_aliases"):
            for choice in alias_group.convert_to_aliases():
                assert isinstance(choice, list)
                assert len(choice) == 1, "Not sure how to handle multiple aliases in an alias group"
                aliases.add(choice[0])
        else:
            aliases.add(alias_group)
    return aliases


def assert_no_name_clashes(target: typing.Type[pydantic.BaseModel]):
    """Test that no field in the `target` can be confused with another field."""
    field_valdation_aliases = collections.defaultdict(set)  # Field name -> set of aliases
    field_serialisation_aliases = collections.defaultdict(set)  # Field name -> set of aliases
    for field_name, field in target.model_fields.items():
        field_valdation_aliases[field_name].update(get_all_aliases(field_name, field.alias, field.validation_alias))
        field_serialisation_aliases[field_name].update(
            get_all_aliases(field_name, field.alias, field.serialization_alias)
        )

    # Now condifm that no alias appears in more than one field's aliases
    errors: list[tuple[str, str, str]] = [
        # List of (field_name_1, field_name_2, shared_alias)
        # for any alias that appears in both field_name_1 and field_name_2
    ]
    all_field_names = set(target.model_fields.keys())
    for field_name_1, field_name_2 in itertools.combinations(all_field_names, 2):
        fld_1_aliases = field_valdation_aliases[field_name_1] | field_serialisation_aliases[field_name_1]
        fld_2_aliases = field_valdation_aliases[field_name_2] | field_serialisation_aliases[field_name_2]
        for shared_alias in fld_1_aliases & fld_2_aliases:
            errors.append((field_name_1, field_name_2, shared_alias))

    # Raise an error if there are any clashes
    if errors:
        class_fqn = f"{target.__module__}.{target.__qualname__}"
        print(f"\nAlias clashes found in {class_fqn}:")  # noqa: T201
        for field_name_1, field_name_2, shared_alias in errors:
            print(f"Alias '{shared_alias}' is shared between fields '{field_name_1}' and '{field_name_2}'")  # noqa: T201
        assert False, "There are alias clashes. See print statements for details."  # noqa: B011


def find_pydantic_models(target: types.ModuleType) -> typing.Generator[typing.Type[pydantic.BaseModel], None, None]:
    """Test that there are no name clashes in the given module."""
    checked_modules = []
    module_queue = [target]
    while module_queue:
        module = module_queue.pop(0)
        if module in checked_modules:
            continue
        checked_modules.append(module)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, pydantic.BaseModel):
                yield attr
            elif isinstance(attr, types.ModuleType) and attr.__name__.startswith(target.__name__):
                module_queue.append(attr)


def test_name_clashes():
    """Test that there are no name clashes in the FCA API types."""
    # Recusrive walk through all pydantic models defined in fca_api.types and check for name clashes
    for model in find_pydantic_models(fca_api.types):
        assert_no_name_clashes(model)
