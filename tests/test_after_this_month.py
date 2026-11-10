"""after this month is the rest of the year, not month-to-date."""
import datetime as dt
from copilot import query as Q


def test_after_this_month_is_the_rest_of_the_year():
    assert Q.parse_window("downtime after this month")[:2] == (
        dt.date(2026, 11, 1),
        dt.date(2026, 12, 31),
    )


def test_this_month_and_after_last_month_are_unchanged():
    assert Q.parse_window("downtime this month")[:2] == (dt.date(2026, 10, 1), dt.date(2026, 10, 16))
    assert Q.parse_window("downtime after last month")[:2] == (dt.date(2026, 10, 1), dt.date(2026, 10, 16))
