"""parse_date() must accept the date forms the product already documents."""
import datetime as dt
from copilot import agent


def test_parse_date_accepts_day_month_iso_and_month_first_forms():
    expected = dt.date(2026, 10, 15)
    assert agent.parse_date("15 Oct 2026") == expected
    assert agent.parse_date("15 October 2026") == expected
    assert agent.parse_date("2026-10-15") == expected
    assert agent.parse_date("on 2026-10-15 show spills") == expected
    assert agent.parse_date("Oct 15 2026") == expected
    assert agent.parse_date("October 15, 2026") == expected
    assert agent.invalid_date_phrase("15 Oct 2026") is None
    assert agent.invalid_date_phrase("2026-10-15") is None
    assert agent.invalid_date_phrase("October 15, 2026") is None


def test_parse_date_rejects_impossible_days_in_each_form():
    assert agent.parse_date("31 February 2026") is None
    assert agent.invalid_date_phrase("on 31 February please") == "31 February"
    assert agent.parse_date("2026-02-31") is None
    assert agent.invalid_date_phrase("2026-02-31") == "2026-02-31"
    assert agent.parse_date("Feb 31 2026") is None
    assert agent.invalid_date_phrase("Feb 31 2026") == "Feb 31 2026"
