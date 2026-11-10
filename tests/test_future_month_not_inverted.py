"""A future month or quarter must not invert after being capped at yesterday."""
import datetime as dt
from copilot import query as Q

END = dt.date(2026, 10, 16)


def test_in_and_during_december_2026_are_the_whole_month():
    expected = (dt.date(2026, 12, 1), dt.date(2026, 12, 31))
    assert Q.parse_window("downtime in December 2026")[:2] == expected
    assert Q.parse_window("downtime during December 2026")[:2] == expected
    assert Q.parse_window("downtime ending in December 2026")[:2] == expected


def test_future_quarter_and_half_month_are_not_inverted():
    assert Q.parse_window("downtime in Q1 2027")[:2] == (dt.date(2027, 1, 1), dt.date(2027, 3, 31))
    assert Q.parse_window("downtime first half of December 2026")[:2] == (
        dt.date(2026, 12, 1),
        dt.date(2026, 12, 15),
    )


def test_current_and_past_windows_are_still_capped_at_yesterday():
    assert Q.parse_window("downtime in October 2026")[:2] == (dt.date(2026, 10, 1), END)
    assert Q.parse_window("downtime Q4 2026")[:2] == (dt.date(2026, 10, 1), END)
    assert Q.parse_window("downtime second half of 2026")[:2] == (dt.date(2026, 7, 1), END)
    assert Q.parse_window("spills in 2026")[:2] == (dt.date(2026, 1, 1), END)
