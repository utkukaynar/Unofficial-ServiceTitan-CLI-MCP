"""Tests for Settings commands (business units, job types)."""

from tests.conftest import make_envelope

BUSINESS_UNIT = {
    "id": 1,
    "name": "HVAC",
    "active": True,
    "isDefault": True,
    "address": {"street": "123 Main St", "city": "Austin", "state": "TX"},
    "phoneNumber": "512-555-0100",
}
BUSINESS_UNIT_2 = {
    "id": 2,
    "name": "Plumbing",
    "active": True,
    "isDefault": False,
    "address": {"street": "456 Oak Ave", "city": "Dallas", "state": "TX"},
    "phoneNumber": "214-555-0200",
}


class TestBusinessUnitsList:
    def test_basic_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([BUSINESS_UNIT, BUSINESS_UNIT_2])
        result = invoke(["settings", "business-units-list"])
        assert result.exit_code == 0
        assert "HVAC" in result.output
        assert "Plumbing" in result.output

    def test_filter_by_active(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([BUSINESS_UNIT])
        invoke(["settings", "business-units-list", "--active"])
        params = mock_client.get.call_args[1]["params"]
        assert params["active"] is True

    def test_all_pages(self, invoke, mock_client):
        mock_client.get.side_effect = [
            make_envelope([BUSINESS_UNIT], has_more=True),
            make_envelope([BUSINESS_UNIT_2], has_more=False),
        ]
        result = invoke(["settings", "business-units-list", "--all"])
        assert result.exit_code == 0

    def test_json_output(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([BUSINESS_UNIT])
        result = invoke(["settings", "business-units-list"], json_output=True)
        assert result.exit_code == 0

    def test_nested_address_fields(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([BUSINESS_UNIT])
        result = invoke(["settings", "business-units-list"])
        assert result.exit_code == 0
        assert "Austin" in result.output
        assert "TX" in result.output
