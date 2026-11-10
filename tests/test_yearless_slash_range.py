"""from 01/10 to 15/10 is a closed day range in the current year."""
import datetime as dt
from copilot import query as Q


def test_from_yearless_slash_to_yearless_slash():
    expected = (dt.date(2026, 10, 1), dt.date(2026, 10, 15))
    assert Q.parse_window("downtime from 01/10 to 15/10")[:2] == expected
    assert Q.parse_window("downtime from 1/10 to 15/10")[:2] == expected
    assert Q.parse_window("downtime between 01/10 and 15/10")[:2] == expected


def test_yearless_mdy_when_the_second_number_cannot_be_a_month():
    # 10/15 cannot be day-month, so it is October 15.
    assert Q.parse_window("downtime from 10/01 to 10/15")[:2] == (
        dt.date(2026, 1, 10),
        dt.date(2026, 10, 15),
    )


def test_dated_slash_with_a_year_is_unchanged():
    assert Q.parse_window("downtime from 01/10/2026 to 15/10/2026")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 10, 15),
    )
