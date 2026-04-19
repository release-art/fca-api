"""Tests for fca_api.types.base module."""

import pydantic
import pytest

from fca_api.types import base


class SampleModel(base.Base):
    name: str
    value: int = 0


class SampleRelaxed(base.RelaxedBase):
    name: str


class TestBaseModelValidate:
    def test_lowercase_normalizes_keys(self):
        result = SampleModel.model_validate({"Name": "test", "Value": 42})
        assert result.name == "test"
        assert result.value == 42

    def test_notinuse_fields_are_dropped(self):
        result = SampleModel.model_validate({"Name": "test", "Old_Field[notinuse]": "ignored"})
        assert result.name == "test"

    def test_non_dict_input_passes_through(self):
        instance = SampleModel(name="direct", value=7)
        result = SampleModel.model_validate(instance)
        assert result.name == "direct"
        assert result.value == 7

    def test_non_string_keys_in_dict_preserved(self):
        # Non-string keys bypass lowercasing but are still included in data
        # (pydantic will reject them if they don't match any field alias)
        with pytest.raises(pydantic.ValidationError):
            SampleModel.model_validate({123: "ignored", "name": "test"})

    def test_model_with_extra_config_uses_own_extra_setting(self):
        # RelaxedBase has model_config with extra="allow", so extra fields are captured
        result = SampleRelaxed.model_validate({"name": "test", "extra_field": "captured"})
        assert result.name == "test"
        assert result.get_additional_fields() == {"extra_field": "captured"}


class TestRelaxedBaseGetAdditionalFields:
    def test_returns_empty_dict_when_no_extras(self):
        result = SampleRelaxed.model_validate({"name": "test"})
        assert result.get_additional_fields() == {}

    def test_returns_all_extra_fields(self):
        result = SampleRelaxed.model_validate({"name": "test", "foo": 1, "bar": "baz"})
        assert result.get_additional_fields() == {"foo": 1, "bar": "baz"}
