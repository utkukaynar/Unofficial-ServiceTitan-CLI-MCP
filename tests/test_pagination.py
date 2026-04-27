"""Tests for pagination.py."""

from __future__ import annotations

from unittest.mock import MagicMock, call

import pytest

from st_cli.pagination import fetch_all, fetch_page


@pytest.fixture()
def mock_client():
    return MagicMock()


class TestFetchPage:
    def test_passes_page_and_size(self, mock_client):
        mock_client.get.return_value = {"data": [], "hasMore": False, "totalCount": 0}
        fetch_page(mock_client, "crm", "customers", page=2, page_size=25)
        mock_client.get.assert_called_once_with(
            "crm", "customers", params={"page": 2, "pageSize": 25}
        )

    def test_merges_extra_params(self, mock_client):
        mock_client.get.return_value = {"data": [], "hasMore": False}
        fetch_page(mock_client, "crm", "customers", params={"name": "Acme"}, page=1, page_size=50)
        expected_params = {"name": "Acme", "page": 1, "pageSize": 50}
        mock_client.get.assert_called_once_with("crm", "customers", params=expected_params)

    def test_returns_envelope(self, mock_client):
        envelope = {"data": [{"id": 1}], "hasMore": False, "totalCount": 1}
        mock_client.get.return_value = envelope
        result = fetch_page(mock_client, "crm", "customers")
        assert result == envelope


class TestFetchAll:
    def test_single_page(self, mock_client):
        mock_client.get.return_value = {
            "data": [{"id": 1}, {"id": 2}], "hasMore": False, "totalCount": 2
        }
        records = list(fetch_all(mock_client, "crm", "customers"))
        assert records == [{"id": 1}, {"id": 2}]
        assert mock_client.get.call_count == 1

    def test_multiple_pages(self, mock_client):
        mock_client.get.side_effect = [
            {"data": [{"id": 1}], "hasMore": True, "totalCount": 2},
            {"data": [{"id": 2}], "hasMore": False, "totalCount": 2},
        ]
        records = list(fetch_all(mock_client, "crm", "customers"))
        assert records == [{"id": 1}, {"id": 2}]
        assert mock_client.get.call_count == 2

    def test_empty_data(self, mock_client):
        mock_client.get.return_value = {"data": [], "hasMore": False, "totalCount": 0}
        records = list(fetch_all(mock_client, "crm", "customers"))
        assert records == []

    def test_passes_page_size(self, mock_client):
        mock_client.get.return_value = {"data": [], "hasMore": False}
        list(fetch_all(mock_client, "crm", "customers", page_size=10))
        mock_client.get.assert_called_once_with(
            "crm", "customers", params={"page": 1, "pageSize": 10}
        )
