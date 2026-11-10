"""A month followed by a 4-digit year must not be read as day 20 of that month."""
import datetime as dt
from copilot import query as Q

END = dt.date(2026, 10, 16)  # yesterday relative to TODAY


def test_month_year_is_not_day_twenty_of_that_month():
    assert Q.parse_window("until December 2026")[:2] == (dt.date(2026, 12, 1), dt.date(2026, 12, 31))
    assert Q.parse_window("through December 2026")[:2] == (dt.date(2026, 12, 1), dt.date(2026, 12, 31))
    assert Q.parse_window("October–December 2026")[:2] == (dt.date(2026, 10, 1), dt.date(2026, 12, 31))
    assert Q.parse_window("in early October 2026")[:2] == (dt.date(2026, 10, 1), END)
    assert Q.parse_window("in late October 2026")[:2] == (dt.date(2026, 10, 1), END)
    assert Q.parse_window("mid-October 2026")[:2] == (dt.date(2026, 10, 1), END)


def test_a_specific_day_is_still_that_day():
    assert Q.parse_window("spills on 15 Oct 2026")[:2] == (dt.date(2026, 10, 15), dt.date(2026, 10, 15))
    assert Q.parse_window("spills on October 15, 2026")[:2] == (dt.date(2026, 10, 15), dt.date(2026, 10, 15))
    assert Q.parse_window("spills on October 20 2026")[:2] == (dt.date(2026, 10, 20), dt.date(2026, 10, 20))
    assert Q._date("october 20") == dt.date(2026, 10, 20)
    assert Q._date("December 2026") == dt.date(2026, 12, 1)


def test_in_month_year_and_bare_year_still_hold():
    assert Q.parse_window("in October 2026")[:2] == (dt.date(2026, 10, 1), END)
    assert Q.parse_window("spills in 2026")[:2] == (dt.date(2026, 1, 1), END)
