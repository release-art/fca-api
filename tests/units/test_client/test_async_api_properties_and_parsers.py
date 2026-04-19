"""Unit tests for Client properties and internal parse methods."""

import unittest.mock

import pydantic
import pytest

import fca_api.async_api


@pytest.fixture
def client():
    mock_raw = unittest.mock.MagicMock()
    mock_raw.api_version = "V0.1"
    orig = fca_api.async_api.raw_api.RawClient
    fca_api.async_api.raw_api.RawClient = lambda *a, **kw: mock_raw
    c = fca_api.async_api.Client(credentials=("test@test.com", "test-key"))
    yield c
    fca_api.async_api.raw_api.RawClient = orig


class TestClientProperties:
    def test_raw_client(self, client):
        assert client.raw_client is client._client

    def test_api_version(self, client):
        assert client.api_version == "V0.1"


class TestParseFirmNamesPg:
    def test_non_dict_element_skipped_with_warning(self, client, caplog):
        result = client._parse_firm_names_pg(["not-a-dict"])
        assert result == []
        assert "Unexpected firm name entry format" in caplog.text

    def test_unexpected_key_warns(self, client, caplog):
        result = client._parse_firm_names_pg([{"Unknown Key": "value"}])
        assert result == []
        assert "Unexpected firm name entry field" in caplog.text


class TestParseFirmAddressesPg:
    def test_non_string_key_skipped(self, client):
        # Non-string keys are skipped during address-line extraction but pydantic
        # still rejects them at model_validate time (keys must be strings).
        data = [
            {
                123: "non-string-key-value",
                "Address Line 1": "Main St",
                "address type": "principal place of business",
                "phone number": "+441234567890",
                "town": "London",
                "postcode": "EC1A 1BB",
                "county": "",
                "country": "United Kingdom",
                "website address": None,
                "url": "https://register.fca.org.uk/services/V0.1/Firm/123456/Address?Type=PPOB",
            }
        ]
        with pytest.raises(pydantic.ValidationError, match="Keys should be strings"):
            client._parse_firm_addresses_pg(data)


class TestParseFirmControlledFunctionsPg:
    def test_non_dict_data_row_skipped_with_warning(self, client, caplog):
        result = client._parse_firm_controlled_functions_pg(["not-a-dict"])
        assert result == []
        assert "Unexpected firm controlled function entry format" in caplog.text

    def test_non_dict_value_skipped_with_warning(self, client, caplog):
        result = client._parse_firm_controlled_functions_pg([{"Current": "not-a-dict"}])
        assert result == []
        assert "Unexpected firm controlled function entry value format" in caplog.text

    def test_subkey_name_mismatch_warns(self, client, caplog):
        # Using lowercase "name" so subvalue.get("name") returns "Different Name",
        # causing subkey_el ("actualkey") != subval_name_el ("different name").
        fn_data = {
            "name": "Different Name",
            "effective date": "01/01/2023",
            "end date": None,
            "individual name": "Test Person",
            "Restriction": None,
            "suspension / restriction end date": None,
            "suspension / restriction start date": None,
            "url": "https://register.fca.org.uk/services/V0.1/Individuals/TST001",
        }
        result = client._parse_firm_controlled_functions_pg([{"Current": {"ActualKey": fn_data}}])
        assert "Mismatch in controlled function subkey and name" in caplog.text
        assert len(result) == 1


class TestParseFirmPermissionsPg:
    def test_non_list_perm_data_skipped_with_warning(self, client, caplog):
        result = client._parse_firm_permissions_pg({"Perm1": "not-a-list"})
        assert result == []
        assert "Unexpected firm permission entry format" in caplog.text

    def test_non_dict_perm_data_el_skipped_with_warning(self, client, caplog):
        result = client._parse_firm_permissions_pg({"Perm1": ["not-a-dict"]})
        assert len(result) == 1
        assert "Unexpected firm permission data element format" in caplog.text


class TestParseFirmPassportsPg:
    def test_non_dict_element_skipped_with_warning(self, client, caplog):
        result = client._parse_firm_passports_pg(["not-a-dict"])
        assert result == []
        assert "Unexpected firm passport entry format" in caplog.text

    def test_unexpected_key_warns(self, client, caplog):
        result = client._parse_firm_passports_pg([{"unknown_key": "value"}])
        assert result == []
        assert "Unexpected firm passport entry field" in caplog.text


class TestParseIndividualControlledFunctionsPg:
    def test_non_dict_row_skipped_with_warning(self, client, caplog):
        result = client._parse_individual_controlled_functions_pg(["not-a-dict"])
        assert result == []
        assert "Unexpected individual controlled function entry format" in caplog.text

    def test_non_dict_value_skipped_with_warning(self, client, caplog):
        result = client._parse_individual_controlled_functions_pg([{"current": "not-a-dict"}])
        assert result == []
        assert "Unexpected individual controlled function entry value format" in caplog.text

    def test_fn_name_mismatch_warns(self, client, caplog):
        fn_data = {
            "Name": "Different Name",
            "effective date": "01/01/2023",
            "end date": None,
            "firm name": "Test Firm",
            "restriction": None,
            "suspension / restriction start date": None,
            "suspension / restriction end date": None,
            "customer engagement method": "",
            "url": "https://register.fca.org.uk/services/V0.1/Individuals/TST001",
        }
        result = client._parse_individual_controlled_functions_pg([{"current": {"ActualFunctionName": fn_data}}])
        assert "Mismatch in controlled function name and data name" in caplog.text
        assert len(result) == 1

    def test_fn_name_matches_name_field_no_warning(self, client, caplog):
        # fn_name ("CF28 Client Dealing") == fn_data.get("Name") → no warning logged
        fn_name = "CF28 Client Dealing"
        fn_data = {
            "Name": fn_name,
            "effective date": "01/01/2023",
            "end date": None,
            "firm name": "Test Firm",
            "restriction": None,
            "suspension / restriction start date": None,
            "suspension / restriction end date": None,
            "customer engagement method": "",
            "url": "https://register.fca.org.uk/services/V0.1/Individuals/TST001",
        }
        result = client._parse_individual_controlled_functions_pg([{"current": {fn_name: fn_data}}])
        assert "Mismatch in controlled function name and data name" not in caplog.text
        assert len(result) == 1
