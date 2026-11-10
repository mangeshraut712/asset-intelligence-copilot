"""15th of October 2026 is that day, not the whole of October."""
import datetime as dt
from copilot import query as Q


def test_day_of_month():
    expected = (dt.date(2026, 10, 15), dt.date(2026, 10, 15))
    assert Q.parse_window("downtime 15th of October 2026")[:2] == expected
    assert Q.parse_window("downtime on the 15th of October 2026")[:2] == expected
    assert Q.parse_window("downtime the 15th of October")[:2] == expected
    assert Q.parse_window("downtime 15th of Oct 2026")[:2] == expected


def test_half_of_month_and_on_date_are_unchanged():
    assert Q.parse_window("downtime first half of October 2026")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 10, 15),
    )
    assert Q.parse_window("spills on 15 Oct 2026")[:2] == (
        dt.date(2026, 10, 15),
        dt.date(2026, 10, 15),
    )
    assert Q.parse_window("downtime in October 2026")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 10, 16),
    )
