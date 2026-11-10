"""last N quarters is a rolling 3N-month window ending yesterday."""
import datetime as dt
from copilot import query as Q

TWO_QUARTERS = (dt.date(2026, 4, 16), dt.date(2026, 10, 16))


def test_last_two_quarters():
    assert Q.parse_window("downtime last 2 quarters")[:2] == TWO_QUARTERS
    assert Q.parse_window("downtime last two quarters")[:2] == TWO_QUARTERS
    assert Q.parse_window("downtime past 2 quarters")[:2] == TWO_QUARTERS
    assert Q.parse_window("downtime previous 2 quarters")[:2] == TWO_QUARTERS


def test_last_quarter_without_a_count_is_unchanged():
    # Calendar Q3 2026, not a rolling 3-month window.
    assert Q.parse_window("downtime last quarter")[:2] == (
        dt.date(2026, 7, 1),
        dt.date(2026, 9, 30),
    )
