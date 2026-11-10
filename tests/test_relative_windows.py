"""Relative windows: today, yesterday, this week, and month-to-date."""
import datetime as dt
from copilot import query as Q

TODAY = dt.date(2026, 10, 17)
YESTERDAY = dt.date(2026, 10, 16)
WEEK_START = dt.date(2026, 10, 12)  # Monday


def test_today_and_yesterday_are_single_day_windows():
    assert Q.parse_window("spills today")[:2] == (TODAY, TODAY)
    assert Q.parse_window("spills yesterday")[:2] == (YESTERDAY, YESTERDAY)
    assert Q.parse_window("year-to-date")[:2] == (dt.date(2026, 1, 1), YESTERDAY)


def test_this_week_and_week_to_date_run_monday_through_yesterday():
    assert Q.parse_window("spills this week")[:2] == (WEEK_START, YESTERDAY)
    assert Q.parse_window("week-to-date downtime")[:2] == (WEEK_START, YESTERDAY)
    assert Q.parse_window("week–to–date downtime")[:2] == (WEEK_START, YESTERDAY)


def test_month_to_date_matches_this_month():
    expected = (dt.date(2026, 10, 1), YESTERDAY)
    assert Q.parse_window("this month spills")[:2] == expected
    assert Q.parse_window("month-to-date spills")[:2] == expected
    assert Q.parse_window("month to date spills")[:2] == expected
