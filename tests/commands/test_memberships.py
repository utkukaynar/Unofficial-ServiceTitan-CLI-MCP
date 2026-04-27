"""Tests for Memberships commands."""

from __future__ import annotations

import pytest

from tests.conftest import make_envelope


MEMBERSHIP = {"id": 1, "customerId": 10, "membershipTypeId": 5, "status": "Active", "from": "2025-01-01", "to": "2026-01-01", "createdOn": "2025-01-01"}
MEMBERSHIP_TYPE = {"id": 5, "name": "Gold Plan", "durationBillingPeriods": 12, "active": True}


class TestMembershipsList:
    def test_basic_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([MEMBERSHIP])
        result = invoke(["memberships", "list"])
        assert result.exit_code == 0

    def test_all_pages(self, invoke, mock_client):
        mock_client.get.side_effect = [
            make_envelope([MEMBERSHIP], has_more=True),
            make_envelope([MEMBERSHIP], has_more=False),
        ]
        result = invoke(["memberships", "list", "--all"])
        assert result.exit_code == 0


class TestMembershipsGet:
    def test_get(self, invoke, mock_client):
        mock_client.get.return_value = MEMBERSHIP
        result = invoke(["memberships", "get", "1"])
        assert result.exit_code == 0


class TestMembershipTypes:
    def test_types_list(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([MEMBERSHIP_TYPE])
        result = invoke(["memberships", "types-list"])
        assert result.exit_code == 0
        assert "Gold Plan" in result.output
