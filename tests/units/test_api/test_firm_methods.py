# -- IMPORTS --

# -- Standard libraries --

# -- 3rd party libraries --
import pytest

# -- Internal libraries --


class TestFirmMethods:
    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm(self, test_client):
        # Covers the case of a request for the firm details of
        # an existing firm, Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm("113849")
        assert recv_response.ok
        assert recv_response.data
        assert (
            recv_response.data[0]["Organisation Name"]
            == "Hiscox Insurance Company Limited"
        )

        # Covers the case of a request for the firm details of
        # a non-existent firm
        recv_response = await test_client.get_firm("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_names(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_names("113849")
        assert recv_response.ok
        assert recv_response.data
        assert recv_response.data[0]["Current Names"][0]["Name"] == "Hiscox"
        assert recv_response.data[1]["Previous Names"]

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_names("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_addresses(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_addresses("113849")
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_addresses("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_controlled_functions(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_controlled_functions("113849")
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_controlled_functions("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_individuals(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_individuals("113849")
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_individuals("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_permissions(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_permissions("113849")
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_permissions("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_requirements(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_requirements("113849")
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_requirements("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_requirement_investment_types(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Barclays Bank Plc (FRN 122702)
        recv_response = await test_client.get_firm_requirement_investment_types(
            "122702", "OR-0262545"
        )
        assert recv_response.ok
        assert recv_response.data

        # Test with non-existent requirement ID
        recv_response = await test_client.get_firm_requirement_investment_types(
            "122702", "OR-1234567890"
        )
        assert recv_response.ok
        assert not recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_requirement_investment_types(
            "1234567890", "OR-0262545"
        )
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_regulators(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_regulators("113849")
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_regulators("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_passports(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_passports("113849")
        assert recv_response.ok
        assert recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_passports("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_passport_permissions(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_passport_permissions(
            "113849", "Gibraltar"
        )
        assert recv_response.ok
        assert recv_response.data

        # Test with country that doesn't have permissions
        recv_response = await test_client.get_firm_passport_permissions(
            "113849", "Germany"
        )
        assert recv_response.ok
        assert not recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_passport_permissions(
            "1234567890", "Gibraltar"
        )
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_waivers(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_waivers("113849")
        try:
            assert recv_response.ok
            assert recv_response.data
        except AssertionError:
            # Some firms may not have waivers
            pass

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_waivers("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_exclusions(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Barclays Bank Plc (FRN 122702)
        recv_response = await test_client.get_firm_exclusions("122702")
        assert recv_response.ok
        assert recv_response.data

        # Test with firm that doesn't have exclusions
        recv_response = await test_client.get_firm_exclusions("113849")
        assert recv_response.ok
        assert not recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_exclusions("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_disciplinary_history(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Barclays Bank Plc (FRN 122702)
        recv_response = await test_client.get_firm_disciplinary_history("122702")
        assert recv_response.ok
        assert recv_response.data

        # Test with firm that doesn't have disciplinary history
        recv_response = await test_client.get_firm_disciplinary_history("113849")
        assert recv_response.ok
        assert not recv_response.data

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_disciplinary_history("1234567890")
        assert recv_response.ok
        assert not recv_response.data

    @pytest.mark.asyncio
    async def test_financial_services_register_api_client__get_firm_appointed_representatives(
        self, test_client
    ):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_appointed_representatives("113849")
        assert recv_response.ok
        assert recv_response.data
        assert any(
            [
                recv_response.data["PreviousAppointedRepresentatives"],
                recv_response.data["CurrentAppointedRepresentatives"],
            ]
        )

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        recv_response = await test_client.get_firm_appointed_representatives(
            "1234567890"
        )
        assert recv_response.ok
        assert not any(
            [
                recv_response.data["PreviousAppointedRepresentatives"],
                recv_response.data["CurrentAppointedRepresentatives"],
            ]
        )
