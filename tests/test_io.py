"""Tests for load_calendar and save_calendar."""
import json
import os
from datetime import date
import pytest
import quando as q
import quando._state as _state
import quando._calendar as _cal


@pytest.fixture
def tmp_path_custom(tmp_path):
    return tmp_path / "cal.json"


class TestSaveCalendar:
    def test_creates_file(self, tmp_path_custom):
        q.save_calendar(str(tmp_path_custom), cal="NYSE")
        assert tmp_path_custom.exists()

    def test_output_is_valid_json(self, tmp_path_custom):
        q.save_calendar(str(tmp_path_custom), cal="NYSE")
        with open(tmp_path_custom) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_schema_has_name_and_holidays(self, tmp_path_custom):
        q.save_calendar(str(tmp_path_custom), cal="NYSE")
        with open(tmp_path_custom) as f:
            data = json.load(f)
        assert "name" in data
        assert "holidays" in data
        assert data["name"] == "NYSE"

    def test_empty_custom_holidays(self, tmp_path_custom):
        # No custom holidays added; save should produce empty list
        q.save_calendar(str(tmp_path_custom), cal="NYSE")
        with open(tmp_path_custom) as f:
            data = json.load(f)
        assert data["holidays"] == []

    def test_saves_custom_holidays(self, tmp_path_custom):
        q.add_holiday("2024-04-10", "Custom A", cal="NYSE")
        q.add_holiday("2024-05-20", "Custom B", cal="NYSE")
        q.save_calendar(str(tmp_path_custom), cal="NYSE")
        with open(tmp_path_custom) as f:
            data = json.load(f)
        saved_dates = [h["date"] for h in data["holidays"]]
        assert "2024-04-10" in saved_dates
        assert "2024-05-20" in saved_dates

    def test_holidays_are_sorted(self, tmp_path_custom):
        q.add_holiday("2024-06-01", "Later", cal="NYSE")
        q.add_holiday("2024-01-15", "Earlier", cal="NYSE")
        q.save_calendar(str(tmp_path_custom), cal="NYSE")
        with open(tmp_path_custom) as f:
            data = json.load(f)
        dates = [h["date"] for h in data["holidays"]]
        assert dates == sorted(dates)

    def test_uses_global_calendar_when_cal_omitted(self, tmp_path_custom):
        q.use("EUREX")
        q.add_holiday("2024-04-10", "Test", cal="EUREX")
        q.save_calendar(str(tmp_path_custom))
        with open(tmp_path_custom) as f:
            data = json.load(f)
        assert data["name"] == "EUREX"


class TestLoadCalendar:
    def _write_cal(self, path, name, holidays):
        data = {
            "name": name,
            "holidays": [{"date": d, "name": n} for d, n in holidays],
        }
        with open(path, "w") as f:
            json.dump(data, f)

    def test_sets_active_calendar(self, tmp_path):
        path = str(tmp_path / "cal.json")
        self._write_cal(path, "MY_CAL", [])
        q.load_calendar(path)
        assert _state._GLOBAL_CAL == "MY_CAL"

    def test_custom_holidays_become_active(self, tmp_path):
        path = str(tmp_path / "cal.json")
        self._write_cal(path, "MY_CAL", [("2024-04-10", "Custom Day")])
        q.load_calendar(path)
        assert q.is_holiday("2024-04-10", cal="MY_CAL") is True

    def test_loaded_holidays_make_days_non_business(self, tmp_path):
        path = str(tmp_path / "cal.json")
        self._write_cal(path, "MY_CAL", [("2024-04-10", "Custom Day")])
        q.load_calendar(path)
        assert q.is_business_day("2024-04-10", cal="MY_CAL") is False

    def test_multiple_holidays_loaded(self, tmp_path):
        path = str(tmp_path / "cal.json")
        self._write_cal(path, "MY_CAL", [
            ("2024-04-10", "Day A"),
            ("2024-05-15", "Day B"),
            ("2024-08-20", "Day C"),
        ])
        q.load_calendar(path)
        assert q.is_holiday("2024-04-10", cal="MY_CAL") is True
        assert q.is_holiday("2024-05-15", cal="MY_CAL") is True
        assert q.is_holiday("2024-08-20", cal="MY_CAL") is True

    def test_nonexistent_file_raises(self):
        with pytest.raises((FileNotFoundError, OSError)):
            q.load_calendar("/nonexistent/path/cal.json")

    def test_round_trip_save_then_load(self, tmp_path):
        path = str(tmp_path / "cal.json")
        q.add_holiday("2024-04-10", "Custom Day", cal="NYSE")
        q.save_calendar(path, cal="NYSE")

        # Reset calendar state, then reload
        _cal._CUSTOM_ADD.clear()
        _cal._xcal_holidays.cache_clear()
        assert q.is_holiday("2024-04-10", cal="NYSE") is False

        q.load_calendar(path)
        assert q.is_holiday("2024-04-10", cal="NYSE") is True
