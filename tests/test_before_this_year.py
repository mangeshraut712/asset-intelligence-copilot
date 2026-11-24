"""before this year is the previous calendar year, not year-to-date."""
import datetime as dt
from copilot import query as Q


def test_before_this_year_is_the_previous_calendar_year():
    assert Q.parse_window("downtime before this year")[:2] == (
        dt.date(2025, 1, 1),
        dt.date(2025, 12, 31),
    )


def test_this_year_and_ytd_are_unchanged():
    expected = (dt.date(2026, 1, 1), dt.date(2026, 10, 16))
    assert Q.parse_window("downtime this year")[:2] == expected
    assert Q.parse_window("downtime year to date")[:2] == expected


def test_before_last_year_is_the_year_before_last():
    assert Q.parse_window("how many spills happened before last year?")[:2] == (
        dt.date(2024, 1, 1),
        dt.date(2024, 12, 31),
    )
    assert Q.parse_window("spills last year")[:2] == (dt.date(2025, 1, 1), dt.date(2025, 12, 31))
