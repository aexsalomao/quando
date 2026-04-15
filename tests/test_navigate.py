"""
Tests for next_business_day, prev_business_day, add_business_days, snap.
All results are verified against the 2024 NYSE holiday schedule.
"""
from datetime import date, datetime, timezone
import pytest
import quando as q

UTC = timezone.utc


class TestNextBusinessDay:
    def test_friday_skips_weekend_to_monday(self):
        # Jan 12 (Fri) → Jan 16 (Tue): skips Sat, Sun, AND MLK Monday Jan 15
        assert q.next_business_day("2024-01-12", cal="NYSE").date() == date(2024, 1, 16)

    def test_plain_friday_skips_to_monday(self):
        # Mar 28 (Thu) → Apr 1 (Mon): skip Good Friday + weekend
        assert q.next_business_day("2024-03-28", cal="NYSE").date() == date(2024, 4, 1)

    def test_holiday_skips_to_next_business_day(self):
        # Dec 25 (Wed holiday) → Dec 26 (Thu)
        assert q.next_business_day("2024-12-25", cal="NYSE").date() == date(2024, 12, 26)

    def test_regular_weekday_advances_one(self):
        # Jan 16 (Tue) → Jan 17 (Wed)
        assert q.next_business_day("2024-01-16", cal="NYSE").date() == date(2024, 1, 17)

    def test_before_christmas_skips_holiday(self):
        # Dec 24 (Tue) → Dec 26 (Thu, skipping Christmas)
        assert q.next_business_day("2024-12-24", cal="NYSE").date() == date(2024, 12, 26)

    def test_returns_datetime(self):
        result = q.next_business_day("2024-01-15", cal="NYSE")
        assert isinstance(result, datetime)

    def test_result_is_business_day(self):
        result = q.next_business_day("2024-01-12", cal="NYSE")
        assert q.is_business_day(result, cal="NYSE") is True

    def test_accepts_all_input_types(self):
        expected = date(2024, 1, 16)
        for value in ("2024-01-15", datetime(2024, 1, 15), date(2024, 1, 15)):
            assert q.next_business_day(value, cal="NYSE").date() == expected

    def test_year_boundary(self):
        # Dec 31, 2024 (Tue) → Jan 2, 2025 (Thu, skipping Jan 1 holiday)
        result = q.next_business_day("2024-12-31", cal="NYSE")
        assert result.date() == date(2025, 1, 2)


class TestPrevBusinessDay:
    def test_monday_skips_weekend_to_friday(self):
        # Jan 16 (Tue) → Jan 15 would be MLK, so Jan 12 (Fri)
        # Wait: prev of Jan 16 = Jan 15 (holiday) → Jan 12 (Fri)
        assert q.prev_business_day("2024-01-16", cal="NYSE").date() == date(2024, 1, 12)

    def test_holiday_rolls_back(self):
        # Jan 15 (MLK holiday) → Jan 12 (Fri)
        assert q.prev_business_day("2024-01-15", cal="NYSE").date() == date(2024, 1, 12)

    def test_monday_after_normal_weekend(self):
        # Jan 22 (Mon) → Jan 19 (Fri)
        assert q.prev_business_day("2024-01-22", cal="NYSE").date() == date(2024, 1, 19)

    def test_good_friday_rolls_back_to_thursday(self):
        # Mar 29 (Good Friday holiday) → Mar 28 (Thu)
        assert q.prev_business_day("2024-03-29", cal="NYSE").date() == date(2024, 3, 28)

    def test_saturday_rolls_back_to_friday(self):
        # Jan 13 (Sat) → Jan 12 (Fri)
        assert q.prev_business_day("2024-01-13", cal="NYSE").date() == date(2024, 1, 12)

    def test_sunday_rolls_back_to_friday(self):
        # Jan 14 (Sun) → Jan 12 (Fri, because Jan 13 is Sat)
        assert q.prev_business_day("2024-01-14", cal="NYSE").date() == date(2024, 1, 12)

    def test_returns_datetime(self):
        assert isinstance(q.prev_business_day("2024-01-16", cal="NYSE"), datetime)

    def test_result_is_business_day(self):
        result = q.prev_business_day("2024-01-16", cal="NYSE")
        assert q.is_business_day(result, cal="NYSE") is True

    def test_year_boundary(self):
        # Jan 1, 2025 (Wed, holiday) → Dec 31, 2024 (Tue)
        result = q.prev_business_day("2025-01-01", cal="NYSE")
        assert result.date() == date(2024, 12, 31)


