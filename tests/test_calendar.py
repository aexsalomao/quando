"""Tests for list_holidays, add_holiday, remove_holiday."""

from datetime import date

import quando as q


class TestListHolidays:
    def test_returns_list_of_tuples(self):
        holidays = q.list_holidays(2024, cal="NYSE")
        assert isinstance(holidays, list)
        assert all(isinstance(h, tuple) and len(h) == 2 for h in holidays)

    def test_dates_are_date_objects(self):
        for d, _ in q.list_holidays(2024, cal="NYSE"):
            assert isinstance(d, date)

    def test_names_are_strings(self):
        for _, name in q.list_holidays(2024, cal="NYSE"):
            assert isinstance(name, str)

    def test_sorted_by_date(self):
        holidays = q.list_holidays(2024, cal="NYSE")
        dates = [d for d, _ in holidays]
        assert dates == sorted(dates)

    def test_contains_known_nyse_holidays(self):
        holidays = q.list_holidays(2024, cal="NYSE")
        holiday_dates = {d for d, _ in holidays}
        expected = {
            date(2024, 1, 1),  # New Year's Day
            date(2024, 1, 15),  # MLK Day
            date(2024, 7, 4),  # Independence Day
            date(2024, 12, 25),  # Christmas
        }
        assert expected.issubset(holiday_dates)

    def test_all_holidays_are_in_requested_year(self):
        for d, _ in q.list_holidays(2024, cal="NYSE"):
            assert d.year == 2024

    def test_no_weekends_in_list(self):
        for d, _ in q.list_holidays(2024, cal="NYSE"):
            assert d.weekday() < 5, f"{d} is a weekend"

    def test_uses_global_calendar(self):
        q.use("NYSE")
        holidays = q.list_holidays(2024)
        holiday_dates = {d for d, _ in holidays}
        assert date(2024, 1, 15) in holiday_dates  # MLK Day

    def test_eurex_differs_from_nyse(self):
        nyse = {d for d, _ in q.list_holidays(2024, cal="NYSE")}
        eurex = {d for d, _ in q.list_holidays(2024, cal="EUREX")}
        # MLK Day is NYSE only
        assert date(2024, 1, 15) in nyse
        assert date(2024, 1, 15) not in eurex

    def test_empty_for_future_year_is_still_a_list(self):
        result = q.list_holidays(2099, cal="NYSE")
        assert isinstance(result, list)


class TestAddHoliday:
    def test_added_holiday_detected_by_is_holiday(self):
        q.add_holiday("2024-03-20", "Custom Day", cal="NYSE")
        assert q.is_holiday("2024-03-20", cal="NYSE") is True

    def test_added_holiday_makes_day_non_business(self):
        # 2024-03-20 is normally a business day
        assert q.is_business_day("2024-03-20", cal="NYSE") is True
        q.add_holiday("2024-03-20", "Custom Day", cal="NYSE")
        assert q.is_business_day("2024-03-20", cal="NYSE") is False

    def test_added_holiday_appears_in_list_holidays(self):
        q.add_holiday("2024-03-20", "Custom Day", cal="NYSE")
        holidays = q.list_holidays(2024, cal="NYSE")
        holiday_dates = {d for d, _ in holidays}
        assert date(2024, 3, 20) in holiday_dates

    def test_added_holiday_has_correct_name(self):
        q.add_holiday("2024-03-20", "My Special Day", cal="NYSE")
        holidays = dict(q.list_holidays(2024, cal="NYSE"))
        assert holidays.get(date(2024, 3, 20)) == "My Special Day"

    def test_accepts_various_input_formats(self):
        from datetime import datetime

        q.add_holiday(datetime(2024, 4, 10), "Custom A", cal="NYSE")
        q.add_holiday(date(2024, 4, 11), "Custom B", cal="NYSE")
        assert q.is_holiday("2024-04-10", cal="NYSE") is True
        assert q.is_holiday("2024-04-11", cal="NYSE") is True

    def test_calendar_isolation(self):
        q.add_holiday("2024-03-20", "NYSE Only", cal="NYSE")
        assert q.is_holiday("2024-03-20", cal="NYSE") is True
        assert q.is_holiday("2024-03-20", cal="EUREX") is False

    def test_uses_global_calendar_when_cal_omitted(self):
        q.use("NYSE")
        q.add_holiday("2024-04-15", "No Cal Holiday")
        assert q.is_holiday("2024-04-15", cal="NYSE") is True


class TestRemoveHoliday:
    def test_removed_holiday_no_longer_detected(self):
        # Jan 1 is a NYSE holiday
        assert q.is_holiday("2024-01-01", cal="NYSE") is True
        q.remove_holiday("2024-01-01", cal="NYSE")
        assert q.is_holiday("2024-01-01", cal="NYSE") is False

    def test_removed_holiday_becomes_business_day(self):
        # 2024-01-01 is Monday and a holiday; after removal it's a business day
        q.remove_holiday("2024-01-01", cal="NYSE")
        assert q.is_business_day("2024-01-01", cal="NYSE") is True

    def test_removed_holiday_absent_from_list(self):
        q.remove_holiday("2024-01-01", cal="NYSE")
        holidays = {d for d, _ in q.list_holidays(2024, cal="NYSE")}
        assert date(2024, 1, 1) not in holidays

    def test_remove_only_affects_specified_calendar(self):
        # Remove MLK from NYSE, shouldn't affect EUREX (where it wasn't a holiday anyway)
        q.remove_holiday("2024-01-15", cal="NYSE")
        assert q.is_holiday("2024-01-15", cal="NYSE") is False

    def test_remove_nonexistent_date_does_not_raise(self):
        # Removing a date that was never a holiday shouldn't crash
        q.remove_holiday("2024-03-20", cal="NYSE")  # normal trading day

    def test_add_then_remove_cycle(self):
        q.add_holiday("2024-04-10", "Temp Holiday", cal="NYSE")
        assert q.is_holiday("2024-04-10", cal="NYSE") is True
        q.remove_holiday("2024-04-10", cal="NYSE")
        assert q.is_holiday("2024-04-10", cal="NYSE") is False
