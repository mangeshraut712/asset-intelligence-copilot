"""October 1 through 15, 2026 is a closed day range, not only 1 Oct."""
import datetime as dt
from copilot import query as Q


def test_month_day_through_day():
    expected = (dt.date(2026, 10, 1), dt.date(2026, 10, 15))
    assert Q.parse_window("downtime October 1 through 15, 2026")[:2] == expected
    assert Q.parse_window("downtime October 1 through 15 2026")[:2] == expected
    assert Q.parse_window("downtime Oct 1 to 15, 2026")[:2] == expected
    assert Q.parse_window("downtime October 1 until 15")[:2] == expected


def test_existing_day_and_month_ranges_are_unchanged():
    assert Q.parse_window("downtime 1st through 15th October")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 10, 15),
    )
    assert Q.parse_window("downtime Oct 1st-15th 2026")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 10, 15),
    )
    assert Q.parse_window("downtime through December 2026")[:2] == (
        dt.date(2026, 12, 1),
        dt.date(2026, 12, 31),
    )
