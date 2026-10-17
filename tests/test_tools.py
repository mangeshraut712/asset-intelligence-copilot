from copilot import tools as T

def test_rules_parsed_from_documents():
    c = T.db()
    assert T.rule(c, "T200.producing_delta_c")[0] == 15 and T.rule(c, "T350.producing_delta_c")[0] == 20
    assert T.rule(c, "SR-01.hours")[0] == 24 and T.rule(c, "SR-02.hours")[0] == 4 and T.rule(c, "spill.reportable_bbl")[0] == 5
    assert T.rule(c, "SR-03.days")[0] == 60 and T.rule(c, "RC-04.days")[0] == 30

def test_status(fresh):
    s = T.well_status("WELL-0001")
    assert not s["producing"] and s["delta_c"] == 3.2 and s["recorded_status_stale"] and s["inspector"] == "Ryan Brooks"
    assert [w["asset_id"] for w in T.area_not_producing("Northeast Block 8")["wells"]] == ["WELL-0164", "WELL-0170", "WELL-0172", "WELL-0175"]

def test_hot_idle_wellhead_not_producing(fresh):
    ev = T.downtime(["WELL-0001"], *T.window(year=2025))[0]
    assert ev["days"] == 21 and ev["events"][0]["wellhead"] == 51.6 and ev["events"][0]["delta"] == 8.5

def test_ranking_and_window(fresh):
    s, e = T.window(months=4); assert (str(s), str(e)) == ("2026-06-16", "2026-10-16")
    r = T.downtime_ranking("Northeast Block 7", s, e)
    assert [(x["asset_id"], x["days"]) for x in r["top"]] == [("WELL-0121", 49), ("WELL-0107", 42), ("WELL-0138", 42)] and r["next"]["days"] == 28

def test_spills_with_correction_notes(fresh):
    r = T.spills(["WELL-0001"]); assert r["count"] == 6 and r["total_bbl"] == 15.1 and r["excluded"][0]["by"] == "CTX-0001-001"
    assert T.spill_heatmap(2026)["totals"] == {"Southwest Block 23": 35, "Southwest Block 24": 43, "Northeast Block 7": 37, "Northeast Block 8": 26}

def test_containment_and_compliance(fresh):
    assert [(x["asset_id"], x["contained_hours"]) for x in T.containment_breaches("Southwest Block 24")["rows"]] == [("WELL-0082", 7.1), ("WELL-0100", 8.1)]
    c = T.compliance("WELL-0001"); assert sorted(b["rule"] for b in c["breaches"]) == ["RC-04", "SR-01", "SR-02", "SR-03"] and c["fines_open"] == 5000

def test_rca_costs(fresh):
    assert [w["asset_id"] for w in T.rca_check("Northeast Block 7", "pump_jack")["wells"]] == ["WELL-0108", "WELL-0121", "WELL-0138"]
    assert [x["total_usd"] for x in T.repair_costs(["WELL-0121", "WELL-0138", "WELL-0107"], 2026)["rows"]] == [25794, 46942, 5176]

def test_area_resolution():
    c = T.db()
    assert T.area_id(c, "Northeast Block 7") == "NE-07" and T.area_id(c, "NE-7") == "NE-07" and T.area_id(c, "SW-23") == "SW-23" and T.area_id(c, "southwest block 24") == "SW-24"
