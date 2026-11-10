"""between <month year> and <month year> includes the whole end month, not just the 1st."""
import datetime as dt
from copilot import query as Q


def test_between_month_years_runs_through_the_last_day_of_the_end_month():
    expected = (dt.date(2026, 10, 1), dt.date(2026, 12, 31))
    assert Q.parse_window("downtime between October 2026 and December 2026")[:2] == expected
    assert Q.parse_window("downtime between Oct 2026 and Dec 2026")[:2] == expected
    assert Q.parse_window("downtime between 2026-10 and 2026-12")[:2] == expected


def test_between_explicit_days_is_unchanged():
    expected = (dt.date(2026, 10, 1), dt.date(2026, 12, 31))
    assert Q.parse_window("downtime between 1 Oct 2026 and 31 Dec 2026")[:2] == expected
    assert Q.parse_window("downtime between 15 Oct 2026 and 20 Oct 2026")[:2] == (
        dt.date(2026, 10, 15),
        dt.date(2026, 10, 20),
    )
