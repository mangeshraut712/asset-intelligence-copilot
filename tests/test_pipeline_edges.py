"""Edge cases in the answer pipeline: blank input, impossible dates, unknown wells, empty scopes."""
import datetime as dt
from fastapi.testclient import TestClient
from copilot import agent, query as Q, tools as T
from copilot.server import app

client = TestClient(app)


def test_blank_questions_do_not_crash_or_remember(fresh):
    cp = agent.Copilot()
    for q in ["", "   ", "???", "\n\t", "\x00", "…"]:
        r = cp.ask(q, "U-201", "edge")
        assert "Ask about" in r["text"] and r["visual"] is None and r["wells"] == []
        assert r["confidence"] == "low" and r["assumptions"] == []
    assert T.db().execute("SELECT count(*) c FROM memory_conversations").fetchone()["c"] == 0


def test_status_question_still_answers(fresh):
    cp = agent.Copilot()
    r = cp.ask("  Is WELL-0001 producing oil right now?  ", "U-201", "edge")
    assert "not producing" in r["text"].lower() and r["confidence"] == "high"
    assert r["assumptions"] == [] and r["trace"]["citations"] >= 1


def test_unknown_well_is_refused_and_not_stored(fresh):
    cp = agent.Copilot()
    r = cp.ask("WELL-9999 has been shut in since 14 Oct.", "Michael Turner", "edge")
    assert "don't have WELL-9999" in r["text"]
    r = cp.ask("Is WELL-9999 producing oil right now?", "U-201", "edge")
    assert "don't have WELL-9999" in r["text"]
    c = T.db()
    assert c.execute("SELECT count(*) c FROM memory_well_facts").fetchone()["c"] == 0
    assert c.execute("SELECT count(*) c FROM memory_corrections").fetchone()["c"] == 0


def test_bare_well_id_is_status_not_a_fact(fresh):
    cp = agent.Copilot()
    r = cp.ask("WELL-0001", "U-201", "edge")
    assert "producing" in r["text"].lower() and r["visual"]["type"] == "card"
    assert T.db().execute("SELECT count(*) c FROM memory_well_facts").fetchone()["c"] == 0
    r = cp.ask("status of WELL-0001", "U-201", "edge")
    assert "producing" in r["text"].lower()


def test_invalid_dates_do_not_write_memory(fresh):
    cp = agent.Copilot()
    r = cp.ask("The 31 February reading for WELL-0164 is wrong. The wellhead was re-measured at 41.0 °C.", "Michael Turner", "edge")
    assert "isn't a real calendar date" in r["text"]
    r = cp.ask("WELL-0175 has been shut in since 31 February.", "Michael Turner", "edge")
    assert "isn't a real calendar date" in r["text"]
    r = cp.ask("Was the 31 February spill at WELL-0101 real oil?", "U-201", "edge")
    assert "isn't a real calendar date" in r["text"]
    c = T.db()
    assert c.execute("SELECT count(*) c FROM memory_corrections").fetchone()["c"] == 0
    assert c.execute("SELECT count(*) c FROM memory_well_facts").fetchone()["c"] == 0
    assert T.well_status("WELL-0164")["producing"] is False


def test_duplicate_correction_and_type_rule(fresh):
    cp = agent.Copilot()
    q = "The 15 Oct reading for WELL-0164 is wrong. The handheld thermal gun used in that inspection was faulty; the field crew re-measured the wellhead at 41.0 °C."
    first = cp.ask(q, "Michael Turner", "a")
    assert "INS-0164-0205" in first["text"] and "producing" in first["text"]
    again = cp.ask(q, "Jessica Reed", "b")
    assert "already on record" in again["text"] and "duplicate" in again["text"]
    rule = "Note for all T350 wells: our team now wants a pump jack root-cause analysis after 2 repairs, not 3."
    cp.ask(rule, "Michael Turner", "a")
    second = cp.ask(rule, "Jessica Reed", "b")
    assert "already on record" in second["text"]
    c = T.db()
    assert c.execute("SELECT count(*) c FROM memory_corrections").fetchone()["c"] == 1
    assert c.execute("SELECT count(*) c FROM memory_type_rules").fetchone()["c"] == 1
    assert T.well_status("WELL-0164")["producing"] is True


def test_windows_survive_inverted_and_impossible_dates():
    assert Q.parse_window("between 31 Jul 2026 and 1 May 2026")[:2] == (dt.date(2026, 5, 1), dt.date(2026, 7, 31))
    assert Q.parse_window("between 31 February 2026 and 5 March 2026") is None
    assert Q.parse_window("since 31 February 2026") is None
    huge = Q.parse_window("last 100000 months")
    assert huge and huge[0] <= huge[1] and huge[0].year >= 1
    assert Q.parse_window("last 4 months")[:2] == (dt.date(2026, 6, 16), dt.date(2026, 10, 16))
    assert agent.parse_date("31 February 2026") is None
    assert agent.parse_date("15 Oct 2026") == dt.date(2026, 10, 15)
    assert agent.invalid_date_phrase("on 31 February please") == "31 February"
    assert agent.invalid_date_phrase("15 Oct 2026") is None


