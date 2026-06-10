"""Tests for dates.py."""

from datetime import date, timedelta
from unittest.mock import patch

import pytest

from st_cli.dates import apply_date_params, parse_date_range, validate_max_range
from st_cli.exceptions import DateParseError

# Pin all tests to a known date: Wednesday 2025-06-18
FIXED_DATE = date(2025, 6, 18)


@pytest.fixture(autouse=True)
def freeze_today():
    """Freeze date.today() to FIXED_DATE for all tests unless overridden."""
    with patch("st_cli.dates.date") as mock_date:
        mock_date.today.return_value = FIXED_DATE
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        mock_date.fromisoformat = date.fromisoformat
        yield mock_date


class TestRelativeDays:
    def test_today(self):
        assert parse_date_range("today") == (FIXED_DATE, FIXED_DATE)

    def test_yesterday(self):
        y = FIXED_DATE - timedelta(days=1)
        assert parse_date_range("yesterday") == (y, y)

    def test_tomorrow(self):
        t = FIXED_DATE + timedelta(days=1)
        assert parse_date_range("tomorrow") == (t, t)


class TestLastNDays:
    def test_last_7_days(self):
        start, end = parse_date_range("last-7-days")
        assert end == FIXED_DATE
        assert start == FIXED_DATE - timedelta(days=7)

    def test_last_30_days(self):
        start, end = parse_date_range("last-30-days")
        assert end == FIXED_DATE
        assert start == FIXED_DATE - timedelta(days=30)

    def test_last_90_days(self):
        start, end = parse_date_range("last-90-days")
        assert end == FIXED_DATE
        assert start == FIXED_DATE - timedelta(days=90)


class TestWeeks:
    def test_this_week_starts_monday(self):
        start, end = parse_date_range("this-week")
        # 2025-06-18 is Wednesday, Monday is 2025-06-16
        assert start == date(2025, 6, 16)
        assert end == date(2025, 6, 22)
        assert start.weekday() == 0  # Monday

    def test_last_week(self):
        start, end = parse_date_range("last-week")
        assert start == date(2025, 6, 9)
        assert end == date(2025, 6, 15)

    def test_next_week(self):
        start, end = parse_date_range("next-week")
        assert start == date(2025, 6, 23)
        assert end == date(2025, 6, 29)


class TestMonths:
    def test_this_month(self):
        start, end = parse_date_range("this-month")
        assert start == date(2025, 6, 1)
        assert end == date(2025, 6, 30)

    def test_last_month(self):
        start, end = parse_date_range("last-month")
        assert start == date(2025, 5, 1)
        assert end == date(2025, 5, 31)

    def test_next_month(self):
        start, end = parse_date_range("next-month")
        assert start == date(2025, 7, 1)
        assert end == date(2025, 7, 31)

    def test_last_month_wraps_to_december(self, freeze_today):
        freeze_today.today.return_value = date(2025, 1, 15)
        start, end = parse_date_range("last-month")
        assert start == date(2024, 12, 1)
        assert end == date(2024, 12, 31)

    def test_next_month_wraps_to_january(self, freeze_today):
        freeze_today.today.return_value = date(2025, 12, 15)
        start, end = parse_date_range("next-month")
        assert start == date(2026, 1, 1)
        assert end == date(2026, 1, 31)


class TestQuarters:
    def test_this_quarter(self):
        # June is Q2 (Apr-Jun)
        start, end = parse_date_range("this-quarter")
        assert start == date(2025, 4, 1)
        assert end == date(2025, 6, 30)

    def test_last_quarter(self):
        start, end = parse_date_range("last-quarter")
        assert start == date(2025, 1, 1)
        assert end == date(2025, 3, 31)

    def test_next_quarter(self):
        start, end = parse_date_range("next-quarter")
        assert start == date(2025, 7, 1)
        assert end == date(2025, 9, 30)

    def test_last_quarter_wraps_to_q4(self, freeze_today):
        freeze_today.today.return_value = date(2025, 1, 15)
        start, end = parse_date_range("last-quarter")
        assert start == date(2024, 10, 1)
        assert end == date(2024, 12, 31)


class TestYears:
    def test_this_year(self):
        assert parse_date_range("this-year") == (date(2025, 1, 1), date(2025, 12, 31))

    def test_last_year(self):
        assert parse_date_range("last-year") == (date(2024, 1, 1), date(2024, 12, 31))


class TestExplicitDates:
    def test_single_date(self):
        d = date(2025, 3, 15)
        assert parse_date_range("2025-03-15") == (d, d)

    def test_date_range(self):
        assert parse_date_range("2025-01-01:2025-01-31") == (date(2025, 1, 1), date(2025, 1, 31))

    def test_date_range_dotdot_separator(self):
        assert parse_date_range("2025-01-01..2025-01-31") == (date(2025, 1, 1), date(2025, 1, 31))

    def test_date_range_dotdot_same_day(self):
        assert parse_date_range("2026-01-02..2026-01-02") == (date(2026, 1, 2), date(2026, 1, 2))

    def test_bad_dotdot_range_raises(self):
        with pytest.raises(DateParseError):
            parse_date_range("bad..dates")


class TestApplyDateParams:
    def test_default_keys_are_created(self):
        params: dict = {}
        apply_date_params(params, "today", None, None)
        assert "createdOnOrAfter" in params
        assert "createdBefore" in params

    def test_custom_keys(self):
        params: dict = {}
        apply_date_params(
            params,
            "today",
            None,
            None,
            start_key="startsOnOrAfter",
            end_key="startsBefore",
        )
        assert "startsOnOrAfter" in params
        assert "startsBefore" in params

    def test_explicit_overrides_range(self):
        params: dict = {}
        apply_date_params(params, "last-week", "2025-01-01", "2025-01-31")
        assert params["createdOnOrAfter"] == "2025-01-01"
        assert params["createdBefore"] == "2025-01-31"

    def test_noop_when_all_none(self):
        params: dict = {}
        apply_date_params(params, None, None, None)
        assert params == {}


class TestErrors:
    def test_unknown_string_raises(self):
        with pytest.raises(DateParseError):
            parse_date_range("not-a-date")

    def test_bad_explicit_range_raises(self):
        with pytest.raises(DateParseError):
            parse_date_range("bad:dates")

    def test_whitespace_is_stripped(self):
        d = date(2025, 3, 15)
        assert parse_date_range("  2025-03-15  ") == (d, d)


class TestValidateMaxRange:
    def test_within_limit_passes(self):
        params = {"startsOnOrAfter": "2025-01-01", "startsBefore": "2025-01-14"}
        validate_max_range(params, "startsOnOrAfter", "startsBefore", 14)

    def test_exactly_at_limit_passes(self):
        params = {"startsOnOrAfter": "2025-01-01", "startsBefore": "2025-01-15"}
        validate_max_range(params, "startsOnOrAfter", "startsBefore", 14)

    def test_exceeds_limit_raises(self):
        params = {"startsOnOrAfter": "2025-01-01", "startsBefore": "2025-01-20"}
        with pytest.raises(DateParseError, match="19 days.*maximum is 14"):
            validate_max_range(params, "startsOnOrAfter", "startsBefore", 14)

    def test_missing_keys_is_noop(self):
        validate_max_range({}, "startsOnOrAfter", "startsBefore", 14)

    def test_partial_keys_is_noop(self):
        validate_max_range({"startsOnOrAfter": "2025-01-01"}, "startsOnOrAfter", "startsBefore", 14)
