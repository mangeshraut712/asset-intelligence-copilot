"""Both ends of a closed range are read the same way: one numeric order, and a
yearless end that wraps past December runs into the next year."""
import datetime as dt
from copilot import query as Q

NYE = (dt.date(2025, 12, 31), dt.date(2026, 1, 2))


def test_unambiguous_month_day_end_sets_the_order_for_the_other_end():
    assert Q.parse_window("downtime 12/31/2025 to 1/2/2026")[:2] == NYE
    assert Q.parse_window("downtime between 1/2/2026 and 12/31/2025")[:2] == NYE


def test_unambiguous_day_month_end_keeps_day_month():
    assert Q.parse_window("downtime 31/12/2025 to 2/1/2026")[:2] == NYE


def test_yearless_days_crossing_new_year_run_forward():
    expected = (dt.date(2026, 12, 30), dt.date(2027, 1, 2))
    assert Q.parse_window("downtime from Dec 30 to Jan 2")[:2] == expected
    assert Q.parse_window("downtime between 30 Dec and 2 Jan")[:2] == expected


def test_yearless_end_takes_its_year_from_the_other_end():
    assert Q.parse_window("downtime from 30 Dec 2025 to 2 Jan")[:2] == (dt.date(2025, 12, 30), dt.date(2026, 1, 2))
    assert Q.parse_window("downtime from Dec 30 to Jan 2 2027")[:2] == (dt.date(2026, 12, 30), dt.date(2027, 1, 2))


def test_reversed_days_in_one_month_are_still_swapped():
    assert Q.parse_window("downtime from 5 Oct to 1 Oct")[:2] == (dt.date(2026, 10, 1), dt.date(2026, 10, 5))
