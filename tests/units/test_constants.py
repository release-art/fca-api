from fca_api.const import ApiConstants


class TestFinancialServicesRegisterApiConstants:
    def test_fsr_api_constants(self):
        assert ApiConstants.API_VERSION.value == "V0.1"
        assert ApiConstants.BASEURL.value == "https://register.fca.org.uk/services/V0.1"
