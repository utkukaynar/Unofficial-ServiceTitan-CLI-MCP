"""Tests for Dispatch commands."""

from __future__ import annotations

import pytest

from st_cli.availability import _build_busy_summary
from st_cli.exceptions import DateParseError
from tests.conftest import make_envelope

SHIFT = {
    "id": 1,
    "technicianId": 100,
    "technicianName": "John Doe",
    "start": "2025-01-15T08:00:00",
    "end": "2025-01-15T17:00:00",
    "active": True,
}
SHIFT_JANE = {
    "id": 2,
    "technicianId": 200,
    "technicianName": "Jane Smith",
    "start": "2025-01-15T08:00:00",
    "end": "2025-01-15T17:00:00",
    "active": True,
}
APPOINTMENT = {
    "id": 10,
    "technicianId": 100,
    "jobId": 50,
    "status": "Scheduled",
    "start": "2025-01-15T09:00:00",
    "end": "2025-01-15T11:00:00",
}
ASSIGNMENT = {
    "id": 1,
    "technicianId": 100,
    "technicianName": "John Doe",
    "appointmentId": 10,
    "jobId": 50,
    "status": "Dispatched",
    "assignedOn": "2025-01-14",
}
EVENT = {
    "id": 1,
    "name": "Training",
    "start": "2025-01-15T09:00:00",
    "end": "2025-01-15T10:00:00",
    "technicianId": 100,
}