def test_validate_rejects_malformed_plans():
    assert Q.validate({"metric": "spills", "group_by": "area", "window": (dt.date(2026, 8, 1), dt.date(2026, 1, 1))})
    assert Q.validate({"metric": "spills", "group_by": None, "window": ("2026-01-01", "2026-02-01")})
    assert Q.validate({"metric": "spills", "group_by": None, "scope": {"wells": ["nope"]}, "top": 0})
    assert not Q.validate({"metric": "spills", "group_by": "well", "scope": {"wells": ["WELL-0001"]}, "window": (dt.date(2026, 1, 1), dt.date(2026, 2, 1), "label")})
    bad = Q.run_query("not_a_metric", {})
    assert bad["rows"] == [] and "unknown metric" in bad["error"]


def test_empty_scope_queries_do_not_crash():
    assert T.effective_inspections(T.db(), []) == []
    r = Q.run_query("downtime", {"well_type": "T999"}, (dt.date(2026, 1, 1), dt.date(2026, 2, 1)), "well")
    assert r["rows"] == [] and r["n_wells"] == 0
    r = Q.run_query("spills", {"wells": ["WELL-9999"]})
    assert r["rows"] == [] and r["n_wells"] == 0
    r = Q.run_query("fines", {"well_type": "T999"})
    assert r["rows"] == [] and r["total"] == 0
    flipped = Q.run_query("repairs", {"area": "NE-07"}, (dt.date(2026, 8, 1), dt.date(2026, 1, 1)))
    assert flipped["window"] == ["2026-01-01", "2026-08-01"]


def test_convert_visual_tolerates_ragged_series():
    short = {"type": "bar", "x": ["a", "b"], "series": [{"name": "n", "data": [1]}]}
    assert agent.convert_visual(short, "table")["type"] == "bar"
    ok = {"type": "bar", "x": ["a"], "series": [{"name": "n", "data": [1]}]}
    table = agent.convert_visual(ok, "table")
    assert table["type"] == "table" and table["rows"] == [{"Label": "a", "n": 1}]
    assert agent.convert_visual(None, "table") is None
    heat = {"type": "heatmap", "x": ["Jan", "Feb"], "y": ["A"], "z": [[1]]}
    assert agent.convert_visual(heat, "table")["type"] == "heatmap"


def test_well_without_inspections(fresh):
    c = T.db()
    c.execute("DELETE FROM wells WHERE asset_id='WELL-9000'")
    c.execute("INSERT INTO wells(asset_id, name, well_type, area_id, team_id, lat, lon, recorded_status) VALUES('WELL-9000','Empty','T200','NE-07','TEAM-NE',0,0,'active')")
    c.commit()
    try:
        assert "no inspections" in T.well_status("WELL-9000")["error"]
        cp = agent.Copilot()
        status = cp.ask("Is WELL-9000 producing oil right now?", "U-201", "edge")
        assert "no inspections" in status["text"]
        temps = cp.ask("Show WELL-9000 temperature for the last 13 weeks", "U-201", "edge")
        assert "No temperature readings" in temps["text"]
        fix = cp.ask("The 15 Oct reading for WELL-9000 is wrong. Re-measured the wellhead at 41.0 °C.", "Michael Turner", "edge")
        assert "nothing to correct" in fix["text"]
        assert c.execute("SELECT count(*) c FROM memory_corrections").fetchone()["c"] == 0
    finally:
        c.execute("DELETE FROM wells WHERE asset_id='WELL-9000'")
        c.commit()


def test_mixed_well_ids_keep_the_known_one(fresh):
    cp = agent.Copilot()
    r = cp.ask("Is WELL-0001 producing oil right now? Also check WELL-9999.", "U-201", "edge")
    assert "not producing" in r["text"].lower()
    assert "WELL-9999" in r["text"] and "left out" in r["text"]
    note = cp.ask("WELL-0001 and WELL-0007 will be shut in from 17 Oct for a workover.", "Jake Morales", "edge")
    assert note["text"].startswith("Noted") and "WELL-0007" in note["text"] and "separate note" in note["text"]
    wells = [row["asset_id"] for row in T.db().execute("SELECT asset_id FROM memory_well_facts")]
    assert wells == ["WELL-0001"]


def test_assumption_lines_are_structured():
    text = "Send a crew.\n\nAssumption: 'today' means this conversation."
    assert agent.collect_assumptions(text) == ["Assumption: 'today' means this conversation."]
    assert agent.collect_assumptions("No assumption here.", ["Assumption: the window was reversed."]) == ["Assumption: the window was reversed."]


def test_api_blank_question(fresh):
    r = client.post("/api/ask", json={"question": "   ", "user": "U-201", "chat": "edge"}).json()
    assert "Ask about" in r["text"] and r["confidence"] == "low" and r["visual"] is None
    assert "assumptions" in r and r["trace"]["assumptions"] == []
