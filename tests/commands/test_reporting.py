"""Tests for Reporting commands."""

from __future__ import annotations

import json

from tests.conftest import make_envelope

CATEGORY = {"id": "performance-reports", "name": "Performance Reports"}
REPORT = {"id": "12345", "name": "Technician Performance Board"}
REPORT_META = {
    "parameters": [
        {"name": "From", "label": "From Date", "isRequired": True, "dataType": "Date"},
        {"name": "To", "label": "To Date", "isRequired": True, "dataType": "Date"},
    ],
    "fields": [
        {"name": "TechnicianName", "label": "Technician Name", "type": "String"},
        {"name": "Revenue", "label": "Revenue", "type": "Number"},
        {"name": "JobsCompleted", "label": "Jobs Completed", "type": "Number"},
        {"name": "ConversionRate", "label": "Conversion Rate", "type": "Number"},
        {"name": "AvgTicket", "label": "Avg Ticket", "type": "Number"},
    ],
}
REPORT_DATA_RESP = {
    "fields": REPORT_META["fields"],
    "data": [
        ["John Smith", 45000.0, 120, 0.72, 375.0],
        ["Jane Doe", 62000.0, 95, 0.85, 652.63],
    ],
    "page": 1,
    "pageSize": 50,
    "hasMore": False,
    "totalCount": 2,
}


class TestCategoriesList:
    def test_basic_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([CATEGORY])
        result = invoke(["reporting", "categories"])
        assert result.exit_code == 0
        assert "Performance Reports" in result.output

    def test_json_output(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([CATEGORY])
        result = invoke(["reporting", "categories"], json_output=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data[0]["name"] == "Performance Reports"


class TestReportsList:
    def test_basic_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([REPORT])
        result = invoke(["reporting", "reports", "performance-reports"])
        assert result.exit_code == 0
        assert "Technician Performance Board" in result.output


class TestReportFields:
    def test_fields_table(self, invoke, mock_client):
        mock_client.get.return_value = REPORT_META
        result = invoke(["reporting", "fields", "performance-reports", "12345"])
        assert result.exit_code == 0
        assert "From Date" in result.output
        assert "Revenue" in result.output
        assert "Conversion Rate" in result.output

    def test_fields_json(self, invoke, mock_client):
        mock_client.get.return_value = REPORT_META
        result = invoke(["reporting", "fields", "performance-reports", "12345"], json_output=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "parameters" in data
        assert "fields" in data


class TestReportData:
    def test_basic_fetch(self, invoke, mock_client):
        mock_client.post.return_value = REPORT_DATA_RESP
        result = invoke(
            [
                "reporting",
                "data",
                "performance-reports",
                "12345",
                "--from",
                "2026-03-01",
                "--to",
                "2026-03-27",
            ]
        )
        assert result.exit_code == 0
        assert "John Smith" in result.output
        assert "Jane Doe" in result.output

    def test_json_output(self, invoke, mock_client):
        mock_client.post.return_value = REPORT_DATA_RESP
        result = invoke(
            [
                "reporting",
                "data",
                "performance-reports",
                "12345",
                "--from",
                "2026-03-01",
                "--to",
                "2026-03-27",
            ],
            json_output=True,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2
        assert data[0]["TechnicianName"] == "John Smith"
        assert data[0]["Revenue"] == 45000.0
        assert data[1]["ConversionRate"] == 0.85

    def test_passes_date_params(self, invoke, mock_client):
        mock_client.post.return_value = REPORT_DATA_RESP
        invoke(
            [
                "reporting",
                "data",
                "performance-reports",
                "12345",
                "--from",
                "2026-03-01",
                "--to",
                "2026-03-27",
            ]
        )
        call_kwargs = mock_client.post.call_args[1]
        body = call_kwargs["json_body"]
        assert {"name": "From", "value": "2026-03-01"} in body["parameters"]
        assert {"name": "To", "value": "2026-03-27"} in body["parameters"]

    def test_passes_page_params(self, invoke, mock_client):
        mock_client.post.return_value = REPORT_DATA_RESP
        invoke(
            [
                "reporting",
                "data",
                "performance-reports",
                "12345",
                "--from",
                "2026-03-01",
                "--to",
                "2026-03-27",
                "--page",
                "2",
                "--page-size",
                "25",
            ]
        )
        call_kwargs = mock_client.post.call_args[1]
        assert call_kwargs["params"]["page"] == 2
        assert call_kwargs["params"]["pageSize"] == 25

    def test_all_pages(self, invoke, mock_client):
        page1 = {
            **REPORT_DATA_RESP,
            "data": [["John Smith", 45000.0, 120, 0.72, 375.0]],
            "hasMore": True,
            "totalCount": 2,
        }
        page2 = {
            **REPORT_DATA_RESP,
            "data": [["Jane Doe", 62000.0, 95, 0.85, 652.63]],
            "hasMore": False,
            "totalCount": 2,
        }
        mock_client.post.side_effect = [page1, page2]
        result = invoke(
            [
                "reporting",
                "data",
                "performance-reports",
                "12345",
                "--from",
                "2026-03-01",
                "--to",
                "2026-03-27",
                "--all",
            ]
        )
        assert result.exit_code == 0
        assert "John Smith" in result.output
        assert "Jane Doe" in result.output

    def test_extra_params(self, invoke, mock_client):
        mock_client.post.return_value = REPORT_DATA_RESP
        invoke(
            [
                "reporting",
                "data",
                "performance-reports",
                "12345",
                "--from",
                "2026-03-01",
                "--to",
                "2026-03-27",
                "--params",
                '[{"name": "BusinessUnitId", "value": "42"}]',
            ]
        )
        call_kwargs = mock_client.post.call_args[1]
        body = call_kwargs["json_body"]
        assert {"name": "BusinessUnitId", "value": "42"} in body["parameters"]
