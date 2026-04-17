"""Tests for q.use / q.verbose / q.as_of / q.today."""

from datetime import date, datetime, timezone

import quando as q
import quando._state as _state


class TestUse:
    def test_sets_global_calendar(self):
        q.use("EUREX")
        assert _state._GLOBAL_CAL == "EUREX"

    def test_normalises_to_uppercase(self):
        q.use("eurex")
        assert _state._GLOBAL_CAL == "EUREX"

    def test_subsequent_calls_override(self):
        q.use("NYSE")
        q.use("LSE")
        assert _state._GLOBAL_CAL == "LSE"

    def test_propagates_to_is_holiday(self):
        # MLK Day is a NYSE holiday but not a EUREX holiday
        q.use("NYSE")
        assert q.is_holiday("2024-01-15") is True
        q.use("EUREX")
        assert q.is_holiday("2024-01-15") is False


class TestVerbose:
    def test_sets_flag_true(self):
        q.verbose(True)
        assert _state._VERBOSE is True

    def test_sets_flag_false(self):
        q.verbose(True)
        q.verbose(False)
        assert _state._VERBOSE is False


class TestAsOf:
    def test_stores_datetime(self):
        q.as_of("2024-06-15")
        stored = _state.get_as_of()
        assert isinstance(stored, datetime)
        assert stored.date() == date(2024, 6, 15)

    def test_accepts_datetime_object(self):
        dt = datetime(2024, 6, 15, tzinfo=timezone.utc)
        q.as_of(dt)
        assert _state.get_as_of().date() == date(2024, 6, 15)

    def test_accepts_unix_timestamp(self):
        q.as_of(1705276800)  # 2024-01-15
        assert _state.get_as_of().date() == date(2024, 1, 15)

    def test_overwrite(self):
        q.as_of("2024-01-01")
        q.as_of("2024-12-31")
        assert _state.get_as_of().date() == date(2024, 12, 31)


class TestToday:
    def test_returns_datetime(self):
        assert isinstance(q.today(), datetime)

    def test_is_timezone_aware(self):
        assert q.today().tzinfo is not None

    def test_nyse_timezone_is_eastern(self):
        q.use("NYSE")
        tz = q.today().tzinfo
        assert "America/New_York" in str(tz) or "EST" in str(tz) or "EDT" in str(tz)

    def test_time_is_midnight(self):
        t = q.today()
        assert t.hour == 0 and t.minute == 0 and t.second == 0

    def test_date_is_today(self):
        from datetime import datetime as dt
        from zoneinfo import ZoneInfo

        q.use("NYSE")
        today_eastern = dt.now(ZoneInfo("America/New_York")).date()
        assert q.today().date() == today_eastern

    def test_respects_cal_arg(self):
        t = q.today(cal="EUREX")
        assert t.tzinfo is not None
