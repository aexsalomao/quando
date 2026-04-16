"""
Tests for business_days_between, date_range, trading_days_in_month,
trading_days_in_year, filter_business_days.
"""

from datetime import date, datetime

import quando as q


class TestBusinessDaysBetween:
    def test_adjacent_business_days_have_zero_between(self):
        # Jan 16 and Jan 17 are consecutive; nothing strictly between them
        assert q.business_days_between("2024-01-16", "2024-01-17", cal="NYSE") == 0

    def test_with_gap_of_two(self):
        # Jan 16 → Jan 19: Jan 17, Jan 18 = 2
        assert q.business_days_between("2024-01-16", "2024-01-19", cal="NYSE") == 2

    def test_across_weekend(self):
        # Jan 19 (Fri) → Jan 23 (Tue): Mon Jan 22 = 1
        assert q.business_days_between("2024-01-19", "2024-01-23", cal="NYSE") == 1

    def test_across_holiday_and_weekend(self):
        # Jan 12 (Fri) → Jan 16 (Tue): Sat, Sun excluded; MLK Mon excluded = 0
        assert q.business_days_between("2024-01-12", "2024-01-16", cal="NYSE") == 0

    def test_same_start_and_end_returns_zero(self):
        assert q.business_days_between("2024-01-16", "2024-01-16", cal="NYSE") == 0

    def test_reversed_dates_return_zero(self):
        assert q.business_days_between("2024-01-17", "2024-01-16", cal="NYSE") == 0

    def test_full_week_without_holidays(self):
        # Jan 22 (Mon) → Jan 27 (Sat): Tue, Wed, Thu, Fri = 4
        assert q.business_days_between("2024-01-22", "2024-01-27", cal="NYSE") == 4

    def test_accepts_all_input_types(self):
        a = date(2024, 1, 16)
        b = datetime(2024, 1, 19)
        assert q.business_days_between(a, b, cal="NYSE") == 2

    def test_excludes_endpoints(self):
        # Explicitly verify the endpoints are excluded
        # Between Jan 16 and Jan 19: only 17, 18 count
        count = q.business_days_between("2024-01-16", "2024-01-19", cal="NYSE")
        assert count == 2
        # Both endpoints are business days, neither is counted
        for d in ("2024-01-16", "2024-01-19"):
            assert q.is_business_day(d, cal="NYSE")


class TestDateRange:
    def test_returns_list(self):
        result = q.date_range("2024-01-15", "2024-01-22", cal="NYSE")
        assert isinstance(result, list)

    def test_all_results_are_business_days(self):
        result = q.date_range("2024-01-10", "2024-01-31", cal="NYSE")
        for dt in result:
            assert q.is_business_day(dt, cal="NYSE") is True

    def test_includes_endpoints_when_business_days(self):
        result = q.date_range("2024-01-16", "2024-01-19", cal="NYSE")
        dates = [r.date() for r in result]
        assert date(2024, 1, 16) in dates
        assert date(2024, 1, 19) in dates

    def test_excludes_holidays_from_range(self):
        # Jan 15 (MLK) should not appear in range Jan 12 – Jan 16
        result = q.date_range("2024-01-12", "2024-01-16", cal="NYSE")
        dates = [r.date() for r in result]
        assert date(2024, 1, 15) not in dates  # MLK
        assert date(2024, 1, 13) not in dates  # Sat
        assert date(2024, 1, 14) not in dates  # Sun
        assert date(2024, 1, 12) in dates
        assert date(2024, 1, 16) in dates

    def test_empty_when_start_equals_end_weekend(self):
        # Entire range is a weekend
        result = q.date_range("2024-01-13", "2024-01-14", cal="NYSE")
        assert result == []

    def test_sorted_ascending(self):
        result = q.date_range("2024-01-02", "2024-01-31", cal="NYSE")
        assert result == sorted(result)

    def test_january_2024_has_21_trading_days(self):
        result = q.date_range("2024-01-01", "2024-01-31", cal="NYSE")
        assert len(result) == 21

    def test_reversed_range_returns_empty(self):
        result = q.date_range("2024-01-20", "2024-01-15", cal="NYSE")
        assert result == []


