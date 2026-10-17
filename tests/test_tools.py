"""Deterministic tool tests on the sample dataset (run: python -m pytest tests or python tests/test_tools.py)."""
import os, sys, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from copilot import tools as T
from copilot.loader import DB_PATH

def clear():
    c = sqlite3.connect(DB_PATH)
    for t in ["memory_corrections", "memory_type_rules"]: c.execute(f"DELETE FROM {t}")
    c.commit()

def test_rules_parsed():
    c = T.db(); assert T.rule(c, "T200.producing_delta_c")[0] == 15 and T.rule(c, "T350.producing_delta_c")[0] == 20
    assert T.rule(c, "SR-01.hours")[0] == 24 and T.rule(c, "SR-02.hours")[0] == 4 and T.rule(c, "spill.reportable_bbl")[0] == 5

def test_status_and_downtime():
    clear(); s = T.well_status("WELL-0001"); assert not s["producing"] and s["delta_c"] == 3.2 and s["recorded_status_stale"]
    assert T.downtime(["WELL-0001"], *T.window(year=2025))[0]["days"] == 21
    r = T.downtime_ranking("Northeast Block 7", *T.window(months=4)); assert [(x["asset_id"], x["days"]) for x in r["top"]][0] == ("WELL-0121", 49)

def test_spills_corrections():
    r = T.spills(["WELL-0001"]); assert r["count"] == 6 and r["total_bbl"] == 15.1
    assert T.spill_heatmap(2026)["totals"]["Northeast Block 8"] == 26

def test_containment_and_compliance():
    assert [x["asset_id"] for x in T.containment_breaches("Southwest Block 24")["rows"]] == ["WELL-0082", "WELL-0100"]
    assert sorted(b["rule"] for b in T.compliance("WELL-0001")["breaches"]) == ["RC-04", "SR-01", "SR-02", "SR-03"]

def test_rca_and_costs():
    clear(); assert [w["asset_id"] for w in T.rca_check("Northeast Block 7", "pump_jack")["wells"]] == ["WELL-0108", "WELL-0121", "WELL-0138"]
    assert [x["total_usd"] for x in T.repair_costs(["WELL-0121", "WELL-0138", "WELL-0107"], 2026)["rows"]] == [25794, 46942, 5176]

if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"): f(); print("ok", k)
