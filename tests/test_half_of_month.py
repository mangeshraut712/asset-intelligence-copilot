"""first/second half of a named month is days 1-15 / 16-end, not the whole month."""
import datetime as dt
from copilot import query as Q


def test_first_half_of_october():
    assert Q.parse_window("downtime first half of October")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 10, 15),
    )
    assert Q.parse_window("downtime first half of October 2026")[:2] == (
        dt.date(2026, 10, 1),
        dt.date(2026, 10, 15),
    )


def test_second_half_of_october_clips_to_yesterday():
    # TODAY is 17 Oct 2026, so the open second half ends yesterday.
    assert Q.parse_window("downtime second half of October")[:2] == (
        dt.date(2026, 10, 16),
        dt.date(2026, 10, 16),
    )


def test_second_half_of_a_past_month_uses_the_month_end():
    assert Q.parse_window("downtime second half of September 2026")[:2] == (
        dt.date(2026, 9, 16),
        dt.date(2026, 9, 30),
    )


def test_first_half_of_a_year_is_unchanged():
    assert Q.parse_window("downtime first half of 2026")[:2] == (
        dt.date(2026, 1, 1),
        dt.date(2026, 6, 30),
    )
