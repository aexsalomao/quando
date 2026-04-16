"""
Tests for period boundary functions.
All expected values verified against 2024 NYSE calendar.
"""

from datetime import date

import quando as q


class TestStartOfMonth:
    def test_january_2024_first_bday_is_jan_2(self):
        # Jan 1 is New Year's Day; first business day is Jan 2
        assert q.start_of_month("2024-01-15", cal="NYSE").date() == date(2024, 1, 2)

    def test_accepts_any_day_in_month(self):
        # Any date in January returns the same start
        for day in (1, 10, 15, 31):
            result = q.start_of_month(f"2024-01-{day:02d}", cal="NYSE")
            assert result.date() == date(2024, 1, 2)

    def test_month_starting_on_business_day(self):
        # March 2024: Mar 1 is Friday (business day)
        assert q.start_of_month("2024-03-15", cal="NYSE").date() == date(2024, 3, 1)

    def test_month_starting_on_saturday(self):
        # June 2024: Jun 1 is Saturday → first bday is Jun 3 (Mon)
        assert q.start_of_month("2024-06-15", cal="NYSE").date() == date(2024, 6, 3)

    def test_month_starting_on_sunday(self):
        # September 2024: Sep 1 is Sunday, Sep 2 is Labor Day → Sep 3
        assert q.start_of_month("2024-09-15", cal="NYSE").date() == date(2024, 9, 3)

    def test_result_is_business_day(self):
        for month in range(1, 13):
            result = q.start_of_month(f"2024-{month:02d}-15", cal="NYSE")
            assert q.is_business_day(result, cal="NYSE") is True

    def test_result_is_in_same_month(self):
        for month in range(1, 13):
            val = f"2024-{month:02d}-15"
            result = q.start_of_month(val, cal="NYSE")
            assert result.date().month == month


class TestEndOfMonth:
    def test_january_2024_last_bday_is_jan_31(self):
        # Jan 31 is Wednesday, business day
        assert q.end_of_month("2024-01-15", cal="NYSE").date() == date(2024, 1, 31)

    def test_accepts_any_day_in_month(self):
        for day in (1, 10, 15, 31):
            result = q.end_of_month(f"2024-01-{day:02d}", cal="NYSE")
            assert result.date() == date(2024, 1, 31)

    def test_month_ending_on_saturday(self):
        # August 2024: Aug 31 is Saturday → last bday is Aug 30 (Fri)
        assert q.end_of_month("2024-08-15", cal="NYSE").date() == date(2024, 8, 30)

    def test_month_ending_on_sunday(self):
        # March 2024: Mar 31 is Sunday → last bday is Mar 28 (Thu, Good Friday is Mar 29)
        assert q.end_of_month("2024-03-15", cal="NYSE").date() == date(2024, 3, 28)

    def test_december_2024_last_bday_is_dec_31(self):
        # Dec 31 is Tuesday, business day
        assert q.end_of_month("2024-12-15", cal="NYSE").date() == date(2024, 12, 31)

    def test_result_is_business_day(self):
        for month in range(1, 13):
            result = q.end_of_month(f"2024-{month:02d}-15", cal="NYSE")
            assert q.is_business_day(result, cal="NYSE") is True

    def test_end_after_start(self):
        for month in range(1, 13):
            val = f"2024-{month:02d}-15"
            start = q.start_of_month(val, cal="NYSE")
            end = q.end_of_month(val, cal="NYSE")
            assert end.date() > start.date()


class TestStartOfQuarter:
    def test_q1_2024_starts_jan_2(self):
        # Q1: Jan 1 → Jan 3; Jan 1 is NYD → Jan 2
        assert q.start_of_quarter("2024-01-15", cal="NYSE").date() == date(2024, 1, 2)

    def test_q2_2024_starts_apr_1(self):
        # Q2: Apr 1 is Monday, business day
        assert q.start_of_quarter("2024-04-15", cal="NYSE").date() == date(2024, 4, 1)

    def test_q3_2024_starts_jul_1(self):
        # Q3: Jul 1 is Monday, business day
        assert q.start_of_quarter("2024-07-15", cal="NYSE").date() == date(2024, 7, 1)

    def test_q4_2024_starts_oct_1(self):
        # Q4: Oct 1 is Tuesday, business day
        assert q.start_of_quarter("2024-10-15", cal="NYSE").date() == date(2024, 10, 1)

    def test_any_month_in_quarter_gives_same_result(self):
        # All months in Q2 (Apr, May, Jun) should give same start
        start_apr = q.start_of_quarter("2024-04-01", cal="NYSE")
        start_may = q.start_of_quarter("2024-05-15", cal="NYSE")
        start_jun = q.start_of_quarter("2024-06-30", cal="NYSE")
        assert start_apr.date() == start_may.date() == start_jun.date()

    def test_result_is_business_day(self):
        for month in range(1, 13):
            result = q.start_of_quarter(f"2024-{month:02d}-15", cal="NYSE")
            assert q.is_business_day(result, cal="NYSE") is True


