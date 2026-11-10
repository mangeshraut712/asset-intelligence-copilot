"""previous/prior should mean the same as last for month, week, quarter and year."""
import datetime as dt
from copilot import query as Q

YESTERDAY = dt.date(2026, 10, 16)
LAST_MONTH = (dt.date(2026, 9, 16), YESTERDAY)
LAST_WEEK = (dt.date(2026, 10, 10), YESTERDAY)
LAST_YEAR = (dt.date(2025, 1, 1), dt.date(2025, 12, 31))


def test_previous_and_prior_month_match_last_month():
    expected = Q.parse_window("downtime last month")[:2]
    assert expected == LAST_MONTH
    assert Q.parse_window("downtime previous month")[:2] == expected
    assert Q.parse_window("downtime prior month")[:2] == expected
    assert Q.parse_window("downtime past month")[:2] == expected


def test_prior_week_matches_last_and_previous_week():
    expected = Q.parse_window("downtime last week")[:2]
    assert expected == LAST_WEEK
    assert Q.parse_window("downtime previous week")[:2] == expected
    assert Q.parse_window("downtime prior week")[:2] == expected


def test_previous_and_prior_year_are_the_last_calendar_year():
    assert Q.parse_window("downtime last year")[:2] == LAST_YEAR
    assert Q.parse_window("downtime previous year")[:2] == LAST_YEAR
    assert Q.parse_window("downtime prior year")[:2] == LAST_YEAR


def test_prior_quarter_matches_last_quarter():
    expected = Q.parse_window("downtime last quarter")[:2]
    assert Q.parse_window("downtime previous quarter")[:2] == expected
    assert Q.parse_window("downtime prior quarter")[:2] == expected
