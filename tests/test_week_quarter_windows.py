"""Unnumbered last-week and this/last-quarter windows must parse like the existing numbered forms."""
import datetime as dt
from copilot import query as Q

YESTERDAY = dt.date(2026, 10, 16)
LAST_WEEK = (dt.date(2026, 10, 10), YESTERDAY)
THIS_QUARTER = (dt.date(2026, 10, 1), YESTERDAY)
LAST_QUARTER = (dt.date(2026, 7, 1), dt.date(2026, 9, 30))


def test_last_week_matches_last_one_week():
    expected = LAST_WEEK
    assert Q.parse_window("downtime last week")[:2] == expected
    assert Q.parse_window("downtime past week")[:2] == expected
    assert Q.parse_window("downtime previous week")[:2] == expected
    assert Q.parse_window("downtime last 1 week")[:2] == expected


def test_this_quarter_and_quarter_to_date():
    expected = THIS_QUARTER
    assert Q.parse_window("downtime this quarter")[:2] == expected
    assert Q.parse_window("quarter-to-date downtime")[:2] == expected
    assert Q.parse_window("quarter to date downtime")[:2] == expected
    assert Q.parse_window("quarter–to–date downtime")[:2] == expected
    assert Q.parse_window("qtd downtime")[:2] == expected


def test_last_quarter_is_the_previous_calendar_quarter():
    expected = LAST_QUARTER
    assert Q.parse_window("downtime last quarter")[:2] == expected
    assert Q.parse_window("downtime past quarter")[:2] == expected
    assert Q.parse_window("downtime previous quarter")[:2] == expected
