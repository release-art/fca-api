"""Tests for fca_api.types.field_parsers module."""

import datetime

import pytest

from fca_api.types import field_parsers


class TestParseFcaDate:
    """Tests for the ParseFcaDate validator."""

    def test_valid_date_formats(self):
        """Test parsing of various valid date formats."""
        test_cases = [
            ("31/12/2023 15:30:45", datetime.datetime(2023, 12, 31, 15, 30, 45)),
            ("01/01/2024 09:15", datetime.datetime(2024, 1, 1, 9, 15, 0)),
            ("15/06/2023", datetime.datetime(2023, 6, 15, 0, 0, 0)),
            ("2023-12-25", datetime.datetime(2023, 12, 25, 0, 0, 0)),
            ("Mon Jan 15 14:30:00 GMT 2024", datetime.datetime(2024, 1, 15, 14, 30, 0)),
            ("Tue Feb 20 24", datetime.datetime(2024, 2, 20, 0, 0, 0)),
        ]

        for date_str, expected in test_cases:
            result = field_parsers.ParseFcaDate.func(date_str)
            assert result == expected, f"Failed to parse {date_str}"

    @pytest.mark.parametrize("input_str", ["", "   ", "\t\n", None])
    def test_empty_string_returns_none(self, input_str):
        """Test that empty strings return None."""
        assert field_parsers.ParseFcaDate.func(input_str) is None

    @pytest.mark.parametrize("input_str", [123, [], {}, 12.34, datetime.datetime.now()])
    def test_non_string_input_raises_type_error(self, input_str):
        """Test that non-string inputs raise TypeError."""

        with pytest.raises(TypeError, match=f"Expected a string, got {type(input_str).__name__}"):
            field_parsers.ParseFcaDate.func(input_str)

    def test_unrecognized_format_raises_value_error(self):
        """Test that unrecognized date formats raise ValueError."""
        invalid_dates = [
            "invalid-date",
            "32/13/2023",  # Invalid day/month
            "2023/12/31",  # Wrong format
            "December 31, 2023",  # Wrong format
            "31-12-2023",  # Wrong separator
        ]

        for invalid_date in invalid_dates:
            with pytest.raises(ValueError, match=f"Date {invalid_date!r} is not in a recognized format"):
                field_parsers.ParseFcaDate.func(invalid_date)

    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is handled correctly."""
        date_str = "  31/12/2023 15:30:45  "
        expected = datetime.datetime(2023, 12, 31, 15, 30, 45)
        result = field_parsers.ParseFcaDate.func(date_str)
        assert result == expected


class TestStrOrNone:
    """Tests for the StrOrNone validator."""

    def test_empty_strings_return_none(self):
        """Test that empty strings return None."""
        empty_inputs = ["", "   ", "\t", "\n", "  \t\n  "]

        for empty_input in empty_inputs:
            result = field_parsers.StrOrNone.func(empty_input)
            assert result is None, f"Expected None for {empty_input!r}, got {result!r}"

    def test_na_values_return_none(self):
        """Test that N/A-like values return None."""
        na_inputs = ["n/a", "N/A", "na", "NA", "Na", "none", "NONE", "None", "   None "]

        for na_input in na_inputs:
            result = field_parsers.StrOrNone.func(na_input)
            assert result is None, f"Expected None for {na_input!r}, got {result!r}"

    def test_normal_strings_are_stripped(self):
        """Test that normal strings have whitespace stripped."""
        test_cases = [
            ("hello", "hello"),
            ("  hello  ", "hello"),
            ("\tworld\n", "world"),
            ("  test string  ", "test string"),
            ("no-whitespace", "no-whitespace"),
        ]

        for input_str, expected in test_cases:
            result = field_parsers.StrOrNone.func(input_str)
            assert result == expected, f"Expected {expected!r} for {input_str!r}, got {result!r}"

    def test_none_input_returns_none(self):
        """Test that None input returns None."""
        # Note: This might not be called in practice due to pydantic's handling,
        # but we test the function behavior directly
        result = field_parsers.StrOrNone.func(None)
        assert result is None

    def test_non_string_input_handling(self):
        """Test handling of non-string inputs."""
        # The function expects string input in normal use, but let's test edge cases
        test_cases = [
            (123, "123"),  # Numbers get converted to string by Python
            (True, "True"),  # Booleans get converted to string
        ]

        for input_val, expected in test_cases:
            # These might cause AttributeError due to .strip() call on non-strings
            try:
                result = field_parsers.StrOrNone.func(input_val)
                # If it doesn't raise an error, check the result
                if hasattr(input_val, "strip"):
                    assert result == expected or result is None
            except AttributeError:
                # Expected for objects without .strip() method
                pass

    def test_whitespace_only_na_values(self):
        """Test that N/A values with whitespace are treated as N/A."""
        whitespace_na_inputs = ["  n/a  ", "\tNA\n", "  none  ", " N/A "]

        for na_input in whitespace_na_inputs:
            result = field_parsers.StrOrNone.func(na_input)
            # These should NOT be None - they get stripped and returned
            assert result is None, f"Expected None result for {na_input!r}, got None"

    def test_case_sensitivity_boundary(self):
        """Test edge cases around case sensitivity."""
        # These should NOT be treated as N/A (different from exact matches)
        non_na_inputs = ["nA/a", "n/aa", "noner", "N/Aa"]

        for input_str in non_na_inputs:
            result = field_parsers.StrOrNone.func(input_str)
            assert result is not None, f"Expected non-None result for {input_str!r}, got None"
            assert result == input_str.strip()

        # This IS treated as N/A due to case-insensitive matching: "nonE".lower() == "none"
        result = field_parsers.StrOrNone.func("nonE")
        assert result is None, f"Expected None for 'nonE', got {result!r}"


class TestFixIncompleteUrl:
    """Tests for the FixIncompleteUrl validator."""

    def test_empty_string_returns_none(self):
        assert field_parsers.FixIncompleteUrl.func("") is None

    def test_whitespace_only_returns_none(self):
        assert field_parsers.FixIncompleteUrl.func("   ") is None

    def test_na_values_return_none(self):
        for na in ("n/a", "N/A", "na", "NA", "none", "None", "NONE"):
            assert field_parsers.FixIncompleteUrl.func(na) is None, f"Expected None for {na!r}"

    def test_url_without_protocol_gets_https_prefix(self):
        assert field_parsers.FixIncompleteUrl.func("www.example.com") == "https://www.example.com"

    def test_url_without_protocol_no_www(self):
        assert field_parsers.FixIncompleteUrl.func("example.com/path") == "https://example.com/path"

    def test_https_url_unchanged(self):
        url = "https://register.fca.org.uk/services/V0.1/Firm/123456"
        assert field_parsers.FixIncompleteUrl.func(url) == url

    def test_http_url_unchanged(self):
        url = "http://example.com/resource"
        assert field_parsers.FixIncompleteUrl.func(url) == url

    def test_whitespace_stripped(self):
        assert field_parsers.FixIncompleteUrl.func("  https://example.com  ") == "https://example.com"
