"""Tests for is_valid, is_same_day, is_before, is_after."""
from datetime import datetime, date, timezone
import pytest
import quando as q

UTC = timezone.utc


class TestIsValid:
    @pytest.mark.parametrize("value", [
        "2024-01-15",
        "20240115",
        "01/15/2024",
        "January 15, 2024",
        datetime(2024, 1, 15),
        datetime(2024, 1, 15, tzinfo=UTC),
        date(2024, 1, 15),
        1705276800,
        1705276800.0,
        45306,          # Excel serial
        "45306",        # Excel serial as string
    ])
    def test_valid_inputs(self, value):
        assert q.is_valid(value) is True

    @pytest.mark.parametrize("value", [
        "not-a-date",
        "99/99/9999",
        "hello",
        None,
        [],
        {},
        object(),
    ])
    def test_invalid_inputs(self, value):
        assert q.is_valid(value) is False

    def test_does_not_raise(self):
        # is_valid must never propagate exceptions
        for bad in ("xyz", None, [], object()):
            result = q.is_valid(bad)
            assert isinstance(result, bool)


class TestIsSameDay:
    def test_identical_strings(self):
        assert q.is_same_day("2024-01-15", "2024-01-15") is True

    def test_different_formats_same_day(self):
        assert q.is_same_day("2024-01-15", "20240115") is True
        assert q.is_same_day("2024-01-15", "01/15/2024") is True
        assert q.is_same_day("2024-01-15", datetime(2024, 1, 15)) is True
        assert q.is_same_day("2024-01-15", date(2024, 1, 15)) is True
        assert q.is_same_day("2024-01-15", 1705276800) is True    # Unix
        assert q.is_same_day("2024-01-15", 45306) is True          # West serial

    def test_cross_format_same_day(self):
        assert q.is_same_day(1705276800, 45306) is True

    def test_different_days(self):
        assert q.is_same_day("2024-01-15", "2024-01-16") is False

    def test_midnight_boundary(self):
        # A time at 23:59 on the 15th is same day as midnight on the 15th
        assert q.is_same_day("2024-01-15T23:59:59", "2024-01-15T00:00:00") is True

    def test_midnight_crosses_day(self):
        assert q.is_same_day("2024-01-15T23:59:59", "2024-01-16T00:00:00") is False


class TestIsBefore:
    def test_earlier_is_before(self):
        assert q.is_before("2024-01-15", "2024-01-16") is True

    def test_later_is_not_before(self):
        assert q.is_before("2024-01-16", "2024-01-15") is False

    def test_same_moment_is_not_before(self):
        assert q.is_before("2024-01-15", "2024-01-15") is False

    def test_cross_format(self):
        assert q.is_before("2024-01-15", 1705363200) is True   # Jan 16 epoch

    def test_cross_year(self):
        assert q.is_before("2023-12-31", "2024-01-01") is True

    def test_time_precision(self):
        assert q.is_before("2024-01-15T10:00:00", "2024-01-15T10:00:01") is True


class TestIsAfter:
    def test_later_is_after(self):
        assert q.is_after("2024-01-16", "2024-01-15") is True

    def test_earlier_is_not_after(self):
        assert q.is_after("2024-01-15", "2024-01-16") is False

    def test_same_moment_is_not_after(self):
        assert q.is_after("2024-01-15", "2024-01-15") is False

    def test_cross_format(self):
        assert q.is_after(1705363200, "2024-01-15") is True   # Jan 16 > Jan 15

    def test_consistency_with_is_before(self):
        a, b = "2024-03-01", "2024-06-01"
        assert q.is_before(a, b) is not q.is_after(a, b)
        assert q.is_before(b, a) is not q.is_after(b, a)
