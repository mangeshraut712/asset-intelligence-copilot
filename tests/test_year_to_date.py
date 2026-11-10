"""'year-to-date' with hyphens or dashes must match the spaced and ytd forms."""
import datetime as dt
from copilot import query as Q

YTD = (dt.date(2026, 1, 1), dt.date(2026, 10, 16))


def test_year_to_date_accepts_hyphen_and_dash_forms():
    assert Q.parse_window("spills year to date")[:2] == YTD
    assert Q.parse_window("spills year-to-date")[:2] == YTD
    assert Q.parse_window("year-to-date spills")[:2] == YTD
    assert Q.parse_window("spills year—to—date")[:2] == YTD  # em dash
    assert Q.parse_window("spills year–to–date")[:2] == YTD  # en dash
    assert Q.parse_window("YTD spills")[:2] == YTD
    assert Q.parse_window("spills ytd")[:2] == YTD


def test_year_to_date_does_not_match_unrelated_year_phrases():
    # a bare calendar year is a full-year window, not year-to-date
    year = Q.parse_window("spills in 2026")
    assert year[:2] == (dt.date(2026, 1, 1), dt.date(2026, 10, 16))
    assert year[2] == "2026"
