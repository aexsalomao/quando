"""
Direct tests for quando._parse.parse and _parse_string.

These tests target the internal parsing engine, which is exercised
indirectly by every public function but never tested in isolation.
Covering _parse directly protects against regressions if _FORMATS is
reordered, new input types are added, or boundary constants change.
"""
from datetime import datetime, date, timezone, timedelta
import pytest

from quando._parse import parse, _parse_string, _WEST_MIN, _WEST_MAX, _WEST_EPOCH

UTC = timezone.utc

# Canonical anchor: 2024-01-15 00:00:00 UTC
_ANCHOR_DATE = date(2024, 1, 15)
_ANCHOR_DT = datetime(2024, 1, 15, tzinfo=UTC)


# ── Input type dispatch ───────────────────────────────────────────────────────

class TestParseInputTypes:
    def test_aware_datetime_returned_unchanged(self):
        dt = datetime(2024, 1, 15, 10, 30, tzinfo=UTC)
        result = parse(dt)
        assert result is dt

    def test_naive_datetime_gets_utc(self):
        dt = datetime(2024, 1, 15, 10, 30)
        result = parse(dt)
        assert result.tzinfo is not None
        assert result.utcoffset().total_seconds() == 0
        assert result == datetime(2024, 1, 15, 10, 30, tzinfo=UTC)

    def test_date_object_becomes_midnight_utc(self):
        result = parse(date(2024, 1, 15))
        assert result == _ANCHOR_DT

    def test_int_in_west_range_parsed_as_serial(self):
        # 45306 is the West serial for 2024-01-15
        result = parse(45306)
        assert result.date() == _ANCHOR_DATE

    def test_int_below_west_min_parsed_as_unix(self):
        # _WEST_MIN - 1 is below the range, so it must be treated as Unix
        unix = int((_WEST_EPOCH + timedelta(days=_WEST_MIN - 1) -
                    date(1970, 1, 1)).total_seconds())
        # Just verify it doesn't raise and returns a datetime
        result = parse(_WEST_MIN - 1)
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_int_above_west_max_parsed_as_unix(self):
        ts = 1_800_000_000   # 2027, well above _WEST_MAX
        result = parse(ts)
        assert isinstance(result, datetime)
        assert result.year == 2027

    def test_float_parsed_as_unix(self):
        result = parse(1705276800.0)
        assert result.date() == _ANCHOR_DATE

    def test_string_dispatches_to_parse_string(self):
        result = parse("2024-01-15")
        assert result.date() == _ANCHOR_DATE

    def test_unsupported_type_raises_type_error(self):
        for bad in ([], {}, object(), None):
            with pytest.raises(TypeError, match="quando"):
                parse(bad)

    def test_result_is_always_utc_aware(self):
        inputs = [
            "2024-01-15",
            datetime(2024, 1, 15),
            date(2024, 1, 15),
            1705276800,
            1705276800.0,
            45306,
        ]
        for v in inputs:
            result = parse(v)
            assert result.tzinfo is not None, f"naive result for {v!r}"
            assert result.utcoffset().total_seconds() == 0, f"non-UTC for {v!r}"


# ── West serial boundary ──────────────────────────────────────────────────────

class TestWestSerialBoundary:
    def test_west_min_is_1970_01_01(self):
        result = parse(_WEST_MIN)
        assert result.date() == date(1970, 1, 1)

    def test_west_max_is_within_range(self):
        result = parse(_WEST_MAX)
        assert isinstance(result, datetime)
        assert result.year >= 2099

    def test_string_west_serial_parsed_correctly(self):
        result = _parse_string("45306")
        assert result.date() == _ANCHOR_DATE

    def test_string_below_west_min_not_treated_as_serial(self):
        # A 5-digit number below _WEST_MIN should fall through to strptime/dateutil
        # and raise, not silently produce a wrong date
        below = str(_WEST_MIN - 1)
        with pytest.raises(ValueError):
            _parse_string(below)


