"""
Tests for is_weekend, is_holiday, is_business_day, is_expiry_day, day_of_week.
Uses verified 2024 NYSE holidays as anchors.
"""

from datetime import date, datetime

import pytest

import quando as q

# 2024 NYSE holidays (verified)
NYSE_HOLIDAYS_2024 = [
    "2024-01-01",  # New Year's Day      Mon
    "2024-01-15",  # MLK Day             Mon
    "2024-02-19",  # Presidents Day      Mon
    "2024-03-29",  # Good Friday         Fri
    "2024-05-27",  # Memorial Day        Mon
    "2024-06-19",  # Juneteenth          Wed
    "2024-07-04",  # Independence Day    Thu
    "2024-09-02",  # Labor Day           Mon
    "2024-11-28",  # Thanksgiving        Thu
    "2024-12-25",  # Christmas           Wed
]

# Confirmed NYSE trading days in 2024
NYSE_TRADING_DAYS_2024 = [
    "2024-01-02",  # First trading day of year
    "2024-01-16",  # Day after MLK
    "2024-01-19",  # Third Friday (expiry)
    "2024-03-28",  # Thursday before Good Friday
    "2024-06-20",  # Day after Juneteenth
    "2024-07-05",  # Day after Independence Day
    "2024-11-29",  # Day after Thanksgiving
    "2024-12-26",  # Day after Christmas
    "2024-12-31",  # Last trading day of year
]


class TestIsWeekend:
    @pytest.mark.parametrize(
        "value",
        [
            "2024-01-13",  # Saturday
            "2024-01-14",  # Sunday
            "2024-03-30",  # Saturday (after Good Friday)
            "2024-12-28",  # Saturday
            "2024-12-29",  # Sunday
        ],
    )
    def test_weekends_are_weekends(self, value):
        assert q.is_weekend(value) is True

    @pytest.mark.parametrize(
        "value",
        [
            "2024-01-15",  # Monday (holiday, but still a weekday)
            "2024-01-16",  # Tuesday
            "2024-01-17",  # Wednesday
            "2024-01-18",  # Thursday
            "2024-01-19",  # Friday
        ],
    )
    def test_weekdays_are_not_weekends(self, value):
        assert q.is_weekend(value) is False

    def test_accepts_datetime(self):
        assert q.is_weekend(datetime(2024, 1, 13)) is True
        assert q.is_weekend(datetime(2024, 1, 15)) is False

    def test_accepts_date(self):
        assert q.is_weekend(date(2024, 1, 13)) is True

    def test_accepts_unix_timestamp(self):
        # 2024-01-13 00:00 UTC = 1705104000
        assert q.is_weekend(1705104000) is True

    def test_no_calendar_needed(self):
        # Should work without q.use() ever being called
        import quando._state as _state

        _state._CAL_SET = False
        # Saturday — answer doesn't depend on calendar
        assert q.is_weekend("2024-01-13") is True


class TestIsHoliday:
    @pytest.mark.parametrize("holiday", NYSE_HOLIDAYS_2024)
    def test_all_nyse_holidays_2024(self, holiday):
        assert q.is_holiday(holiday, cal="NYSE") is True

    @pytest.mark.parametrize("trading_day", NYSE_TRADING_DAYS_2024)
    def test_trading_days_are_not_holidays(self, trading_day):
        assert q.is_holiday(trading_day, cal="NYSE") is False

    def test_weekends_are_not_holidays(self):
        assert q.is_holiday("2024-01-13") is False  # Saturday
        assert q.is_holiday("2024-01-14") is False  # Sunday

    def test_uses_global_calendar(self):
        q.use("NYSE")
        assert q.is_holiday("2024-01-15") is True  # MLK Day

    def test_cal_arg_overrides_global(self):
        q.use("NYSE")
        # MLK Day is NYSE-only; EUREX doesn't observe it
        assert q.is_holiday("2024-01-15", cal="EUREX") is False

    def test_good_friday_observed_by_both_nyse_and_eurex(self):
        assert q.is_holiday("2024-03-29", cal="NYSE") is True
        assert q.is_holiday("2024-03-29", cal="EUREX") is True

    def test_accepts_all_input_types(self):
        for value in ("2024-01-01", datetime(2024, 1, 1), date(2024, 1, 1)):
            assert q.is_holiday(value, cal="NYSE") is True


