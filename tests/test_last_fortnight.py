"""last fortnight is the same 14-day window as last two weeks."""
import datetime as dt
from copilot import query as Q

FORTNIGHT = (dt.date(2026, 10, 3), dt.date(2026, 10, 16))


def test_last_fortnight_matches_last_two_weeks():
    expected = Q.parse_window("downtime last two weeks")[:2]
    assert expected == FORTNIGHT
    assert Q.parse_window("downtime last 2 weeks")[:2] == expected
    assert Q.parse_window("downtime last fortnight")[:2] == expected
    assert Q.parse_window("downtime past fortnight")[:2] == expected
    assert Q.parse_window("downtime previous fortnight")[:2] == expected
    assert Q.parse_window("downtime prior fortnight")[:2] == expected


def test_last_week_is_unchanged():
    assert Q.parse_window("downtime last week")[:2] == (dt.date(2026, 10, 10), dt.date(2026, 10, 16))
