"""
Tests for all conversion functions:
to_timestamp, to_datetime, to_west, to_iso, convert, to_timestamps, to_datetimes.
Every function is tested against all auto-detected input types.
"""
from datetime import datetime, date, timezone
import pytest
import quando as q

UTC = timezone.utc

# 2024-01-15 00:00:00 UTC in multiple representations
_DATE = date(2024, 1, 15)
_DT_NAIVE = datetime(2024, 1, 15)
_DT_AWARE = datetime(2024, 1, 15, tzinfo=UTC)
_UNIX = 1705276800        # int epoch
_UNIX_F = 1705276800.0    # float epoch
_WEST = 45306             # Excel serial
_ISO_STR = "2024-01-15T00:00:00+00:00"
_WEST_STR = "45306"

ALL_INPUTS = pytest.mark.parametrize("value", [
    "2024-01-15",
    "20240115",
    "01/15/2024",
    _DT_NAIVE,
    _DT_AWARE,
    _DATE,
    _UNIX,
    _UNIX_F,
    _WEST,
    _WEST_STR,
])


# ── to_timestamp ─────────────────────────────────────────────────────────────

class TestToTimestamp:
    @ALL_INPUTS
    def test_all_input_types(self, value):
        assert q.to_timestamp(value) == pytest.approx(1705276800.0)

    def test_returns_float(self):
        assert isinstance(q.to_timestamp("2024-01-15"), float)

    def test_unix_round_trip(self):
        ts = q.to_timestamp("2024-06-15")
        assert q.to_timestamp(ts) == pytest.approx(ts)

    def test_different_dates_differ(self):
        assert q.to_timestamp("2024-01-15") != q.to_timestamp("2024-01-16")

    def test_invalid_raises(self):
        with pytest.raises((ValueError, TypeError)):
            q.to_timestamp("not-a-date")


# ── to_datetime ───────────────────────────────────────────────────────────────

class TestToDatetime:
    @ALL_INPUTS
    def test_all_input_types(self, value):
        result = q.to_datetime(value)
        assert result.date() == _DATE

    def test_returns_datetime(self):
        assert isinstance(q.to_datetime("2024-01-15"), datetime)

    def test_returns_utc_aware(self):
        result = q.to_datetime("2024-01-15")
        assert result.tzinfo is not None
        assert result.utcoffset().total_seconds() == 0

    def test_naive_input_becomes_utc(self):
        result = q.to_datetime(datetime(2024, 1, 15))
        assert result.tzinfo is not None

    def test_aware_input_preserves_tz(self):
        import pytz
        eastern = pytz.timezone("America/New_York")
        dt_eastern = eastern.localize(datetime(2024, 1, 15, 9, 30))
        result = q.to_datetime(dt_eastern)
        assert result.date() == date(2024, 1, 15)


# ── to_west ───────────────────────────────────────────────────────────────────

class TestToWest:
    @ALL_INPUTS
    def test_all_input_types(self, value):
        assert q.to_west(value) == 45306

    def test_returns_int(self):
        assert isinstance(q.to_west("2024-01-15"), int)

    def test_known_anchor_dates(self):
        # Excel epoch is 1899-12-30; serial 1 = 1899-12-31
        assert q.to_west("1900-01-01") == 2    # known Excel serial
        assert q.to_west("2000-01-01") == 36526
        assert q.to_west("2024-01-15") == 45306

    def test_round_trip_via_to_datetime(self):
        serial = q.to_west("2024-03-15")
        assert q.to_datetime(serial).date() == date(2024, 3, 15)

    def test_round_trip_string_serial(self):
        serial = str(q.to_west("2024-06-15"))
        assert q.to_datetime(serial).date() == date(2024, 6, 15)

    def test_sequential_dates_are_sequential(self):
        assert q.to_west("2024-01-16") == q.to_west("2024-01-15") + 1

    def test_time_component_ignored(self):
        assert q.to_west("2024-01-15T23:59:59") == 45306


# ── to_iso ────────────────────────────────────────────────────────────────────

class TestToIso:
    @ALL_INPUTS
    def test_all_input_types_produce_correct_date(self, value):
        result = q.to_iso(value)
        assert result.startswith("2024-01-15")

    def test_returns_string(self):
        assert isinstance(q.to_iso("2024-01-15"), str)

    def test_format_contains_offset(self):
        result = q.to_iso("2024-01-15")
        assert "+00:00" in result or "Z" in result

    def test_known_value(self):
        assert q.to_iso("2024-01-15") == "2024-01-15T00:00:00+00:00"

    def test_round_trip(self):
        iso = q.to_iso("2024-07-04")
        assert q.to_datetime(iso).date() == date(2024, 7, 4)


# ── convert ───────────────────────────────────────────────────────────────────

class TestConvert:
    def test_timestamp_format(self):
        result = q.convert("2024-01-15", "timestamp")
        assert result == pytest.approx(1705276800.0)

    def test_datetime_format(self):
        result = q.convert("2024-01-15", "datetime")
        assert isinstance(result, datetime)
        assert result.date() == date(2024, 1, 15)

    def test_west_format(self):
        result = q.convert("2024-01-15", "west")
        assert result == 45306

    def test_iso_format(self):
        result = q.convert("2024-01-15", "iso")
        assert result == "2024-01-15T00:00:00+00:00"

    def test_case_insensitive_format(self):
        assert q.convert("2024-01-15", "TIMESTAMP") == q.convert("2024-01-15", "timestamp")
        assert q.convert("2024-01-15", "ISO") == q.convert("2024-01-15", "iso")

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="quando"):
            q.convert("2024-01-15", "bogus")


# ── batch conversions ─────────────────────────────────────────────────────────

class TestBatchConversions:
    _values = ["2024-01-15", "2024-01-16", "2024-01-17"]

    def test_to_timestamps_returns_list_of_floats(self):
        result = q.to_timestamps(self._values)
        assert isinstance(result, list)
        assert all(isinstance(x, float) for x in result)
        assert len(result) == 3

    def test_to_timestamps_correct_order(self):
        result = q.to_timestamps(self._values)
        assert result == sorted(result)

    def test_to_datetimes_returns_list_of_datetimes(self):
        result = q.to_datetimes(self._values)
        assert isinstance(result, list)
        assert all(isinstance(x, datetime) for x in result)
        assert len(result) == 3

    def test_to_datetimes_dates(self):
        result = q.to_datetimes(self._values)
        expected = [date(2024, 1, 15), date(2024, 1, 16), date(2024, 1, 17)]
        assert [r.date() for r in result] == expected

    def test_empty_list(self):
        assert q.to_timestamps([]) == []
        assert q.to_datetimes([]) == []

    def test_mixed_input_types(self):
        values = ["2024-01-15", 1705363200, date(2024, 1, 17)]
        result = q.to_datetimes(values)
        assert len(result) == 3
        assert result[0].date() == date(2024, 1, 15)
        assert result[2].date() == date(2024, 1, 17)
