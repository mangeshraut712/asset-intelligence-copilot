"""after last year is this year to date, not the previous calendar year."""
import datetime as dt
from copilot import query as Q


def test_after_last_year_is_this_year_to_date():
    assert Q.parse_window("downtime after last year")[:2] == (
        dt.date(2026, 1, 1),
        dt.date(2026, 10, 16),
    )


def test_last_year_is_unchanged():
    assert Q.parse_window("downtime last year")[:2] == (
        dt.date(2025, 1, 1),
        dt.date(2025, 12, 31),
    )
