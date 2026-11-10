"""Sept is a common abbreviation for September and must parse as that month."""
import datetime as dt
from copilot import query as Q

SEP_2026 = (dt.date(2026, 9, 1), dt.date(2026, 9, 30))


def test_sept_is_september():
    assert Q.parse_window("in Sept 2026")[:2] == SEP_2026
    assert Q.parse_window("in Sept 2025")[:2] == (dt.date(2025, 9, 1), dt.date(2025, 9, 30))
    assert Q._date("Sept 2026") == dt.date(2026, 9, 1)
    assert Q._month_only("Sept") == 9


def test_sep_and_september_are_unchanged():
    assert Q.parse_window("in Sep 2026")[:2] == SEP_2026
    assert Q.parse_window("in September 2026")[:2] == SEP_2026
