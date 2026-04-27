"""Tests for reporting helper functions."""

from __future__ import annotations

from st_cli.commands.reporting import _report_rows_to_dicts


class TestReportRowsToDicts:
    def test_basic_conversion(self):
        fields = [
            {"name": "Name", "label": "Name", "type": "String"},
            {"name": "Revenue", "label": "Revenue", "type": "Number"},
        ]
        data = [
            ["Alice", 10000.0],
            ["Bob", 20000.0],
        ]
        result = _report_rows_to_dicts(fields, data)
        assert result == [
            {"Name": "Alice", "Revenue": 10000.0},
            {"Name": "Bob", "Revenue": 20000.0},
        ]

    def test_empty_data(self):
        fields = [{"name": "Name", "label": "Name", "type": "String"}]
        assert _report_rows_to_dicts(fields, []) == []

    def test_empty_fields(self):
        assert _report_rows_to_dicts([], []) == []

    def test_preserves_none_values(self):
        fields = [
            {"name": "Name", "label": "Name", "type": "String"},
            {"name": "Score", "label": "Score", "type": "Number"},
        ]
        data = [["Alice", None]]
        result = _report_rows_to_dicts(fields, data)
        assert result == [{"Name": "Alice", "Score": None}]