class TestIsBusinessDay:
    @pytest.mark.parametrize("trading_day", NYSE_TRADING_DAYS_2024)
    def test_trading_days_are_business_days(self, trading_day):
        assert q.is_business_day(trading_day, cal="NYSE") is True

    @pytest.mark.parametrize("holiday", NYSE_HOLIDAYS_2024)
    def test_holidays_are_not_business_days(self, holiday):
        assert q.is_business_day(holiday, cal="NYSE") is False

    @pytest.mark.parametrize("weekend", ["2024-01-13", "2024-01-14"])
    def test_weekends_are_not_business_days(self, weekend):
        assert q.is_business_day(weekend) is False

    def test_uses_global_calendar(self):
        q.use("NYSE")
        assert q.is_business_day("2024-01-02") is True
        assert q.is_business_day("2024-01-15") is False  # MLK

    def test_cal_arg_overrides(self):
        # MLK is NYSE holiday; EUREX trades that day
        assert q.is_business_day("2024-01-15", cal="NYSE") is False
        assert q.is_business_day("2024-01-15", cal="EUREX") is True

    def test_accepts_all_input_types(self):
        for value in ("2024-01-02", datetime(2024, 1, 2), date(2024, 1, 2), 1704153600):
            assert q.is_business_day(value, cal="NYSE") is True


class TestIsExpiryDay:
    # Third Fridays of each month in 2024
    @pytest.mark.parametrize(
        "third_friday",
        [
            "2024-01-19",
            "2024-02-16",
            "2024-03-15",
            "2024-04-19",
            "2024-05-17",
            "2024-06-21",
            "2024-07-19",
            "2024-08-16",
            "2024-09-20",
            "2024-10-18",
            "2024-11-15",
            "2024-12-20",
        ],
    )
    def test_third_fridays_are_expiry_days(self, third_friday):
        assert q.is_expiry_day(third_friday) is True

    # First and second Fridays are NOT expiry days
    @pytest.mark.parametrize(
        "not_expiry",
        [
            "2024-01-05",  # 1st Friday of Jan
            "2024-01-12",  # 2nd Friday of Jan
            "2024-01-26",  # 4th Friday of Jan
            "2024-02-09",  # 2nd Friday of Feb
            "2024-03-01",  # 1st Friday of Mar
        ],
    )
    def test_other_fridays_are_not_expiry(self, not_expiry):
        assert q.is_expiry_day(not_expiry) is False

    @pytest.mark.parametrize(
        "non_friday",
        [
            "2024-01-15",  # Monday
            "2024-01-16",  # Tuesday
            "2024-01-17",  # Wednesday
            "2024-01-18",  # Thursday
            "2024-01-13",  # Saturday
        ],
    )
    def test_non_fridays_are_not_expiry(self, non_friday):
        assert q.is_expiry_day(non_friday) is False

    def test_accepts_datetime(self):
        assert q.is_expiry_day(datetime(2024, 1, 19)) is True

    def test_accepts_date_object(self):
        assert q.is_expiry_day(date(2024, 1, 19)) is True


class TestDayOfWeek:
    @pytest.mark.parametrize(
        "date_str, expected",
        [
            ("2024-01-15", "Monday"),
            ("2024-01-16", "Tuesday"),
            ("2024-01-17", "Wednesday"),
            ("2024-01-18", "Thursday"),
            ("2024-01-19", "Friday"),
            ("2024-01-13", "Saturday"),
            ("2024-01-14", "Sunday"),
        ],
    )
    def test_all_weekday_names(self, date_str, expected):
        assert q.day_of_week(date_str) == expected

    def test_returns_string(self):
        assert isinstance(q.day_of_week("2024-01-15"), str)

    def test_accepts_datetime(self):
        assert q.day_of_week(datetime(2024, 1, 15)) == "Monday"

    def test_accepts_date(self):
        assert q.day_of_week(date(2024, 1, 15)) == "Monday"

    def test_accepts_unix_timestamp(self):
        assert q.day_of_week(1705276800) == "Monday"  # 2024-01-15

    def test_year_boundary(self):
        assert q.day_of_week("2024-12-31") == "Tuesday"
        assert q.day_of_week("2025-01-01") == "Wednesday"