class TestTradingDaysInMonth:
    def test_january_2024(self):
        # 23 weekdays - 2 holidays (Jan 1 NYD, Jan 15 MLK) = 21
        assert q.trading_days_in_month("2024-01-15", cal="NYSE") == 21

    def test_march_2024(self):
        # 21 weekdays - 1 holiday (Mar 29 Good Friday) = 20
        assert q.trading_days_in_month("2024-03-15", cal="NYSE") == 20

    def test_july_2024(self):
        # 23 weekdays - 1 holiday (Jul 4 Independence Day) = 22
        assert q.trading_days_in_month("2024-07-01", cal="NYSE") == 22

    def test_result_is_int(self):
        assert isinstance(q.trading_days_in_month("2024-01-15", cal="NYSE"), int)

    def test_result_is_positive(self):
        for month in range(1, 13):
            val = f"2024-{month:02d}-15"
            assert q.trading_days_in_month(val, cal="NYSE") > 0

    def test_result_lte_total_weekdays(self):
        import calendar

        for month in range(1, 13):
            val = f"2024-{month:02d}-15"
            trading = q.trading_days_in_month(val, cal="NYSE")
            # Count weekdays in month
            days_in_month = calendar.monthrange(2024, month)[1]
            weekdays = sum(
                1 for d in range(1, days_in_month + 1) if date(2024, month, d).weekday() < 5
            )
            assert trading <= weekdays


class TestTradingDaysInYear:
    def test_2024_nyse_is_252(self):
        # Standard NYSE trading days for 2024
        assert q.trading_days_in_year(2024, cal="NYSE") == 252

    def test_returns_int(self):
        assert isinstance(q.trading_days_in_year(2024, cal="NYSE"), int)

    def test_result_is_positive(self):
        assert q.trading_days_in_year(2024, cal="NYSE") > 0

    def test_result_less_than_365(self):
        assert q.trading_days_in_year(2024, cal="NYSE") < 366

    def test_consistent_with_sum_of_months(self):
        year_total = q.trading_days_in_year(2024, cal="NYSE")
        month_sum = sum(
            q.trading_days_in_month(f"2024-{m:02d}-01", cal="NYSE") for m in range(1, 13)
        )
        assert year_total == month_sum


class TestFilterBusinessDays:
    def test_removes_weekends(self):
        values = ["2024-01-13", "2024-01-14", "2024-01-15", "2024-01-16"]
        result = q.filter_business_days(values, cal="NYSE")
        result_dates = [q.to_datetime(r).date() for r in result]
        assert date(2024, 1, 13) not in result_dates  # Sat
        assert date(2024, 1, 14) not in result_dates  # Sun
        assert date(2024, 1, 15) not in result_dates  # MLK
        assert date(2024, 1, 16) in result_dates

    def test_removes_holidays(self):
        values = ["2024-01-01", "2024-01-02"]
        result = q.filter_business_days(values, cal="NYSE")
        result_dates = [q.to_datetime(r).date() for r in result]
        assert date(2024, 1, 1) not in result_dates  # New Year
        assert date(2024, 1, 2) in result_dates

    def test_empty_list(self):
        assert q.filter_business_days([], cal="NYSE") == []

    def test_all_business_days_unchanged(self):
        values = ["2024-01-16", "2024-01-17", "2024-01-18"]
        result = q.filter_business_days(values, cal="NYSE")
        assert len(result) == 3

    def test_all_non_business_days_filtered(self):
        values = ["2024-01-13", "2024-01-14", "2024-01-15"]  # Sat, Sun, MLK
        result = q.filter_business_days(values, cal="NYSE")
        assert result == []

    def test_preserves_original_values(self):
        # The returned items should be the originals, not converted datetimes
        values = ["2024-01-16", "2024-01-17"]
        result = q.filter_business_days(values, cal="NYSE")
        assert result == values

    def test_accepts_mixed_input_types(self):
        values = [date(2024, 1, 16), "2024-01-17", datetime(2024, 1, 18)]
        result = q.filter_business_days(values, cal="NYSE")
        assert len(result) == 3
