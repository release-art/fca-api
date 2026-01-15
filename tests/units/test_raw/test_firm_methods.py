import pytest

import fca_api


class TestFirmMethods:
    @pytest.mark.asyncio
    async def test_get_firm_success(self, test_client):
        # Covers the case of a request for the firm details of
        # an existing firm, Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm("113849")
        assert recv_response.is_success
        assert recv_response.data
        assert recv_response.data[0]["Organisation Name"] == "Hiscox Insurance Company Limited"

    @pytest.mark.asyncio
    async def test_get_firm_failure(self, test_client):
        # Covers the case of a request for the firm details of
        # a non-existent firm
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_names_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_names("113849")
        assert recv_response.is_success
        assert recv_response.data
        assert recv_response.data[0]["Current Names"][0]["Name"] == "Hiscox"
        assert recv_response.data[1]["Previous Names"]

    @pytest.mark.asyncio
    async def test_get_firm_names_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_names("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_addresses_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_addresses("113849")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_addresses_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_addresses("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_controlled_functions_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_controlled_functions("113849")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_controlled_functions_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_controlled_functions("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_individuals_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_individuals("113849")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_individuals_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_individuals("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_permissions_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_permissions("113849")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_permissions_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_permissions("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_requirements_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_requirements("113849")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_requirements_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_requirements("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_requirement_investment_types_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Barclays Bank Plc (FRN 122702)
        recv_response = await test_client.get_firm_requirement_investment_types("122702", "OR-0262545")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_requirement_investment_types_failure(self, test_client):
        # Test with non-existent requirement ID
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_requirement_investment_types("122702", "OR-1234567890")

        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_requirement_investment_types("1234567890", "OR-0262545")

    @pytest.mark.asyncio
    async def test_get_firm_regulators_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_regulators("113849")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_regulators_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_regulators("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_passports_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_passports("113849")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_passports_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_passports("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_passport_permissions_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_passport_permissions("113849", "Gibraltar")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_passport_permissions_failure_no_permissions(self, test_client):
        # Test with country that doesn't have permissions - this also raises an error
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_passport_permissions("113849", "Germany")

    @pytest.mark.asyncio
    async def test_get_firm_passport_permissions_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_passport_permissions("1234567890", "Gibraltar")

    @pytest.mark.asyncio
    async def test_get_firm_waivers_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_waivers("113849")
        assert recv_response.is_success
        # Some firms may not have waivers, so we just check success

    @pytest.mark.asyncio
    async def test_get_firm_waivers_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_waivers("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_exclusions_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Barclays Bank Plc (FRN 122702)
        recv_response = await test_client.get_firm_exclusions("122702")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_exclusions_failure_no_exclusions(self, test_client):
        # Test with firm that doesn't have exclusions - this also raises an error
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_exclusions("113849")

    @pytest.mark.asyncio
    async def test_get_firm_exclusions_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_exclusions("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_disciplinary_history_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Barclays Bank Plc (FRN 122702)
        recv_response = await test_client.get_firm_disciplinary_history("122702")
        assert recv_response.is_success
        assert recv_response.data

    @pytest.mark.asyncio
    async def test_get_firm_disciplinary_history_failure_no_history(self, test_client):
        # Test with firm that doesn't have disciplinary history - this also raises an error
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_disciplinary_history("113849")

    @pytest.mark.asyncio
    async def test_get_firm_disciplinary_history_failure(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890
        with pytest.raises(fca_api.exc.FcaRequestError):
            await test_client.get_firm_disciplinary_history("1234567890")

    @pytest.mark.asyncio
    async def test_get_firm_appointed_representatives_success(self, test_client):
        # Covers the case of a request for an existing firm which is
        # Hiscox Insurance Company Limited (FRN 113849)
        recv_response = await test_client.get_firm_appointed_representatives("113849")
        assert recv_response.is_success
        assert recv_response.data
        assert any(
            [
                recv_response.data["PreviousAppointedRepresentatives"],
                recv_response.data["CurrentAppointedRepresentatives"],
            ]
        )

    @pytest.mark.asyncio
    async def test_get_firm_appointed_representatives_empty_result(self, test_client):
        # Covers the case of a request for an non-existent firm given by
        # a non-existent FRN 1234567890 - returns empty but doesn't fail
        recv_response = await test_client.get_firm_appointed_representatives("1234567890")
        assert recv_response.is_success
        assert not any(
            [
                recv_response.data["PreviousAppointedRepresentatives"],
                recv_response.data["CurrentAppointedRepresentatives"],
            ]
        )

    @pytest.mark.asyncio
    async def test_get_firm_names_with_page_parameter(self, test_client, mock_http_client):
        """Test get_firm_names with page parameter to cover pagination code path in _get_resource_info."""
        test_client._api_session = mock_http_client
        mock_http_client.get.return_value.status_code = 200
        mock_http_client.get.return_value.is_success = True
        mock_http_client.get.return_value.reason_phrase = "OK"
        mock_http_client.get.return_value.json.return_value = {
            "Status": "FSR-API-02-04-00",
            "Message": "Ok. Found Brand Names - Request Successful",
            "Data": [{"Current Names": [{"Name": "Test Firm"}]}],
        }

        # Call with page parameter to trigger pagination code path
        result = await test_client.get_firm_names("123456", page=2)
        assert result.is_success
        assert result.data

        # Verify the mock was called with correct URL including page parameter
        mock_http_client.get.assert_called_once()
        call_args = mock_http_client.get.call_args[0]
        assert "pgnp=2" in call_args[0]  # Check that page parameter was included

    @pytest.mark.asyncio
    async def test_get_firm_addresses_with_page_parameter(self, test_client, mock_http_client):
        """Test get_firm_addresses with page parameter to cover pagination code path in _get_resource_info."""
        test_client._api_session = mock_http_client
        mock_http_client.get.return_value.status_code = 200
        mock_http_client.get.return_value.is_success = True
        mock_http_client.get.return_value.reason_phrase = "OK"
        mock_http_client.get.return_value.json.return_value = {
            "Status": "FSR-API-02-02-00",
            "Message": "Ok. Firm Address Found - Request Successful",
            "Data": [{"Address": "Test Address"}],
        }

        # Call with page parameter to trigger pagination code path
        result = await test_client.get_firm_addresses("123456", page=1)
        assert result.is_success
        assert result.data

        # Verify the mock was called with correct URL including page parameter
        mock_http_client.get.assert_called_once()
        call_args = mock_http_client.get.call_args[0]
        assert "pgnp=1" in call_args[0]  # Check that page parameter was included

    @pytest.mark.asyncio
    async def test_get_firm_individuals_with_page_parameter(self, test_client, mock_http_client):
        """Test get_firm_individuals with page parameter to cover pagination code path in _get_resource_info."""
        test_client._api_session = mock_http_client
        mock_http_client.get.return_value.status_code = 200
        mock_http_client.get.return_value.is_success = True
        mock_http_client.get.return_value.reason_phrase = "OK"
        mock_http_client.get.return_value.json.return_value = {
            "Status": "FSR-API-02-05-00",
            "Message": "Ok. Firm Individuals found - Request Successful",
            "Data": [{"Name": "Test Individual"}],
        }

        # Call with page parameter to trigger pagination code path
        result = await test_client.get_firm_individuals("123456", page=3)
        assert result.is_success
        assert result.data

        # Verify the mock was called with correct URL including page parameter
        mock_http_client.get.assert_called_once()
        call_args = mock_http_client.get.call_args[0]
        assert "pgnp=3" in call_args[0]  # Check that page parameter was included

    @pytest.mark.asyncio
    async def test_get_firm_names_with_fca_error_status_code(self, test_client, mock_http_client):
        """Test get_firm_names with known FCA error status code to cover error handling path in _get_resource_info."""
        test_client._api_session = mock_http_client
        mock_http_client.get.return_value.status_code = 200
        mock_http_client.get.return_value.is_success = True
        mock_http_client.get.return_value.reason_phrase = "OK"
        mock_http_client.get.return_value.json.return_value = {
            "Status": "FSR-API-02-04-11",  # Known error status code: Brand Name not found
            "Message": "Brand Name not found - When SOQL returns no record",
            "Data": None,
        }

        # This should raise an exception due to the error status code
        with pytest.raises(fca_api.exc.FcaRequestError, match="API search request failed with FCA API status code"):
            await test_client.get_firm_names("999999")

    @pytest.mark.asyncio
    async def test_get_firm_names_with_http_error(self, test_client, mock_http_client):
        """Test get_firm_names with HTTP error to cover HTTP error handling path in _get_resource_info."""
        test_client._api_session = mock_http_client
        mock_http_client.get.return_value.status_code = 500
        mock_http_client.get.return_value.is_success = False  # This triggers the missing line 417
        mock_http_client.get.return_value.reason_phrase = "Internal Server Error"
        mock_http_client.get.return_value.json.return_value = {
            "Status": "ERROR",
            "Message": "Internal server error",
            "Data": None,
        }

        # This should raise an exception due to HTTP failure
        with pytest.raises(fca_api.exc.FcaRequestError, match="API search request failed with status code 500"):
            await test_client.get_firm_names("123456")
