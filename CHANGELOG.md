# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `start_of_year()` / `end_of_year()` — first/last business day of the year
- `start_of_week()` / `end_of_week()` — first/last business day of the ISO week
- `is_month_end()` / `is_quarter_end()` / `is_year_end()` — rebalancing triggers
- All module-level imports moved to top of file (lazy-import pattern removed; no circular deps exist)
- `_WEST_EPOCH` unified in `_parse.py`; `_convert.py` imports it directly
- Ruff linting + formatting (`pyproject.toml [tool.ruff]`)
- Mypy type checking (`pyproject.toml [tool.mypy]`)
- Pre-commit hooks (`.pre-commit-config.yaml`)
- GitHub Actions CI workflow (lint → format → test → coverage upload)
- GitHub Actions docs workflow (MkDocs → GitHub Pages on push to master)
- MkDocs documentation site (`mkdocs.yml`, `docs/`)
- MIT `LICENSE` file
- `CONTRIBUTING.md`
- `example.py` — runnable walkthrough of all major API categories

## [0.1.0] - 2026-04-16

### Added
- Initial release
- 42 public methods across 13 categories
- `_parse.py` — universal input detection (string, datetime, date, int/float, West serial)
- `_state.py` — global calendar state (`use()`, `verbose()`, `as_of()`)
- `_calendar.py` — holiday data via `exchange-calendars` with LRU cache and custom overrides
- `_checks.py` — `is_weekend`, `is_holiday`, `is_business_day`, `is_expiry_day`, `day_of_week`
- `_convert.py` — `to_timestamp`, `to_datetime`, `to_west`, `to_iso`, `convert`, batch ops
- `_timezone.py` — `shift_tz`, `localize`, `strip_tz`
- `_validate.py` — `is_valid`, `is_same_day`, `is_before`, `is_after`
- `_navigate.py` — `next/prev_business_day`, `add_business_days`, `snap`
- `_ranges.py` — `business_days_between`, `date_range`, `trading_days_in_month/year`, `filter_business_days`
- `_periods.py` — `start/end_of_month`, `start/end_of_quarter`
- `_settlement.py` — `to_settlement_date`, `to_cob`, `next_expiry`, `days_to_expiry`
- `_io.py` — `load_calendar`, `save_calendar`
- 447 tests across all modules
