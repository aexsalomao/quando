"""
Tests for to_settlement_date, to_cob, next_expiry, days_to_expiry.
"""

from datetime import date, datetime

import pytest

import quando as q


class TestToSettlementDate:
    def test_t_plus_0_returns_same_day(self):
        assert q.to_settlement_date("2024-01-16", "T+0", cal="NYSE").date() == date(2024, 1, 16)

    def test_t_plus_1(self):
        assert q.to_settlement_date("2024-01-16", "T+1", cal="NYSE").date() == date(2024, 1, 17)

    def test_t_plus_2(self):
        assert q.to_settlement_date("2024-01-16", "T+2", cal="NYSE").date() == date(2024, 1, 18)

    def test_t_plus_2_skips_holiday(self):
        # Jun 17 (Mon) + 2 = Jun 19 (Juneteenth holiday) + skip → Jun 20 (Thu)
        assert q.to_settlement_date("2024-06-17", "T+2", cal="NYSE").date() == date(2024, 6, 20)

    def test_t_plus_2_skips_weekend(self):
        # Jan 19 (Fri) + 2: skip Sat, Sun → Jan 23 (Mon), Jan 24 (Tue) — wait
        # Jan 19 (Fri) + 1 bday = Jan 22 (Mon), + 1 more = Jan 23 (Tue)
        assert q.to_settlement_date("2024-01-19", "T+2", cal="NYSE").date() == date(2024, 1, 23)

    def test_t_plus_3(self):
        assert q.to_settlement_date("2024-01-16", "T+3", cal="NYSE").date() == date(2024, 1, 19)

    def test_result_is_business_day(self):
        result = q.to_settlement_date("2024-01-12", "T+2", cal="NYSE")
        assert q.is_business_day(result, cal="NYSE") is True

    def test_case_insensitive_convention(self):
        assert (
            q.to_settlement_date("2024-01-16", "t+2", cal="NYSE").date()
            == q.to_settlement_date("2024-01-16", "T+2", cal="NYSE").date()
        )

    def test_invalid_convention_raises(self):
        with pytest.raises(ValueError, match="quando"):
            q.to_settlement_date("2024-01-16", "T2", cal="NYSE")

    def test_invalid_convention_no_t_raises(self):
        with pytest.raises(ValueError, match="quando"):
            q.to_settlement_date("2024-01-16", "+2", cal="NYSE")

    def test_accepts_all_input_types(self):
        expected = date(2024, 1, 18)
        for value in ("2024-01-16", datetime(2024, 1, 16), date(2024, 1, 16)):
            assert q.to_settlement_date(value, "T+2", cal="NYSE").date() == expected


class TestToCob:
    def test_business_day_returns_itself(self):
        assert q.to_cob("2024-01-16", cal="NYSE").date() == date(2024, 1, 16)

    def test_saturday_rolls_to_friday(self):
        # Jan 13 (Sat) → Jan 12 (Fri)
        assert q.to_cob("2024-01-13", cal="NYSE").date() == date(2024, 1, 12)

    def test_sunday_rolls_to_friday(self):
        # Jan 14 (Sun) → Jan 12 (Fri, via Jan 13 which is Sat)
        assert q.to_cob("2024-01-14", cal="NYSE").date() == date(2024, 1, 12)

    def test_holiday_on_monday_rolls_to_friday(self):
        # Jan 15 (MLK) → Jan 12 (Fri)
        assert q.to_cob("2024-01-15", cal="NYSE").date() == date(2024, 1, 12)

    def test_holiday_on_wednesday_rolls_to_tuesday(self):
        # Jun 19 (Juneteenth, Wed) → Jun 18 (Tue)
        assert q.to_cob("2024-06-19", cal="NYSE").date() == date(2024, 6, 18)

    def test_good_friday_rolls_to_thursday(self):
        # Mar 29 (Good Friday) → Mar 28 (Thu)
        assert q.to_cob("2024-03-29", cal="NYSE").date() == date(2024, 3, 28)

    def test_result_is_always_business_day(self):
        test_dates = [
            "2024-01-13",
            "2024-01-14",
            "2024-01-15",
            "2024-03-29",
            "2024-06-19",
            "2024-07-04",
            "2024-12-25",
        ]
        for d in test_dates:
            result = q.to_cob(d, cal="NYSE")
            assert q.is_business_day(result, cal="NYSE") is True, f"Failed for {d}"

    def test_accepts_all_input_types(self):
        expected = date(2024, 1, 12)
        for value in ("2024-01-13", datetime(2024, 1, 13), date(2024, 1, 13)):
            assert q.to_cob(value, cal="NYSE").date() == expected


