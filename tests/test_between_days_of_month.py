"""between DAY and DAY MONTH YEAR is a same-month range, not an empty window."""
import datetime as dt
from copilot import query as Q

MID_OCT = (dt.date(2026, 10, 15), dt.date(2026, 10, 20))


def test_between_days_of_a_named_month_year():
    assert Q.parse_window("downtime between 15 and 20 October 2026")[:2] == MID_OCT
    assert Q.parse_window("downtime between 15 and 20 Oct 2026")[:2] == MID_OCT
    assert Q.parse_window("downtime between 15th and 20th October 2026")[:2] == MID_OCT


def test_between_days_of_a_named_month_without_a_year():
    assert Q.parse_window("downtime between 15 and 20 October")[:2] == MID_OCT
    assert Q.parse_window("downtime between 15 and 20 Oct")[:2] == MID_OCT


def test_repeated_month_and_full_date_forms_are_unchanged():
    assert Q.parse_window("downtime between 15 October and 20 October 2026")[:2] == MID_OCT
    assert Q.parse_window("downtime between 15 Oct and 20 Oct 2026")[:2] == MID_OCT
    assert Q.parse_window("downtime between Oct 15 and Oct 20 2026")[:2] == MID_OCT
    assert Q.parse_window("downtime between 15/10/2026 and 20/10/2026")[:2] == MID_OCT
