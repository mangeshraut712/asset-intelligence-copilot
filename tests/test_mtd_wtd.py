"""mtd and wtd must match month-to-date and week-to-date, not a bare year."""
import datetime as dt
from copilot import query as Q

MTD = (dt.date(2026, 10, 1), dt.date(2026, 10, 16))
WTD = Q.parse_window("spills week-to-date")[:2]
YTD = (dt.date(2026, 1, 1), dt.date(2026, 10, 16))
QTD = Q.parse_window("spills qtd")[:2]


def test_mtd_matches_month_to_date():
    assert Q.parse_window("spills month-to-date")[:2] == MTD
    assert Q.parse_window("spills mtd")[:2] == MTD
    assert Q.parse_window("spills MTD")[:2] == MTD
    # a trailing year must not widen this to the whole of 2026
    assert Q.parse_window("spills mtd 2026")[:2] == MTD


def test_wtd_matches_week_to_date():
    assert Q.parse_window("spills wtd")[:2] == WTD
    assert Q.parse_window("spills WTD")[:2] == WTD


def test_ytd_and_qtd_are_unchanged():
    assert Q.parse_window("spills ytd")[:2] == YTD
    assert Q.parse_window("spills qtd")[:2] == QTD
    assert Q.parse_window("spills this month")[:2] == MTD
