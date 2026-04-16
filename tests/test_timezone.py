"""Tests for shift_tz, localize, strip_tz."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest

import quando as q

UTC = timezone.utc


class TestShiftTz:
    def test_utc_to_eastern(self):
        # 2024-01-15 00:00 UTC == 2024-01-14 19:00 EST (UTC-5)
        result = q.shift_tz("2024-01-15", "America/New_York")
        assert result.date().isoformat() in ("2024-01-14", "2024-01-15")
        assert result.tzinfo is not None

    def test_utc_to_berlin(self):
        # 2024-01-15 00:00 UTC == 2024-01-15 01:00 CET (UTC+1)
        result = q.shift_tz("2024-01-15", "Europe/Berlin")
        assert result.hour == 1

    def test_result_is_timezone_aware(self):
        result = q.shift_tz("2024-01-15", "Asia/Tokyo")
        assert result.tzinfo is not None

    def test_clock_changes(self):
        # 2024-01-15 12:00 UTC -> different hours in different zones
        base = datetime(2024, 1, 15, 12, 0, tzinfo=UTC)
        eastern = q.shift_tz(base, "America/New_York")
        berlin = q.shift_tz(base, "Europe/Berlin")
        assert eastern.hour != berlin.hour

    def test_accepts_all_input_types(self):
        for value in ("2024-06-15", datetime(2024, 6, 15, tzinfo=UTC), 1718409600):
            result = q.shift_tz(value, "America/New_York")
            assert result.tzinfo is not None

    def test_invalid_tz_raises(self):
        with pytest.raises(ZoneInfoNotFoundError):
            q.shift_tz("2024-01-15", "Not/Real_Tz")


class TestLocalize:
    def test_attaches_tz_without_shifting(self):
        result = q.localize("2024-01-15", "America/New_York")
        assert result.tzinfo is not None
        # Clock should read midnight New York time, not UTC
        assert result.hour == 0
        assert result.minute == 0

    def test_different_from_shift_tz(self):
        # shift_tz converts existing UTC time to a new zone
        # localize stamps the tz label onto the naive time directly
        shifted = q.shift_tz("2024-01-15", "America/New_York")
        localized = q.localize("2024-01-15", "America/New_York")
        # Localized midnight NY != shifted midnight UTC (which is 19:00 NY)
        assert shifted != localized

    def test_naive_datetime_input(self):
        naive = datetime(2024, 6, 15, 9, 30)
        result = q.localize(naive, "America/New_York")
        assert result.tzinfo is not None
        assert result.hour == 9
        assert result.minute == 30

    def test_dst_aware_localize(self):
        # June is EDT (UTC-4), January is EST (UTC-5)
        june = q.localize("2024-06-15", "America/New_York")
        jan = q.localize("2024-01-15", "America/New_York")
        # UTC offsets should differ
        assert june.utcoffset() != jan.utcoffset()


class TestStripTz:
    def test_removes_timezone(self):
        aware = datetime(2024, 1, 15, tzinfo=UTC)
        result = q.strip_tz(aware)
        assert result.tzinfo is None

    def test_returns_utc_equivalent_time(self):
        # 2024-01-15 01:00 Berlin == 2024-01-15 00:00 UTC
        dt_berlin = datetime(2024, 1, 15, 1, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        result = q.strip_tz(dt_berlin)
        assert result.hour == 0  # stripped to UTC midnight
        assert result.tzinfo is None

    def test_naive_utc_input_passes_through(self):
        # Naive input is treated as UTC
        result = q.strip_tz("2024-01-15")
        assert result.tzinfo is None
        assert result.date().isoformat() == "2024-01-15"

    def test_string_input(self):
        result = q.strip_tz("2024-06-15T14:30:00")
        assert result.tzinfo is None
        assert result.hour == 14
