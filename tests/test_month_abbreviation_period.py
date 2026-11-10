"""A period after a month abbreviation must not widen the window to the whole year."""
import datetime as dt
from copilot import query as Q

DAY = dt.date(2026, 10, 15)
SEP_2026 = (dt.date(2026, 9, 1), dt.date(2026, 9, 30))


def test_on_oct_dot_is_that_day_not_the_year():
    assert Q.parse_window("spills on Oct. 15, 2026")[:2] == (DAY, DAY)
    assert Q.parse_window("spills on Oct. 15 2026")[:2] == (DAY, DAY)
    assert Q._date("Oct. 15, 2026") == DAY


def test_sept_dot_is_still_september():
    assert Q.parse_window("in Sept. 2026")[:2] == SEP_2026
    assert Q._date("Sept. 2026") == dt.date(2026, 9, 1)


def test_forms_without_a_period_are_unchanged():
    assert Q.parse_window("spills on Oct 15, 2026")[:2] == (DAY, DAY)
    assert Q.parse_window("spills on October 15, 2026")[:2] == (DAY, DAY)
    assert Q.parse_window("in September 2026")[:2] == SEP_2026
