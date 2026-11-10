"""A specific calendar date must not be widened to the whole year it mentions."""
import datetime as dt
from copilot import agent
from copilot import query as Q

DAY = dt.date(2026, 10, 15)


def test_parse_date_accepts_numeric_slash_and_dot_forms():
    assert agent.parse_date("15/10/2026") == DAY
    assert agent.parse_date("10/15/2026") == DAY  # unambiguous US form (day 15)
    assert agent.parse_date("15.10.2026") == DAY
    assert agent.parse_date("15-10-2026") == DAY
    assert agent.parse_date("2026/10/15") == DAY
    assert agent.parse_date("spills on 15/10/2026") == DAY
    assert agent.invalid_date_phrase("15/10/2026") is None
    assert agent.parse_date("31/02/2026") is None
    assert agent.invalid_date_phrase("31/02/2026") == "31/02/2026"
    assert agent.parse_date("2026/02/31") is None


def test_parse_window_on_a_named_or_iso_date_is_that_day_not_the_year():
    assert Q.parse_window("spills on 15 Oct 2026")[:2] == (DAY, DAY)
    assert Q.parse_window("spills on 2026-10-15")[:2] == (DAY, DAY)
    assert Q.parse_window("spills on 15/10/2026")[:2] == (DAY, DAY)
    assert Q.parse_window("spills on October 15, 2026")[:2] == (DAY, DAY)
    # a date sitting in the question without "on" must still not become the whole year
    assert Q.parse_window("spills 15 Oct 2026")[:2] == (DAY, DAY)


def test_parse_window_from_and_between_accept_numeric_dates():
    start, end, _ = Q.parse_window("spills from 15/10/2026")
    assert start == DAY
    assert end == dt.date(2026, 10, 16)
    a, b, _ = Q.parse_window("between 15/10/2026 and 20/10/2026")
    assert (a, b) == (DAY, dt.date(2026, 10, 20))


def test_parse_window_in_year_month_is_that_month_not_the_year():
    assert Q.parse_window("spills in 2026-10")[:2] == (dt.date(2026, 10, 1), dt.date(2026, 10, 16))
    # a bare year is still a year window
    year = Q.parse_window("spills in 2026")
    assert year[:2] == (dt.date(2026, 1, 1), dt.date(2026, 10, 16))
    assert year[2] == "2026"


def test_existing_year_to_date_and_named_month_windows_still_hold():
    assert Q.parse_window("spills year-to-date")[:2] == (dt.date(2026, 1, 1), dt.date(2026, 10, 16))
    assert Q.parse_window("in October 2026")[:2] == (dt.date(2026, 10, 1), dt.date(2026, 10, 16))
    assert Q.parse_window("is it producing right now") is None
