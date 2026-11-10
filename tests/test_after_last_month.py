"""after last month is this month, not the rolling last-month window."""
import datetime as dt
from copilot import query as Q


def test_after_last_month_is_this_month():
    this_month = (dt.date(2026, 10, 1), dt.date(2026, 10, 16))
    assert Q.parse_window("downtime after last month")[:2] == this_month
    assert Q.parse_window("downtime this month")[:2] == this_month


def test_last_month_is_unchanged():
    # Rolling 1-month window ending yesterday, not calendar September.
    assert Q.parse_window("downtime last month")[:2] == (
        dt.date(2026, 9, 16),
        dt.date(2026, 10, 16),
    )
