"""during/for/of YYYY-MM must be that month, like in YYYY-MM already is."""
import datetime as dt
from copilot import query as Q

OCT_2026 = (dt.date(2026, 10, 1), dt.date(2026, 10, 16))  # through yesterday


def test_during_for_and_of_year_month_are_that_month():
    assert Q.parse_window("spills during 2026-10")[:2] == OCT_2026
    assert Q.parse_window("spills for 2026-10")[:2] == OCT_2026
    assert Q.parse_window("spills of 2026-10")[:2] == OCT_2026
    assert Q.parse_window("spills during 2026/10")[:2] == OCT_2026


def test_in_year_month_and_named_month_are_unchanged():
    assert Q.parse_window("spills in 2026-10")[:2] == OCT_2026
    assert Q.parse_window("spills in October 2026")[:2] == OCT_2026
    assert Q.parse_window("spills during October 2026")[:2] == OCT_2026
