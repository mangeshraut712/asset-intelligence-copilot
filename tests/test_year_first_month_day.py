"""Regression: the day-first date regex must not tear digits off a 4-digit year.
'2026 Oct 15' used to match '26 Oct' and silently answer for 26 October."""
import datetime as dt
from copilot.agent import parse_date, invalid_date_phrase


def test_year_first_month_day_keeps_the_written_day():
    d = parse_date("How much did WELL-0001 produce on 2026 Oct 15?")
    assert d is not None and (d.month, d.day) == (10, 15)


def test_year_first_full_month_name_keeps_the_written_day():
    d = parse_date("spills on 2026 October 15")
    assert d is not None and (d.month, d.day) == (10, 15)


def test_year_before_bare_month_is_not_a_day():
    # Used to parse as 26 Oct (digits stolen from the year); a bare month is not a date.
    assert parse_date("Show spills for 2026 Oct") is None


def test_impossible_day_after_year_first_is_flagged():
    # Used to parse as a valid 26 Feb, hiding the impossible date the user wrote.
    assert invalid_date_phrase("leak started 2026 Feb 30") == "2026 Feb 30"


def test_day_first_with_explicit_year_unchanged():
    assert parse_date("between 15 Oct 2026 and 31 Dec 2026") == dt.date(2026, 10, 15)


def test_year_first_keeps_the_written_year():
    # Used to drop "2025" and resolve against the dataset clock, so a correction
    # for "2025 Oct 1" was saved against the 2026 inspection.
    assert parse_date("The 2025 Oct 1 reading for WELL-0001 is wrong") == dt.date(2025, 10, 1)


def test_year_first_leap_day_uses_the_written_year():
    assert parse_date("spills on 2024 Feb 29") == dt.date(2024, 2, 29)
    assert invalid_date_phrase("spills on 2024 Feb 29") is None
    assert invalid_date_phrase("spills on 2025 Feb 29") == "2025 Feb 29"
