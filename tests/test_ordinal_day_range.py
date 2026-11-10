"""1st to 15th October is a closed day range in that month."""
import datetime as dt
from copilot import query as Q


def test_ordinal_day_to_day_of_month():
    expected = (dt.date(2026, 10, 1), dt.date(2026, 10, 15))
    assert Q.parse_window("downtime 1st to 15th October")[:2] == expected
    assert Q.parse_window("downtime 1st to 15th October 2026")[:2] == expected
    assert Q.parse_window("downtime 1 to 15 October")[:2] == expected
    assert Q.parse_window("downtime 1st through 15th October")[:2] == expected


def test_between_days_of_month_is_unchanged():
    assert Q.parse_window("downtime between 15 and 20 October")[:2] == (
        dt.date(2026, 10, 15),
        dt.date(2026, 10, 20),
    )
