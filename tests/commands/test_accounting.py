"""Tests for Accounting commands."""

from __future__ import annotations

import pytest

from tests.conftest import make_envelope


INVOICE = {"id": 1, "number": "INV-001", "jobId": 10, "customerId": 20, "status": "Posted", "total": 500.0, "createdOn": "2025-01-01"}
ESTIMATE = {"id": 1, "number": "EST-001", "jobId": 10, "status": "Open", "total": 300.0, "createdOn": "2025-01-01"}
PAYMENT = {"id": 1, "invoiceId": 1, "type": "Check", "amount": 500.0, "date": "2025-01-15"}


class TestInvoicesList:
    def test_basic_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([INVOICE])
        result = invoke(["accounting", "invoices-list"])
        assert result.exit_code == 0
        assert "INV-001" in result.output

    def test_with_status_filter(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([])
        invoke(["accounting", "invoices-list", "--status", "Posted"])
        params = mock_client.get.call_args[1]["params"]
        assert params["status"] == "Posted"

    def test_with_range(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([])
        invoke(["accounting", "invoices-list", "--range", "this-month"])
        params = mock_client.get.call_args[1]["params"]
        assert "createdOnOrAfter" in params


class TestInvoicesGet:
    def test_get(self, invoke, mock_client):
        mock_client.get.return_value = INVOICE
        result = invoke(["accounting", "invoices-get", "1"])
        assert result.exit_code == 0
        assert "INV-001" in result.output


class TestEstimates:
    def test_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([ESTIMATE])
        result = invoke(["accounting", "estimates-list"])
        assert result.exit_code == 0

    def test_with_status_filter(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([])
        invoke(["accounting", "estimates-list", "--status", "Open"])
        params = mock_client.get.call_args[1]["params"]
        assert params["status"] == "Open"

    def test_with_range(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([])
        invoke(["accounting", "estimates-list", "--range", "this-month"])
        params = mock_client.get.call_args[1]["params"]
        assert "createdOnOrAfter" in params

    def test_all_pages(self, invoke, mock_client):
        mock_client.get.side_effect = [
            make_envelope([ESTIMATE], has_more=True),
            make_envelope([{**ESTIMATE, "id": 2}], has_more=False),
        ]
        result = invoke(["accounting", "estimates-list", "--all"])
        assert result.exit_code == 0

    def test_get(self, invoke, mock_client):
        mock_client.get.return_value = ESTIMATE
        result = invoke(["accounting", "estimates-get", "1"])
        assert result.exit_code == 0


class TestPayments:
    def test_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([PAYMENT])
        result = invoke(["accounting", "payments-list"])
        assert result.exit_code == 0

    def test_with_range(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([])
        invoke(["accounting", "payments-list", "--range", "last-30-days"])
        params = mock_client.get.call_args[1]["params"]
        assert "createdOnOrAfter" in params

    def test_all_pages(self, invoke, mock_client):
        mock_client.get.side_effect = [
            make_envelope([PAYMENT], has_more=True),
            make_envelope([{**PAYMENT, "id": 2}], has_more=False),
        ]
        result = invoke(["accounting", "payments-list", "--all"])
        assert result.exit_code == 0
