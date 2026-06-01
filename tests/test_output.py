"""Tests for output.py."""

from __future__ import annotations

import json

from st_cli.output import _resolve, render, render_single


class TestResolve:
    def test_flat_key(self):
        assert _resolve({"name": "Acme"}, "name") == "Acme"

    def test_nested_key(self):
        assert _resolve({"address": {"city": "Austin"}}, "address.city") == "Austin"

    def test_missing_key_returns_none(self):
        assert _resolve({"name": "Acme"}, "email") is None

    def test_missing_nested_returns_none(self):
        assert _resolve({"address": {}}, "address.city") is None

    def test_deeply_nested(self):
        data = {"a": {"b": {"c": "deep"}}}
        assert _resolve(data, "a.b.c") == "deep"


class TestRender:
    def test_json_output(self, capsys):
        data = [{"id": 1, "name": "Acme"}]
        columns = [("ID", "id"), ("Name", "name")]
        render(data, columns, as_json=True)
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed == data

    def test_table_output_contains_data(self, capsys):
        data = [{"id": 1, "name": "Acme"}]
        columns = [("ID", "id"), ("Name", "name")]
        render(data, columns, as_json=False, title="Test")
        captured = capsys.readouterr()
        assert "Acme" in captured.out
        assert "Test" in captured.out

    def test_total_count_shown(self, capsys):
        data = [{"id": 1}]
        columns = [("ID", "id")]
        render(data, columns, as_json=False, total_count=42)
        captured = capsys.readouterr()
        assert "42" in captured.out


class TestRenderSingle:
    def test_json_output(self, capsys):
        record = {"id": 1, "name": "Acme"}
        columns = [("ID", "id"), ("Name", "name")]
        render_single(record, columns, as_json=True)
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed == record

    def test_table_output_contains_data(self, capsys):
        record = {"id": 1, "name": "Acme"}
        columns = [("ID", "id"), ("Name", "name")]
        render_single(record, columns, as_json=False)
        captured = capsys.readouterr()
        assert "Acme" in captured.out
        assert "ID" in captured.out
