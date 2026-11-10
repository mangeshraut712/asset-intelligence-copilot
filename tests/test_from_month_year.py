"""from/since <month year> is the first of that month, not day 20 of the year digits."""
import datetime as dt
from copilot import query as Q

YESTERDAY = dt.date(2026, 10, 16)


def test_date_reads_month_year_as_the_first_of_that_month():
    assert Q._date("october 2026") == dt.date(2026, 10, 1)
    assert Q._date("Oct 2026") == dt.date(2026, 10, 1)
    assert Q._date("2026-10") == dt.date(2026, 10, 1)
    assert Q._date("october 20") == dt.date(2026, 10, 20)
    assert Q._date("oct 15 2026") == dt.date(2026, 10, 15)


def test_from_month_year_starts_on_the_first_and_ends_yesterday():
    expected_2026 = (dt.date(2026, 10, 1), YESTERDAY)
    expected_2025 = (dt.date(2025, 10, 1), YESTERDAY)
    assert Q.parse_window("downtime from October 2026")[:2] == expected_2026
    assert Q.parse_window("downtime from Oct 2026")[:2] == expected_2026
    assert Q.parse_window("downtime from 2026-10")[:2] == expected_2026
    assert Q.parse_window("downtime since September 2026")[:2] == (dt.date(2026, 9, 1), YESTERDAY)
    assert Q.parse_window("downtime from October 2025")[:2] == expected_2025
    start, end, _ = Q.parse_window("downtime from October 2026")
    assert start <= end


def test_from_a_specific_day_is_unchanged():
    assert Q.parse_window("downtime from 15 Oct 2026")[:2] == (dt.date(2026, 10, 15), YESTERDAY)
    assert Q.parse_window("downtime from Oct 15 2026")[:2] == (dt.date(2026, 10, 15), YESTERDAY)
    assert Q.parse_window("downtime from 2026-10-15")[:2] == (dt.date(2026, 10, 15), YESTERDAY)
