"""A bare month on one end of a between-range must cross the year correctly."""
import datetime as dt
from copilot import query as Q

NOV_JAN = (dt.date(2026, 11, 1), dt.date(2027, 1, 31))


def test_bare_start_month_crosses_into_the_end_year():
    assert Q.parse_window("downtime between Nov and Jan 2027")[:2] == NOV_JAN
    assert Q.parse_window("downtime between November and January 2027")[:2] == NOV_JAN


def test_bare_end_month_crosses_out_of_the_start_year():
    assert Q.parse_window("downtime between November 2026 and January")[:2] == NOV_JAN
    assert Q.parse_window("downtime between Nov 2026 and Jan")[:2] == NOV_JAN


def test_same_year_and_explicit_years_are_unchanged():
    assert Q.parse_window("downtime between January and March 2027")[:2] == (
        dt.date(2027, 1, 1),
        dt.date(2027, 3, 31),
    )
    assert Q.parse_window("downtime between Nov 2026 and Jan 2027")[:2] == NOV_JAN
    assert Q.parse_window("downtime between October and December 2026")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 12, 31),
    )
    # both bare, no year: already wraps using TODAY.year
    assert Q.parse_window("downtime between December and January")[:2] == (
        dt.date(2026, 12, 1),
        dt.date(2027, 1, 31),
    )
