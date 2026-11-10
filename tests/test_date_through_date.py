"""15 Oct through 20 Oct 2026 is a closed range, not only the start day."""
import datetime as dt
from copilot import query as Q


def test_date_through_date():
    expected = (dt.date(2026, 10, 15), dt.date(2026, 10, 20))
    assert Q.parse_window("downtime 15 Oct through 20 Oct 2026")[:2] == expected
    assert Q.parse_window("downtime 15 October to 20 October 2026")[:2] == expected
    assert Q.parse_window("downtime 15 Oct until 20 Oct 2026")[:2] == expected


def test_from_and_single_day_are_unchanged():
    assert Q.parse_window("downtime from 15 Oct 2026 to 20 Oct 2026")[:2] == (
        dt.date(2026, 10, 15),
        dt.date(2026, 10, 20),
    )
    assert Q.parse_window("spills on 15 Oct 2026")[:2] == (dt.date(2026, 10, 15), dt.date(2026, 10, 15))