class TestAddBusinessDays:
    def test_add_zero_returns_same(self):
        result = q.add_business_days("2024-01-16", 0, cal="NYSE")
        assert result.date() == date(2024, 1, 16)

    def test_add_one(self):
        assert q.add_business_days("2024-01-16", 1, cal="NYSE").date() == date(2024, 1, 17)

    def test_add_skips_weekend(self):
        # Jan 19 (Fri) + 1 = Jan 22 (Mon)
        assert q.add_business_days("2024-01-19", 1, cal="NYSE").date() == date(2024, 1, 22)

    def test_add_skips_holiday(self):
        # Jan 12 (Fri) + 1 = Jan 16 (Tue, skipping MLK Mon)
        assert q.add_business_days("2024-01-12", 1, cal="NYSE").date() == date(2024, 1, 16)

    def test_add_five_business_days(self):
        # Jan 10 (Wed) + 5: 11, 12, [skip Sat/Sun/MLK Mon], 16, 17, 18 → Jan 18
        assert q.add_business_days("2024-01-10", 5, cal="NYSE").date() == date(2024, 1, 18)

    def test_subtract_one(self):
        assert q.add_business_days("2024-01-17", -1, cal="NYSE").date() == date(2024, 1, 16)

    def test_subtract_skips_holiday(self):
        # Jan 16 (Tue) - 1 = Jan 12 (Fri, skips MLK Mon Jan 15)
        assert q.add_business_days("2024-01-16", -1, cal="NYSE").date() == date(2024, 1, 12)

    def test_subtract_five(self):
        # Jan 17 (Wed) - 5: 16, [skip MLK Mon/Sun/Sat], 12, 11, 10, 9 → Jan 9
        assert q.add_business_days("2024-01-17", -5, cal="NYSE").date() == date(2024, 1, 9)

    def test_large_n(self):
        # Jan 2 + 252 business days should be approximately end of year
        result = q.add_business_days("2024-01-02", 252, cal="NYSE")
        assert result.date().year == 2025

    def test_result_is_always_business_day(self):
        for n in range(-10, 11):
            if n == 0:
                continue
            result = q.add_business_days("2024-01-15", n, cal="NYSE")
            assert q.is_business_day(result, cal="NYSE") is True

    def test_add_n_then_subtract_n_is_identity(self):
        start = "2024-06-10"
        for n in (1, 5, 10, 20):
            forward = q.add_business_days(start, n, cal="NYSE")
            back = q.add_business_days(forward, -n, cal="NYSE")
            assert back.date() == date(2024, 6, 10)


class TestSnap:
    def test_business_day_returns_itself(self):
        assert q.snap("2024-01-16", "forward", cal="NYSE").date() == date(2024, 1, 16)
        assert q.snap("2024-01-16", "backward", cal="NYSE").date() == date(2024, 1, 16)
        assert q.snap("2024-01-16", "nearest", cal="NYSE").date() == date(2024, 1, 16)

    def test_saturday_forward(self):
        # Jan 13 (Sat): forward → Jan 16 (Tue, because Jan 15 is MLK)
        assert q.snap("2024-01-13", "forward", cal="NYSE").date() == date(2024, 1, 16)

    def test_saturday_backward(self):
        # Jan 13 (Sat): backward → Jan 12 (Fri)
        assert q.snap("2024-01-13", "backward", cal="NYSE").date() == date(2024, 1, 12)

    def test_saturday_nearest_picks_closer(self):
        # Jan 13 (Sat): backward Jan 12 is 1 day away, forward Jan 16 is 3 days
        assert q.snap("2024-01-13", "nearest", cal="NYSE").date() == date(2024, 1, 12)

    def test_sunday_nearest_picks_closer(self):
        # Jan 14 (Sun): forward Jan 16 is 2 days, backward Jan 12 is 2 days
        # tie breaks to backward per implementation (bwd_delta <= fwd_delta)
        result = q.snap("2024-01-14", "nearest", cal="NYSE")
        assert result.date() in (date(2024, 1, 12), date(2024, 1, 16))

    def test_holiday_forward(self):
        # Jan 15 (MLK): forward → Jan 16
        assert q.snap("2024-01-15", "forward", cal="NYSE").date() == date(2024, 1, 16)

    def test_holiday_backward(self):
        # Jan 15 (MLK): backward → Jan 12 (Fri)
        assert q.snap("2024-01-15", "backward", cal="NYSE").date() == date(2024, 1, 12)

    def test_invalid_direction_raises(self):
        with pytest.raises(ValueError, match="quando"):
            q.snap("2024-01-13", "sideways", cal="NYSE")

    def test_result_is_always_business_day(self):
        for direction in ("forward", "backward", "nearest"):
            result = q.snap("2024-01-13", direction, cal="NYSE")
            assert q.is_business_day(result, cal="NYSE") is True
