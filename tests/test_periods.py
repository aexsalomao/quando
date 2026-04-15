"""
Tests for start_of_month, end_of_month, start_of_quarter, end_of_quarter.
All expected values verified against 2024 NYSE calendar.
"""
from datetime import date
import pytest
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
            end   = q.end_of_month(val, cal="NYSE")
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
            end   = q.end_of_quarter(val, cal="NYSE")
            assert end.date() > start.date()
