"""Oct 1st-15th is a closed day range in that month, not a month-to-month dash."""
import datetime as dt
from copilot import query as Q


def test_month_day_dash_day():
    expected = (dt.date(2026, 10, 1), dt.date(2026, 10, 15))
    assert Q.parse_window("downtime Oct 1st-15th")[:2] == expected
    assert Q.parse_window("downtime Oct 1st - 15th")[:2] == expected
    assert Q.parse_window("downtime October 1 - 15")[:2] == expected
    assert Q.parse_window("downtime Oct 1st-15th 2026")[:2] == expected


def test_month_to_month_dash_is_unchanged():
    assert Q.parse_window("downtime Oct-Dec 2026")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 12, 31),
    )
