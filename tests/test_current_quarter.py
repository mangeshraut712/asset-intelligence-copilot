"""current quarter is the same quarter-to-date window as this quarter."""
import datetime as dt
from copilot import query as Q


def test_current_quarter_matches_this_quarter():
    expected = Q.parse_window("downtime this quarter")[:2]
    assert expected == (dt.date(2026, 10, 1), dt.date(2026, 10, 16))
    assert Q.parse_window("downtime current quarter")[:2] == expected
    assert Q.parse_window("downtime qtd")[:2] == expected


def test_last_quarter_is_unchanged():
    assert Q.parse_window("downtime last quarter")[:2] == (
        dt.date(2026, 7, 1),
        dt.date(2026, 9, 30),
    )
