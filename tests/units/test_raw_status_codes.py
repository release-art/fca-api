import fca_api


def test_counts():
    assert len(fca_api.raw_status_codes.ALL_KNOWN_CODES) == len(fca_api.raw_status_codes.ALL_KNOWN_CODES_DICT)
