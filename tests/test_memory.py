from copilot import agent, tools as T

def ask(cp, q, u, chat, day=0):
    agent.SIM_DAY = day; return cp.ask(q, u, chat)

def test_private_memory_isolated(fresh):
    cp = agent.Copilot()
    ask(cp, "Which 3 wells in Northeast Block 7 had the most downtime in the last 4 months? Show a bar chart.", "Michael Turner", "a", 1)
    r = ask(cp, "For the three wells we discussed yesterday, what have repairs cost this year?", "Michael Turner", "b", 2)
    assert "WELL-0121: USD 25,794" in r["text"]
    r = ask(cp, "For the three wells we discussed yesterday, what have repairs cost this year?", "Jessica Reed", "c", 2)
    assert "no earlier conversation with Jessica Reed" in r["text"] and "25,794" not in r["text"]
    r = ask(cp, "For the three wells we discussed earlier, what have repairs cost this year?", "Michael Turner", "d", 2)
    assert "WELL-0138" in r["text"]

def test_correction_provenance_and_scope(fresh):
    cp = agent.Copilot()
    r = ask(cp, "The 15 Oct reading for WELL-0164 is wrong. The handheld thermal gun used in that inspection was faulty; the field crew re-measured the wellhead at 41.0 °C.", "Michael Turner", "a")
    assert "INS-0164-0205" in r["text"] and "Pump jack not moving" in r["text"]
    s = T.well_status("WELL-0164"); assert s["producing"] and s["corrections"][0]["original"] == "24.0" and s["corrections"][0]["by"] == "Michael Turner"
    assert T.well_status("WELL-0170")["producing"] is False  # other wells untouched
    r = ask(cp, "Is WELL-0164 producing oil right now?", "Jessica Reed", "j")
    assert "corrected by Michael Turner" in r["text"]

def test_type_rule_scope(fresh):
    cp = agent.Copilot()
    ask(cp, "Note for all T350 wells: our team now wants a pump jack root-cause analysis after 2 repairs, not 3.", "Michael Turner", "a")
    ids = [w["asset_id"] for w in T.rca_check("Northeast Block 7", "pump_jack")["wells"]]
    assert ids == ["WELL-0108", "WELL-0120", "WELL-0121", "WELL-0138"] and "WELL-0102" not in ids

def test_conflict_marked_unconfirmed(fresh):
    cp = agent.Copilot()
    ask(cp, "WELL-0175 has been shut in for planned work since 14 Oct.", "Michael Turner", "a")
    r = ask(cp, "WELL-0175 is running fine.", "Tyler Hughes", "t")
    assert "unconfirmed" in r["text"] and "Michael Turner" in r["text"]
    facts = T.shared_facts(T.db(), "WELL-0175"); assert [f["status"].split()[0] for f in facts] == ["confirmed", "unconfirmed"]

def test_user_requested_visual(fresh):
    cp = agent.Copilot()
    assert ask(cp, "Show WELL-0001 temperature for the last 13 weeks as a table", "U-201", "x")["visual"]["type"] == "table"
    assert ask(cp, "Which 3 wells in Northeast Block 7 had the most downtime in the last 4 months? Show it as a table", "U-201", "x")["visual"]["type"] == "table"