class TestNextExpiry:
    # Monthly (third Friday of each month)
    @pytest.mark.parametrize(
        "trade_date, expected_expiry",
        [
            ("2024-01-01", date(2024, 1, 19)),  # before Jan expiry
            ("2024-01-19", date(2024, 2, 16)),  # ON Jan expiry → next is Feb
            ("2024-01-20", date(2024, 2, 16)),  # after Jan expiry
            ("2024-11-15", date(2024, 12, 20)),  # Nov expiry day → Dec
            ("2024-12-20", date(2025, 1, 17)),  # Dec expiry → Jan next year
            ("2024-12-31", date(2025, 1, 17)),  # end of year
        ],
    )
    def test_monthly_expiry(self, trade_date, expected_expiry):
        result = q.next_expiry(trade_date, "monthly")
        assert result.date() == expected_expiry

    # Quarterly (third Friday of Mar, Jun, Sep, Dec)
    @pytest.mark.parametrize(
        "trade_date, expected_expiry",
        [
            ("2024-01-01", date(2024, 3, 15)),  # Q1 expiry
            ("2024-03-15", date(2024, 6, 21)),  # ON Q1 expiry → Q2
            ("2024-03-16", date(2024, 6, 21)),  # after Q1 expiry
            ("2024-06-21", date(2024, 9, 20)),  # ON Q2 → Q3
            ("2024-09-20", date(2024, 12, 20)),  # ON Q3 → Q4
            ("2024-12-20", date(2025, 3, 21)),  # ON Q4 → next year Q1
        ],
    )
    def test_quarterly_expiry(self, trade_date, expected_expiry):
        result = q.next_expiry(trade_date, "quarterly")
        assert result.date() == expected_expiry

    # Weekly (every Friday)
    @pytest.mark.parametrize(
        "trade_date, expected_expiry",
        [
            ("2024-01-01", date(2024, 1, 5)),  # Mon → Fri same week
            ("2024-01-05", date(2024, 1, 12)),  # ON Fri → next Fri
            ("2024-01-06", date(2024, 1, 12)),  # Sat → next Fri
            ("2024-01-07", date(2024, 1, 12)),  # Sun → next Fri
            ("2024-01-11", date(2024, 1, 12)),  # Thu → next day (Fri)
            ("2024-01-12", date(2024, 1, 19)),  # ON Fri → next Fri
        ],
    )
    def test_weekly_expiry(self, trade_date, expected_expiry):
        result = q.next_expiry(trade_date, "weekly")
        assert result.date() == expected_expiry

    def test_result_is_always_a_friday(self):
        for contract in ("monthly", "quarterly", "weekly"):
            result = q.next_expiry("2024-01-10", contract)
            assert result.weekday() == 4, f"{contract} expiry {result.date()} is not a Friday"

    def test_invalid_contract_type_raises(self):
        with pytest.raises(ValueError, match="quando"):
            q.next_expiry("2024-01-10", "daily")

    def test_accepts_all_input_types(self):
        expected = date(2024, 1, 19)
        for value in ("2024-01-10", datetime(2024, 1, 10), date(2024, 1, 10)):
            assert q.next_expiry(value, "monthly").date() == expected


class TestDaysToExpiry:
    def test_zero_when_same_day(self):
        # Exclusive: nothing between a date and itself
        assert q.days_to_expiry("2024-01-19", "2024-01-19", cal="NYSE") == 0

    def test_zero_when_adjacent_business_days(self):
        # Jan 18 (Thu) to Jan 19 (Fri): nothing strictly between them
        assert q.days_to_expiry("2024-01-18", "2024-01-19", cal="NYSE") == 0

    def test_two_days_apart(self):
        # Jan 16 (Tue) to Jan 19 (Fri): 17, 18 = 2 business days
        assert q.days_to_expiry("2024-01-16", "2024-01-19", cal="NYSE") == 2

    def test_across_weekend(self):
        # Jan 19 (Fri) to Jan 23 (Tue): Mon Jan 22 = 1
        assert q.days_to_expiry("2024-01-19", "2024-01-23", cal="NYSE") == 1

    def test_typical_monthly_cycle(self):
        # From Jan 2 to Jan 19 expiry: business days strictly between
        count = q.days_to_expiry("2024-01-02", "2024-01-19", cal="NYSE")
        # Jan 3,4,5,8,9,10,11,12,16,17,18 = 11 (skipping MLK Jan 15)
        assert count == 11

    def test_expiry_before_value_returns_zero(self):
        assert q.days_to_expiry("2024-01-19", "2024-01-10", cal="NYSE") == 0

    def test_accepts_all_input_types(self):
        for v in ("2024-01-16", datetime(2024, 1, 16), date(2024, 1, 16)):
            for e in ("2024-01-19", datetime(2024, 1, 19), date(2024, 1, 19)):
                assert q.days_to_expiry(v, e, cal="NYSE") == 2
