"""A bare month in a between-range inherits the year from the other end."""
import datetime as dt
from copilot import query as Q

EXPECTED_2026 = (dt.date(2026, 10, 1), dt.date(2026, 12, 31))


def test_mixed_bare_month_and_month_year():
    assert Q.parse_window("downtime between October and December 2026")[:2] == EXPECTED_2026
    assert Q.parse_window("downtime between October 2026 and December")[:2] == EXPECTED_2026
    assert Q.parse_window("downtime between Oct and Dec 2025")[:2] == (
        dt.date(2025, 10, 1),
        dt.date(2025, 12, 31),
    )


def test_existing_between_forms_are_unchanged():
    assert Q.parse_window("downtime between October and December")[:2] == EXPECTED_2026
    assert Q.parse_window("downtime between October 2026 and December 2026")[:2] == EXPECTED_2026
    assert Q.parse_window("downtime between 2026-10 and December 2026")[:2] == EXPECTED_2026
    assert Q.parse_window("downtime between 1 Oct 2026 and 31 Dec 2026")[:2] == EXPECTED_2026
