"""between October and December (no year) should still be a month-to-month window."""
import datetime as dt
from copilot import query as Q


def test_between_bare_month_names_uses_this_year_and_the_whole_end_month():
    assert Q.parse_window("downtime between October and December")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 12, 31),
    )
    assert Q.parse_window("downtime between Oct and Dec")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 12, 31),
    )
    assert Q.parse_window("downtime between January and March")[:2] == (
        dt.date(2026, 1, 1),
        dt.date(2026, 3, 31),
    )


def test_between_bare_months_rolls_the_end_into_next_year_when_it_precedes_the_start():
    assert Q.parse_window("downtime between November and February")[:2] == (
        dt.date(2026, 11, 1),
        dt.date(2027, 2, 28),
    )


def test_between_month_years_and_explicit_days_still_work():
    expected = (dt.date(2026, 10, 1), dt.date(2026, 12, 31))
    assert Q.parse_window("downtime between October 2026 and December 2026")[:2] == expected
    assert Q.parse_window("downtime between 1 Oct 2026 and 31 Dec 2026")[:2] == expected
