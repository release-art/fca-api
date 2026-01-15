import pytest

import fca_api


def test_counts():
    assert len(fca_api.raw_status_codes.ALL_KNOWN_CODES) == len(fca_api.raw_status_codes.ALL_KNOWN_CODES_DICT)


def test_find_code_with_none():
    """Test that find_code returns None when given None."""
    result = fca_api.raw_status_codes.find_code(None)
    assert result is None


def test_find_code_with_invalid_type():
    """Test that find_code raises TypeError for non-string input."""
    with pytest.raises(TypeError) as exc_info:
        fca_api.raw_status_codes.find_code(123)
    assert "Value must be a string" in str(exc_info.value)


def test_find_code_with_unknown_status():
    """Test that find_code warns for unknown status codes."""
    with pytest.warns(UserWarning) as warning_list:
        result = fca_api.raw_status_codes.find_code("unknown_status_code")

    assert result is None
    assert len(warning_list) == 1
    assert "Unknown FCA API status code encountered" in str(warning_list[0].message)
    assert "unknown_status_code" in str(warning_list[0].message)


def test_find_code_with_valid_status():
    """Test that find_code returns valid code for known status."""
    # Test with a known status code (case insensitive)
    result = fca_api.raw_status_codes.find_code("FSR-API-01-01-00")
    assert result is not None
    assert result.value == "FSR-API-01-01-00"
