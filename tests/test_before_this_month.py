"""before this month ends on the last day of the previous month, not MTD."""
import datetime as dt
from copilot import query as Q


def test_before_this_month_is_year_to_end_of_last_month():
    assert Q.parse_window("downtime before this month")[:2] == (
        dt.date(2026, 1, 1),
        dt.date(2026, 9, 30),
    )


def test_this_month_and_mtd_are_unchanged():
    this_month = (dt.date(2026, 10, 1), dt.date(2026, 10, 16))
    assert Q.parse_window("downtime this month")[:2] == this_month
    assert Q.parse_window("downtime MTD")[:2] == this_month