class TestShiftsList:
    def test_basic_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([SHIFT])
        result = invoke(["dispatch", "shifts-list"])
        assert result.exit_code == 0
        assert "John Doe" in result.output

    def test_with_range(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([])
        invoke(["dispatch", "shifts-list", "--range", "this-week"])
        params = mock_client.get.call_args[1]["params"]
        assert "startsOnOrAfter" in params
        assert "startsBefore" in params

    def test_all_pages(self, invoke, mock_client):
        mock_client.get.side_effect = [
            make_envelope([SHIFT], has_more=True),
            make_envelope([SHIFT_JANE], has_more=False),
        ]
        result = invoke(["dispatch", "shifts-list", "--all"])
        assert result.exit_code == 0


class TestAssignmentsList:
    def test_basic_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([ASSIGNMENT])
        result = invoke(["dispatch", "assignments-list"])
        assert result.exit_code == 0
        assert "John Doe" in result.output

    def test_filter_by_technician(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([ASSIGNMENT])
        invoke(["dispatch", "assignments-list", "--technician-id", "100"])
        params = mock_client.get.call_args[1]["params"]
        assert params["technicianId"] == 100


class TestBuildBusySummary:
    """Unit tests for the cross-referencing logic."""

    def test_single_tech_with_appointment(self):
        rows = _build_busy_summary([SHIFT], [APPOINTMENT])
        assert len(rows) == 1
        row = rows[0]
        assert row["technicianId"] == 100
        assert row["technicianName"] == "John Doe"
        assert row["shiftHours"] == 9.0  # 08:00-17:00
        assert row["bookedHours"] == 2.0  # 09:00-11:00
        assert row["availableHours"] == 7.0
        assert row["appointments"] == 1
        assert row["percentBooked"] == pytest.approx(22.2, abs=0.1)

    def test_tech_with_no_appointments(self):
        rows = _build_busy_summary([SHIFT_JANE], [])
        assert len(rows) == 1
        row = rows[0]
        assert row["technicianId"] == 200
        assert row["bookedHours"] == 0.0
        assert row["availableHours"] == 9.0
        assert row["percentBooked"] == 0.0

    def test_multiple_techs_sorted_by_id(self):
        rows = _build_busy_summary([SHIFT_JANE, SHIFT], [APPOINTMENT])
        assert len(rows) == 2
        assert rows[0]["technicianId"] == 100
        assert rows[1]["technicianId"] == 200

    def test_no_shifts_returns_empty(self):
        rows = _build_busy_summary([], [APPOINTMENT])
        assert rows == []

    def test_multiple_appointments_same_tech(self):
        appt2 = {
            **APPOINTMENT,
            "id": 11,
            "start": "2025-01-15T13:00:00",
            "end": "2025-01-15T15:00:00",
        }
        rows = _build_busy_summary([SHIFT], [APPOINTMENT, appt2])
        row = rows[0]
        assert row["appointments"] == 2
        assert row["bookedHours"] == 4.0  # 2 + 2
        assert row["availableHours"] == 5.0


class TestWhoBusy:
    def test_with_shifts_and_appointments(self, invoke, mock_client):
        # who-busy calls fetch_all twice: shifts then appointments
        # Each fetch_all calls client.get repeatedly until hasMore=False
        mock_client.get.side_effect = [
            make_envelope([SHIFT, SHIFT_JANE]),  # shifts page 1
            make_envelope([APPOINTMENT]),  # appointments page 1
        ]
        result = invoke(["dispatch", "who-busy", "--range", "today"])
        assert result.exit_code == 0
        assert "100" in result.output  # tech ID for John
        assert "200" in result.output  # tech ID for Jane

    def test_no_shifts_shows_message(self, invoke, mock_client):
        mock_client.get.side_effect = [
            make_envelope([]),  # no shifts
            make_envelope([]),  # no appointments
        ]
        result = invoke(["dispatch", "who-busy"])
        assert result.exit_code == 0
        assert "No technician shifts found" in result.output

    def test_json_output(self, invoke, mock_client):
        mock_client.get.side_effect = [
            make_envelope([SHIFT]),
            make_envelope([APPOINTMENT]),
        ]
        result = invoke(["dispatch", "who-busy"], json_output=True)
        assert result.exit_code == 0


class TestEvents:
    def test_events_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([EVENT])
        result = invoke(["dispatch", "events-list"])
        assert result.exit_code == 0

    def test_events_create(self, invoke, mock_client):
        mock_client.post.return_value = EVENT
        result = invoke(["dispatch", "events-create", "--data", '{"name": "Training"}'])
        assert result.exit_code == 0


# --- Zones ---

ZONE = {"id": 1, "name": "North Zone", "active": True}
ZONE2 = {"id": 2, "name": "South Zone", "active": True}


class TestZonesList:
    def test_basic_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([ZONE, ZONE2])
        result = invoke(["dispatch", "zones-list"])
        assert result.exit_code == 0
        assert "North Zone" in result.output

    def test_filter_by_active(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([ZONE])
        invoke(["dispatch", "zones-list", "--active"])
        params = mock_client.get.call_args[1]["params"]
        assert params["active"] is True

    def test_all_pages(self, invoke, mock_client):
        mock_client.get.side_effect = [
            make_envelope([ZONE], has_more=True),
            make_envelope([ZONE2], has_more=False),
        ]
        result = invoke(["dispatch", "zones-list", "--all"])
        assert result.exit_code == 0

    def test_json_output(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([ZONE])
        result = invoke(["dispatch", "zones-list"], json_output=True)
        assert result.exit_code == 0


# --- Teams ---

TEAM = {"id": 10, "name": "Install Team", "active": True}
TEAM2 = {"id": 20, "name": "Repair Team", "active": True}


class TestTeamsList:
    def test_basic_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([TEAM, TEAM2])
        result = invoke(["dispatch", "teams-list"])
        assert result.exit_code == 0
        assert "Install Team" in result.output

    def test_filter_by_active(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([TEAM])
        invoke(["dispatch", "teams-list", "--active"])
        params = mock_client.get.call_args[1]["params"]
        assert params["active"] is True

    def test_all_pages(self, invoke, mock_client):
        mock_client.get.side_effect = [
            make_envelope([TEAM], has_more=True),
            make_envelope([TEAM2], has_more=False),
        ]
        result = invoke(["dispatch", "teams-list", "--all"])
        assert result.exit_code == 0


# --- Capacity ---

CAPACITY_AVAILABILITY = {
    "start": "2025-01-15T08:00:00",
    "end": "2025-01-15T10:00:00",
    "startUtc": "2025-01-15T13:00:00Z",
    "endUtc": "2025-01-15T15:00:00Z",
    "businessUnitIds": [1],
    "totalAvailability": 8.0,
    "openAvailability": 6.0,
    "technicians": [{"id": 100, "name": "John Doe", "status": "Available"}],
    "isAvailable": True,
    "isExceedingIdealBookingPercentage": False,
}
CAPACITY_RESPONSE = {
    "timeStamp": "2025-01-15T07:00:00Z",
    "availabilities": [CAPACITY_AVAILABILITY],
}


class TestCapacity:
    def test_basic_query(self, invoke, mock_client):
        mock_client.post.return_value = CAPACITY_RESPONSE
        result = invoke(["dispatch", "capacity", "--range", "this-week"])
        assert result.exit_code == 0
        assert "Capacity" in result.output

    def test_body_has_required_fields(self, invoke, mock_client):
        mock_client.post.return_value = CAPACITY_RESPONSE
        invoke(["dispatch", "capacity", "--range", "today"])
        body = mock_client.post.call_args[1]["json_body"]
        assert "startsOnOrAfter" in body
        assert "endsOnOrBefore" in body
        assert body["skillBasedAvailability"] is False
        # No args wrapper, no businessUnitIds/jobTypeId when not requested
        assert "args" not in body
        assert "businessUnitIds" not in body
        assert "jobTypeId" not in body

    def test_with_business_units(self, invoke, mock_client):
        mock_client.post.return_value = CAPACITY_RESPONSE
        invoke(["dispatch", "capacity", "--range", "today", "--bu-ids", "1,2"])
        body = mock_client.post.call_args[1]["json_body"]
        assert body["businessUnitIds"] == [1, 2]
        assert "jobTypeId" not in body

    def test_with_job_type_id(self, invoke, mock_client):
        mock_client.post.return_value = CAPACITY_RESPONSE
        invoke(["dispatch", "capacity", "--range", "today", "--job-type-id", "10"])
        body = mock_client.post.call_args[1]["json_body"]
        assert body["jobTypeId"] == 10
        assert "businessUnitIds" not in body

    def test_with_bu_and_job_type(self, invoke, mock_client):
        mock_client.post.return_value = CAPACITY_RESPONSE
        invoke(
            [
                "dispatch",
                "capacity",
                "--range",
                "today",
                "--bu-ids",
                "1,2",
                "--job-type-id",
                "10",
            ]
        )
        body = mock_client.post.call_args[1]["json_body"]
        assert body["businessUnitIds"] == [1, 2]
        assert body["jobTypeId"] == 10

    def test_skill_based_flag(self, invoke, mock_client):
        mock_client.post.return_value = {"timeStamp": "x", "availabilities": []}
        invoke(["dispatch", "capacity", "--range", "today", "--skill-based"])
        body = mock_client.post.call_args[1]["json_body"]
        assert body["skillBasedAvailability"] is True

    def test_14_day_limit_exceeded(self, invoke, mock_client):
        with pytest.raises(DateParseError, match="19 days.*maximum is 14"):
            invoke(
                [
                    "dispatch",
                    "capacity",
                    "--from-date",
                    "2025-01-01",
                    "--to-date",
                    "2025-01-20",
                ]
            )

    def test_empty_availabilities(self, invoke, mock_client):
        mock_client.post.return_value = {"timeStamp": "x", "availabilities": []}
        result = invoke(["dispatch", "capacity", "--range", "today"])
        assert result.exit_code == 0
        assert "No availability returned" in result.output

    def test_json_output(self, invoke, mock_client):
        mock_client.post.return_value = CAPACITY_RESPONSE
        result = invoke(["dispatch", "capacity", "--range", "today"], json_output=True)
        assert result.exit_code == 0
