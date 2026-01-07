# -- IMPORTS --

# -- Standard libraries --

# -- 3rd party libraries --
import pytest

# -- Internal libraries --


class TestFinancialServicesRegisterApiSession:
    @pytest.mark.asyncio
    async def test_fs_register_api_session(self, test_session, test_api_username, test_api_key):
        assert test_session.api_username == test_api_username
        assert test_session.api_key == test_api_key
        assert test_session.headers == {
            "ACCEPT": "application/json",
            "X-AUTH-EMAIL": test_api_username,
            "X-AUTH-KEY": test_api_key,
        }
