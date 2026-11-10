"""October–December 2026 is a month range, not only December."""
import datetime as dt
from copilot import query as Q

OCT_DEC = (dt.date(2026, 10, 1), dt.date(2026, 12, 31))
NOV_JAN = (dt.date(2026, 11, 1), dt.date(2027, 1, 31))


def test_month_dash_month_year_is_a_closed_range():
    assert Q.parse_window("downtime October–December 2026")[:2] == OCT_DEC
    assert Q.parse_window("downtime October-December 2026")[:2] == OCT_DEC
    assert Q.parse_window("downtime Oct-Dec 2026")[:2] == OCT_DEC
    assert Q.parse_window("downtime Oct – Dec 2026")[:2] == OCT_DEC
    assert Q.parse_window("downtime from Oct-Dec 2026")[:2] == OCT_DEC


def test_a_year_crossing_dash_range():
    assert Q.parse_window("downtime November-January 2026")[:2] == NOV_JAN
    assert Q.parse_window("downtime Nov-Jan 2026")[:2] == NOV_JAN


def test_between_and_from_to_forms_are_unchanged():
    assert Q.parse_window("downtime between October and December 2026")[:2] == OCT_DEC
    assert Q.parse_window("downtime from October 2026 to December 2026")[:2] == OCT_DEC
    assert Q.parse_window("in October 2026")[:2] == (dt.date(2026, 10, 1), dt.date(2026, 10, 16))