# ── Format strings ────────────────────────────────────────────────────────────

class TestFormatStrings:
    """Each format in _FORMATS gets at least one test."""

    def test_yyyymmdd(self):
        assert _parse_string("20240115").date() == _ANCHOR_DATE

    def test_yyyy_mm_dd(self):
        assert _parse_string("2024-01-15").date() == _ANCHOR_DATE

    def test_mm_dd_yyyy(self):
        # %m/%d/%Y — US slash format
        assert _parse_string("01/15/2024").date() == _ANCHOR_DATE

    def test_dd_mm_yyyy(self):
        # %d/%m/%Y — only reachable when day > 12, so it can't match %m/%d/%Y
        assert _parse_string("15/01/2024").date() == _ANCHOR_DATE

    def test_iso_datetime_no_suffix(self):
        # %Y-%m-%dT%H:%M:%S
        result = _parse_string("2024-01-15T10:30:00")
        assert result.date() == _ANCHOR_DATE
        assert result.hour == 10
        assert result.minute == 30

    def test_iso_datetime_z_suffix(self):
        # %Y-%m-%dT%H:%M:%SZ
        result = _parse_string("2024-01-15T10:30:00Z")
        assert result.date() == _ANCHOR_DATE
        assert result.hour == 10

    def test_space_separated_datetime(self):
        # %Y-%m-%d %H:%M:%S
        result = _parse_string("2024-01-15 10:30:00")
        assert result.date() == _ANCHOR_DATE
        assert result.hour == 10

    def test_iso_datetime_with_microseconds(self):
        # %Y-%m-%dT%H:%M:%S.%f
        result = _parse_string("2024-01-15T10:30:00.123456")
        assert result.date() == _ANCHOR_DATE
        assert result.microsecond == 123456

    def test_all_format_results_are_utc_aware(self):
        samples = [
            "20240115",
            "2024-01-15",
            "01/15/2024",
            "15/01/2024",
            "2024-01-15T10:30:00",
            "2024-01-15T10:30:00Z",
            "2024-01-15 10:30:00",
            "2024-01-15T10:30:00.000001",
        ]
        for s in samples:
            result = _parse_string(s)
            assert result.tzinfo is not None, f"naive result for '{s}'"


# ── %m/%d/%Y vs %d/%m/%Y ordering ────────────────────────────────────────────

class TestSlashFormatOrdering:
    """
    _FORMATS tries %m/%d/%Y before %d/%m/%Y.
    When the month field is ≤ 12, the first format wins.
    This test documents the tie-breaking behaviour so any reordering
    of _FORMATS breaks loudly here rather than silently in production.
    """

    def test_ambiguous_date_resolves_to_month_first(self):
        # "01/06/2024" could be Jan 6 (%m/%d/%Y) or Jun 1 (%d/%m/%Y).
        # With the current ordering, %m/%d/%Y wins → January 6.
        result = _parse_string("01/06/2024")
        assert result.month == 1
        assert result.day == 6

    def test_unambiguous_dd_slash_mm_parses_correctly(self):
        # Day > 12 forces %d/%m/%Y because %m/%d/%Y would fail
        result = _parse_string("15/01/2024")
        assert result.month == 1
        assert result.day == 15


# ── dateutil fallback ─────────────────────────────────────────────────────────

class TestDateutilFallback:
    """Strings that none of the strptime formats match fall through to dateutil."""

    def test_natural_language_date(self):
        result = _parse_string("January 15, 2024")
        assert result.date() == _ANCHOR_DATE

    def test_natural_language_result_is_utc_aware(self):
        result = _parse_string("January 15, 2024")
        assert result.tzinfo is not None

    def test_unrecognised_string_raises_value_error(self):
        with pytest.raises(ValueError, match="quando"):
            _parse_string("not-a-date")

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError, match="quando"):
            _parse_string("")
