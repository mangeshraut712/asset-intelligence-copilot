"""from START to END must use the given end, not yesterday."""
import datetime as dt
from copilot import query as Q

YESTERDAY = dt.date(2026, 10, 16)
OCT_DEC_2026 = (dt.date(2026, 10, 1), dt.date(2026, 12, 31))


def test_from_month_year_to_month_year_includes_the_end_month():
    assert Q.parse_window("downtime from October 2026 to December 2026")[:2] == OCT_DEC_2026
    assert Q.parse_window("downtime from Oct 2026 to Dec 2026")[:2] == OCT_DEC_2026
    assert Q.parse_window("downtime from 2026-10 to 2026-12")[:2] == OCT_DEC_2026
    assert Q.parse_window("downtime from October 2026 through December 2026")[:2] == OCT_DEC_2026


def test_from_day_to_day_uses_the_given_end():
    assert Q.parse_window("downtime from 15 Oct 2026 to 20 Oct 2026")[:2] == (
        dt.date(2026, 10, 15),
        dt.date(2026, 10, 20),
    )
    assert Q.parse_window("downtime from 2026-10-15 to 2026-10-20")[:2] == (
        dt.date(2026, 10, 15),
        dt.date(2026, 10, 20),
    )


def test_from_bare_month_to_month_year():
    assert Q.parse_window("downtime from October to December 2026")[:2] == OCT_DEC_2026
    assert Q.parse_window("downtime from Oct to Dec 2026")[:2] == OCT_DEC_2026


def test_from_month_year_without_an_end_still_ends_yesterday():
    assert Q.parse_window("downtime from October 2026")[:2] == (dt.date(2026, 10, 1), YESTERDAY)
    assert Q.parse_window("downtime since September 2026")[:2] == (dt.date(2026, 9, 1), YESTERDAY)
    assert Q.parse_window("downtime from 15 Oct 2026")[:2] == (dt.date(2026, 10, 15), YESTERDAY)
