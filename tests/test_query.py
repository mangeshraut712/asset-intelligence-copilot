import datetime as dt
from copilot import query as Q, tools as T

def test_parse_window():
    assert Q.parse_window("last 4 months")[:2] == (dt.date(2026, 6, 16), dt.date(2026, 10, 16))
    assert Q.parse_window("in March 2026")[:2] == (dt.date(2026, 3, 1), dt.date(2026, 3, 31))
    assert Q.parse_window("between 1 May 2026 and 31 Jul 2026")[:2] == (dt.date(2026, 5, 1), dt.date(2026, 7, 31))
    assert Q.parse_window("this summer")[:2] == (dt.date(2026, 6, 1), dt.date(2026, 8, 31))
    assert Q.parse_window("first half of 2026")[:2] == (dt.date(2026, 1, 1), dt.date(2026, 6, 30))
    assert Q.parse_window("Q2 2025")[:2] == (dt.date(2025, 4, 1), dt.date(2025, 6, 30))
    assert Q.parse_window("is it producing right now") is None

def test_parse_scope_metric_group():
    c = T.db(); s = Q.parse_scope(c, "fines for T350 wells of the Southwest Production team in Northeast Block 7")
    assert s == {"area": "NE-07", "well_type": "T350", "team": "TEAM-SW"}
    assert Q.parse_metric("how much did repairs cost") == "repair_cost" and Q.parse_metric("crude on the ground") == "spill_volume"
    assert Q.parse_group("downtime by area") == "area" and Q.parse_group("spills by month") == "month"

def test_validate_and_query():
    assert Q.validate({"metric": "nope", "group_by": None}) and not Q.validate({"metric": "spills", "group_by": "area"})
    r = Q.run_query("downtime", {"area": "NE-07"}, (dt.date(2026, 6, 16), dt.date(2026, 10, 16)), "well", 3)
    assert [(x["key"], x["value"]) for x in r["rows"]] == [("WELL-0121", 49), ("WELL-0107", 42), ("WELL-0138", 42)]

def test_briefing_and_evidence():
    from copilot.insights import briefing, evidence
    b = {c["id"]: c for c in briefing()["cards"]}; assert b["fines"]["count"] == 2 and b["breaches"]["count"] > 0
    e = evidence("MNT-0001-029"); assert any("contained about 7 hours" in h for h in e["highlight"])
    assert evidence("Spill Response SOP SR-02")["highlight"]
