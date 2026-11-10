"""before last month ends at the previous calendar month, not the rolling last-month window."""
import datetime as dt
from copilot import query as Q


def test_before_last_month_is_year_to_end_of_month_before_last():
    # TODAY is 17 Oct 2026, so last calendar month is September; before that is through 31 Aug.
    assert Q.parse_window("downtime before last month")[:2] == (
        dt.date(2026, 1, 1),
        dt.date(2026, 8, 31),
    )


def test_last_month_and_before_this_month_are_unchanged():
    assert Q.parse_window("downtime last month")[:2] == (
        dt.date(2026, 9, 16),
        dt.date(2026, 10, 16),
    )
    assert Q.parse_window("downtime before this month")[:2] == (
        dt.date(2026, 1, 1),
        dt.date(2026, 9, 30),
    )