class TestEndOfQuarter:
    def test_q1_2024_ends_mar_28(self):
        # Q1 ends Mar 31 (Sun) → skip to Mar 28 (Thu, because Good Friday is Mar 29)
        assert q.end_of_quarter("2024-01-15", cal="NYSE").date() == date(2024, 3, 28)

    def test_q2_2024_ends_jun_28(self):
        # Q2 ends Jun 30 (Sun) → Jun 28 (Fri)
        assert q.end_of_quarter("2024-04-15", cal="NYSE").date() == date(2024, 6, 28)

    def test_q3_2024_ends_sep_30(self):
        # Q3 ends Sep 30 (Mon), business day
        assert q.end_of_quarter("2024-07-15", cal="NYSE").date() == date(2024, 9, 30)

    def test_q4_2024_ends_dec_31(self):
        # Q4 ends Dec 31 (Tue), business day
        assert q.end_of_quarter("2024-10-15", cal="NYSE").date() == date(2024, 12, 31)

    def test_any_month_in_quarter_gives_same_end(self):
        end_oct = q.end_of_quarter("2024-10-01", cal="NYSE")
        end_nov = q.end_of_quarter("2024-11-15", cal="NYSE")
        end_dec = q.end_of_quarter("2024-12-31", cal="NYSE")
        assert end_oct.date() == end_nov.date() == end_dec.date()

    def test_result_is_business_day(self):
        for month in range(1, 13):
            result = q.end_of_quarter(f"2024-{month:02d}-15", cal="NYSE")
            assert q.is_business_day(result, cal="NYSE") is True

    def test_end_after_start(self):
        for month in range(1, 13):
            val = f"2024-{month:02d}-15"
            start = q.start_of_quarter(val, cal="NYSE")
            end = q.end_of_quarter(val, cal="NYSE")
            assert end.date() > start.date()


class TestStartOfYear:
    def test_2024_starts_jan_2(self):
        # Jan 1 is New Year's Day; first business day is Jan 2
        assert q.start_of_year("2024-06-15", cal="NYSE").date() == date(2024, 1, 2)

    def test_any_date_in_year_gives_same_result(self):
        for month in (1, 6, 12):
            result = q.start_of_year(f"2024-{month:02d}-15", cal="NYSE")
            assert result.date() == date(2024, 1, 2)

    def test_result_is_business_day(self):
        for year in (2022, 2023, 2024, 2025):
            result = q.start_of_year(f"{year}-06-15", cal="NYSE")
            assert q.is_business_day(result, cal="NYSE") is True


class TestEndOfYear:
    def test_2024_ends_dec_31(self):
        # Dec 31, 2024 is a Tuesday — business day
        assert q.end_of_year("2024-06-15", cal="NYSE").date() == date(2024, 12, 31)

    def test_any_date_in_year_gives_same_result(self):
        for month in (1, 6, 12):
            result = q.end_of_year(f"2024-{month:02d}-15", cal="NYSE")
            assert result.date() == date(2024, 12, 31)

    def test_result_is_business_day(self):
        for year in (2022, 2023, 2024, 2025):
            result = q.end_of_year(f"{year}-06-15", cal="NYSE")
            assert q.is_business_day(result, cal="NYSE") is True

    def test_end_after_start(self):
        start = q.start_of_year("2024-06-15", cal="NYSE")
        end = q.end_of_year("2024-06-15", cal="NYSE")
        assert end.date() > start.date()


class TestStartOfWeek:
    def test_wednesday_gives_monday(self):
        # 2024-01-24 is Wednesday; Monday 2024-01-22 is a regular business day
        assert q.start_of_week("2024-01-24", cal="NYSE").date() == date(2024, 1, 22)

    def test_monday_returns_itself_if_business_day(self):
        # 2024-01-22 is a regular Monday (no holiday)
        assert q.start_of_week("2024-01-22", cal="NYSE").date() == date(2024, 1, 22)

    def test_holiday_monday_rolls_forward(self):
        # 2024-01-15 is MLK Day (NYSE closed); week of Jan 15 starts Jan 16 (Tue)
        assert q.start_of_week("2024-01-15", cal="NYSE").date() == date(2024, 1, 16)

    def test_result_is_business_day(self):
        result = q.start_of_week("2024-01-24", cal="NYSE")
        assert q.is_business_day(result, cal="NYSE") is True


class TestEndOfWeek:
    def test_wednesday_gives_friday(self):
        # 2024-01-17 is Wednesday; Friday is 2024-01-19 (business day)
        assert q.end_of_week("2024-01-17", cal="NYSE").date() == date(2024, 1, 19)

    def test_friday_returns_itself_if_business_day(self):
        assert q.end_of_week("2024-01-19", cal="NYSE").date() == date(2024, 1, 19)

    def test_result_is_business_day(self):
        result = q.end_of_week("2024-01-17", cal="NYSE")
        assert q.is_business_day(result, cal="NYSE") is True

    def test_end_after_start(self):
        start = q.start_of_week("2024-01-17", cal="NYSE")
        end = q.end_of_week("2024-01-17", cal="NYSE")
        assert end.date() >= start.date()


class TestIsMonthEnd:
    def test_last_bday_of_jan_2024_is_true(self):
        assert q.is_month_end("2024-01-31", cal="NYSE") is True

    def test_mid_month_is_false(self):
        assert q.is_month_end("2024-01-15", cal="NYSE") is False

    def test_non_last_bday_is_false(self):
        assert q.is_month_end("2024-01-30", cal="NYSE") is False


class TestIsQuarterEnd:
    def test_q1_2024_end_mar_28(self):
        assert q.is_quarter_end("2024-03-28", cal="NYSE") is True

    def test_q4_2024_end_dec_31(self):
        assert q.is_quarter_end("2024-12-31", cal="NYSE") is True

    def test_mid_quarter_is_false(self):
        assert q.is_quarter_end("2024-02-15", cal="NYSE") is False


class TestIsYearEnd:
    def test_dec_31_2024_is_true(self):
        assert q.is_year_end("2024-12-31", cal="NYSE") is True

    def test_mid_year_is_false(self):
        assert q.is_year_end("2024-06-15", cal="NYSE") is False

    def test_last_bday_that_is_not_dec_31_is_true(self):
        # If Dec 31 is not a business day, the prev bday is year end
        # 2022: Dec 31 is Saturday → year end is Dec 30 (Friday)
        assert q.is_year_end("2022-12-30", cal="NYSE") is True
        assert q.is_year_end("2022-12-31", cal="NYSE") is False
