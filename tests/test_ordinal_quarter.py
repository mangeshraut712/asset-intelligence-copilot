"""2nd quarter 2026 is Q2, not the whole year."""
import datetime as dt
from copilot import query as Q


def test_ordinal_quarters():
    assert Q.parse_window("downtime 1st quarter 2026")[:2] == (dt.date(2026, 1, 1), dt.date(2026, 3, 31))
    assert Q.parse_window("downtime 2nd quarter 2026")[:2] == (dt.date(2026, 4, 1), dt.date(2026, 6, 30))
    assert Q.parse_window("downtime 3rd quarter of 2026")[:2] == (dt.date(2026, 7, 1), dt.date(2026, 9, 30))
    assert Q.parse_window("downtime 4th quarter 2026")[:2] == (dt.date(2026, 10, 1), dt.date(2026, 10, 16))


def test_word_and_q_forms_are_unchanged():
    assert Q.parse_window("downtime second quarter 2026")[:2] == (dt.date(2026, 4, 1), dt.date(2026, 6, 30))
    assert Q.parse_window("downtime Q2 2026")[:2] == (dt.date(2026, 4, 1), dt.date(2026, 6, 30))
