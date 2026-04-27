"""Tests for Jobs commands."""

from __future__ import annotations

import pytest

from tests.conftest import make_envelope


JOB = {"id": 1, "number": "J-001", "customerId": 10, "jobStatus": "Completed", "jobTypeName": "Repair", "total": 150.0, "createdOn": "2025-01-01"}
APPOINTMENT = {"id": 1, "jobId": 1, "status": "Scheduled", "start": "2025-01-01T09:00", "end": "2025-01-01T10:00", "arrivalWindowStart": "09:00", "arrivalWindowEnd": "10:00"}
PROJECT = {"id": 1, "number": "P-001", "name": "Big Project", "status": "Active", "customerId": 10}


class TestJobsList:
    def test_basic_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([JOB])
        result = invoke(["jobs", "list"])
        assert result.exit_code == 0
        assert "J-001" in result.output

    def test_with_status_filter(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([])
        invoke(["jobs", "list", "--status", "Completed"])
        params = mock_client.get.call_args[1]["params"]
        assert params["jobStatus"] == "Completed"

    def test_with_range(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([])
        invoke(["jobs", "list", "--range", "last-7-days"])
        params = mock_client.get.call_args[1]["params"]
        assert "createdOnOrAfter" in params
        assert "createdBefore" in params

    def test_explicit_dates_override_range(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([])
        invoke(["jobs", "list", "--range", "last-week", "--from-date", "2025-01-01"])
        params = mock_client.get.call_args[1]["params"]
        assert params["createdOnOrAfter"] == "2025-01-01"


class TestJobsGet:
    def test_get(self, invoke, mock_client):
        mock_client.get.return_value = JOB
        result = invoke(["jobs", "get", "1"])
        assert result.exit_code == 0
        assert "J-001" in result.output


class TestJobsCancel:
    def test_cancel(self, invoke, mock_client):
        mock_client.post.return_value = None
        result = invoke(["jobs", "cancel", "1"])
        assert result.exit_code == 0
        assert "cancelled" in result.output
        mock_client.post.assert_called_once_with("jpm", "jobs/1/cancel")


class TestAppointments:
    def test_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([APPOINTMENT])
        result = invoke(["jobs", "appointments-list"])
        assert result.exit_code == 0

    def test_get(self, invoke, mock_client):
        mock_client.get.return_value = APPOINTMENT
        result = invoke(["jobs", "appointments-get", "1"])
        assert result.exit_code == 0


class TestProjects:
    def test_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([PROJECT])
        result = invoke(["jobs", "projects-list"])
        assert result.exit_code == 0

    def test_get(self, invoke, mock_client):
        mock_client.get.return_value = PROJECT
        result = invoke(["jobs", "projects-get", "1"])
        assert result.exit_code == 0
