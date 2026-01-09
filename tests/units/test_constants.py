import pytest

from fca_api.const import ApiConstants, ResourceTypes


def test_fsr_api_constants():
    assert ApiConstants.API_VERSION.value == "V0.1"
    assert ApiConstants.BASEURL.value == "https://register.fca.org.uk/services/V0.1"


class TestResourceTypes:
    def test_all_resource_types(self):
        resource_types = ResourceTypes.all_resource_types()
        assert len(resource_types) == 3
        assert any(rt.type_name == "firm" for rt in resource_types)
        assert any(rt.type_name == "fund" for rt in resource_types)
        assert any(rt.type_name == "individual" for rt in resource_types)

    def test_all_types(self):
        types = ResourceTypes.all_types()
        assert types == ["firm", "fund", "individual"]

    def test_from_type_name_valid(self):
        firm_info = ResourceTypes.from_type_name("firm")
        assert firm_info.type_name == "firm"
        assert firm_info.endpoint_base == "Firm"

        fund_info = ResourceTypes.from_type_name("fund")
        assert fund_info.type_name == "fund"
        assert fund_info.endpoint_base == "CIS"

        individual_info = ResourceTypes.from_type_name("individual")
        assert individual_info.type_name == "individual"
        assert individual_info.endpoint_base == "Individuals"

    def test_from_type_name_invalid(self):
        with pytest.raises(ValueError):
            ResourceTypes.from_type_name("unknown")
