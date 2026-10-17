"""Post-submission logic for the final-question tools: OPS-3 note reading (incl. the ambiguous drive-trip
reading), data_correction notes, the evidence-based repair ranking, the shut-in delay breakdown and the
'which well first' comparison. Uses a tiny synthetic database, so it doesn't depend on any dataset."""
import datetime as dt, json, sqlite3, pytest
from copilot import loader, tools as T, final_tools as F

TODAY = dt.date(2027, 1, 15)

class CP:
    def __init__(self, c): self.c = c

@pytest.fixture
def cp(tmp_path, monkeypatch):
    c = sqlite3.connect(tmp_path / "t.db"); c.row_factory = sqlite3.Row
    c.executescript(loader.RAW_SCHEMA + loader.MEM_SCHEMA)
    monkeypatch.setattr(F, "TODAY", TODAY); monkeypatch.setattr(T, "TODAY", TODAY)
    c.execute("INSERT INTO areas VALUES('A-1','Alpha Block 1','TEAM-A',0,0)")
    c.execute("INSERT INTO teams VALUES('TEAM-A','Alpha Production','U-1')")
    c.execute("INSERT INTO users VALUES('U-1','Pat Lead','production_supervisor','TEAM-A')")
    for k, v in [("T200.producing_delta_c", 15), ("T500.producing_delta_c", 25), ("T200.rca_repairs", 3), ("T500.rca_repairs", 3)]:
        c.execute("INSERT INTO rules VALUES(?,?,?)", (k, v, "manual"))
    c.execute("INSERT INTO documents VALUES('T500','fleet/well-types/T500.md','T500','three inspections in a row (four readings, each lower than the last) and has fallen by 3 °C or more in total')")
    c.commit(); return CP(c)

def well(c, w, wt="T200"):
    c.execute("INSERT INTO wells VALUES(?,?,?,?,?,?,?,?,?,?,?)", (w, w, wt, "A-1", "TEAM-A", "U-1", 0, 0, "2010-01-01", "active", None))

def ins(c, w, iid, when, delta, method="drone"):
    c.execute("INSERT INTO inspections VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (iid, w, when, when[:10], "U-1", method, 5.0, 5.0 + delta, 0, None, None, "", "[]"))

def note(c, w, nid, when, text, kind="operator_note", **kw):
    c.execute("INSERT INTO notes VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (nid, w, when, "U-1", kind, kw.get("inspection_id"), text, when[:10], None,
                                                                   kw.get("field"), kw.get("orig"), kw.get("corr")))

def mnt(c, w, mid, start, end, issue, kind="corrective", eq="pump_jack", report=""):
    c.execute("INSERT INTO maintenance VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (mid, w, start, end, kind, eq, issue, "", "U-1", None, 1, 0, 0, 1000, None, None, None, report))

# ---------- pure helpers ----------
@pytest.mark.parametrize("text,kind", [
    ("Shut in WELL-0001 at the wellhead for the repair crew.", "shut"),
    ("Shut-in WELL-0001 so the maintenance crew can start work.", "shut"),
    ("Repair crew on WELL-0001, shut the well in for them.", "shut"),
    ("Found WELL-0001 leaking at the stuffing box, shut the well in.", "shut"),
    ("Restarted WELL-0001, unit running smooth.", "restart"),
    ("Brought WELL-0001 back online after the pump change.", "restart"),
    ("WELL-0001 put back on production after the repair crew finished.", "restart"),
    ("WELL-0001 drive tripping on underload, restarted from the panel.", "trip"),
    ("WELL-0001 drive tripping on and off overnight, reset it each time.", "trip"),
    ("Workover rig delayed by weather; restart pushed back about a week.", None),
    ("WELL-0001 pumping normally.", None),
])
def test_status_note_kind(text, kind):
    assert F.status_note_kind(text) == kind

def test_falling_rule():
    assert F.falling([37.3, 36.9, 34.9, 33.1], 3, 3.0)
    assert not F.falling([37.3, 36.9, 36.5, 36.0], 3, 3.0)        # falls, but less than 3 °C in total
    assert not F.falling([37.3, 36.9, 37.0, 33.1], 3, 3.0)        # not lower every time
    assert not F.falling([36.0, 33.0], 3, 3.0)                    # too few readings

def test_warning_rule_parsed_from_manual(cp):
    assert F.warning_rule(cp.c) == (3, 3.0, True)

def test_symptom_maps_to_equipment():
    assert F.symptom("Heard fluid pound on WELL-0001, unit still running.")[1] == ("downhole_pump",)
    assert F.symptom("Pumper reports rattling at WELL-0001 pump jack")[1] == ("pump_jack",)
    assert "esp_pump" in F.symptom("WELL-0001 drive tripping on underload")[1]

def test_chi2_sf_matches_tables():
    assert F.chi2_sf(3.841, 1) == pytest.approx(0.05, abs=1e-3)
    assert F.chi2_sf(28.869, 18) == pytest.approx(0.05, abs=1e-3)
    assert F.chi2_sf(0, 5) == 1.0

# ---------- data_correction notes ----------
def test_data_correction_note_changes_status(cp):
    c = cp.c; well(c, "WELL-0001")
    ins(c, "WELL-0001", "INS-1", "2027-01-14T10:00:00Z", 27.1)  # reads producing
    note(c, "WELL-0001", "CTX-1", "2027-01-14T18:00:00Z", "Inspection INS-1: wellhead_temp_c corrected", kind="data_correction",
         inspection_id="INS-1", field="wellhead_temp_c", orig="32.1", corr="10.4")
    r = T.effective_inspections(c, ["WELL-0001"])[-1]
    assert r["wellhead_temp_c"] == 10.4 and r["wellhead_temp_c_original"] == 32.1
    assert not r["producing"] and r["corrections"][0]["source"] == "CTX-1"

# ---------- OPS-3 conflicts ----------
def test_status_conflicts_reads_all_phrasings_and_reports_trip_reading(cp):
    c = cp.c
    for w in ["WELL-0001", "WELL-0002", "WELL-0003", "WELL-0004"]: well(c, w)
    ins(c, "WELL-0001", "INS-1", "2027-01-14T10:00:00Z", 25)   # producing, then "shut the well in" later
    note(c, "WELL-0001", "N1", "2027-01-14T19:00:00Z", "Found WELL-0001 leaking at the stuffing box, shut the well in.")
    ins(c, "WELL-0002", "INS-2", "2027-01-14T10:00:00Z", 2)    # not producing, restart note later
    note(c, "WELL-0002", "N2", "2027-01-15T10:00:00Z", "Restarted WELL-0002, unit running smooth.")
    ins(c, "WELL-0003", "INS-3", "2027-01-14T10:00:00Z", 2)    # drive trip reset before the inspection: ambiguous
    note(c, "WELL-0003", "N3", "2027-01-10T10:00:00Z", "WELL-0003 drive tripping on underload, restarted from the panel.")
    ins(c, "WELL-0004", "INS-4", "2027-01-14T10:00:00Z", 25)   # agrees: restart then producing
    note(c, "WELL-0004", "N4", "2027-01-10T10:00:00Z", "Restarted WELL-0004 after the crew cleared the lockout.")
    r = F.status_conflicts(cp, "")
    st = {row["Well"]: row["Status now"] for row in r["visual"]["rows"]}
    assert st == {"WELL-0001": "Not producing oil (shut in)", "WELL-0002": "Producing oil (unconfirmed)"}
    assert [a["Well"] for a in r["alt_table"]] == ["WELL-0003"]
    assert "Assumption, stated" in r["text"] and "same under both readings" in r["text"]

# ---------- repair ranking ----------
def test_note_risk_ranks_documented_precursors_first_and_skips_repaired(cp):
    c = cp.c
    well(c, "WELL-0500", "T500")  # ESP early-warning fall + one amps note
    for i, d in enumerate([37.3, 36.9, 34.9, 33.1]): ins(c, "WELL-0500", f"I5-{i}", f"2027-01-0{i+1}T10:00:00Z", d)
    note(c, "WELL-0500", "N5", "2027-01-05T10:00:00Z", "WELL-0500 amps hunting on the drive panel, still running.")
    well(c, "WELL-0200")          # three noise notes, producing steadily, no precursor
    for i, d in enumerate([25, 26, 25, 26]): ins(c, "WELL-0200", f"I2-{i}", f"2027-01-0{i+1}T10:00:00Z", d)
    for i in range(3): note(c, "WELL-0200", f"N2-{i}", f"2027-01-0{i+2}T10:00:00Z", "Rod squeal at WELL-0200 stuffing box, greased the polished rod.")
    well(c, "WELL-0201")          # unit running, wellhead cold, nothing explains it
    for i, d in enumerate([25, 26, 25, 3]): ins(c, "WELL-0201", f"I3-{i}", f"2027-01-0{i+1}T10:00:00Z", d)
    note(c, "WELL-0201", "N3", "2027-01-02T10:00:00Z", "Heard fluid pound on WELL-0201, unit still running.")
    well(c, "WELL-0202")          # repaired after its note: excluded
    ins(c, "WELL-0202", "I4", "2027-01-01T10:00:00Z", 25)
    note(c, "WELL-0202", "N4", "2027-01-02T10:00:00Z", "Pumper reports rattling at WELL-0202 pump jack, keep an eye on it.")
    mnt(c, "WELL-0202", "M4", "2027-01-03T08:00:00Z", "2027-01-03T18:00:00Z", "Walking beam bearing wear")
    well(c, "WELL-0203")          # spill clean-up after the note does not count as a repair
    ins(c, "WELL-0203", "I6", "2027-01-01T10:00:00Z", 25)
    note(c, "WELL-0203", "N6", "2027-01-02T10:00:00Z", "WELL-0203 tagging bottom on the downstroke, adjust spacing next visit.")
    mnt(c, "WELL-0203", "M6", "2027-01-03T08:00:00Z", "2027-01-03T18:00:00Z", "Flowline leak causing spill", eq="flowline")
    c.commit()
    r = F.note_risk(cp, "", "U-1", "x", n=10)
    order = [row["Well"] for row in r["visual"]["rows"]]
    assert "WELL-0202" not in order and "WELL-0203" in order
    assert set(order[:2]) == {"WELL-0500", "WELL-0201"} and order.index("WELL-0200") > 1
    assert "N5" in r["citations"] and "drive and insulation check" in r["visual"]["rows"][order.index("WELL-0500")]["Warning signs"]
    top3 = F.crew_first(cp, "", "U-1", "x")
    assert [x["Well"] for x in top3["visual"]["rows"]][:2] == order[:2] and "Assumption" in top3["text"]

# ---------- shut-in delays ----------
def test_delays_reports_no_standout_when_mix_is_even(cp):
    c = cp.c; well(c, "WELL-0001")
    causes = ["the replacement part was back-ordered from the supplier", "the job had to wait for a weekday contractor slot",
              "the crew was committed to a higher-priority spill response elsewhere", "heavy rain made the lease road impassable"]
    for i in range(40):
        mnt(c, "WELL-0001", f"M{i}", f"2026-{1 + i % 12:02d}-10T08:00:00Z", "2026-12-31T00:00:00Z", "Prime mover failure",
            report=f"The well stayed shut in about {5 + i % 7} days longer than the repair itself because {causes[i % 4]}.")
    c.commit()
    r = F.delays(cp, "jobs started in 2026")
    assert "40 jobs started in 2026" in r["text"] and "Not clearly" in r["text"] and "chi-square" in r["text"]
    assert r["table"][0]["Delayed share of jobs"] == "100%"

# ---------- which well first ----------
def test_deal_first_puts_unanswered_gas_report_first_and_explains(cp):
    c = cp.c
    for w in ["WELL-0001", "WELL-0002"]: well(c, w)
    ins(c, "WELL-0001", "INS-1", "2027-01-14T10:00:00Z", 25)
    note(c, "WELL-0001", "G1", "2026-12-03T12:10:00Z", "Gas odor reported by the pumper near WELL-0001 wellhead, area flagged off.")
    ins(c, "WELL-0002", "INS-2", "2027-01-14T10:00:00Z", 2)   # not producing, nothing else
    c.execute("INSERT INTO memory_conversations(user_id,chat_id,ts,question,answer,wells) VALUES('U-1','q9','t','q','a',?)", (json.dumps(["WELL-0002", "WELL-0001"]),))
    c.commit()
    r = F.deal_first(cp, "Of all the wells we've talked about today, which one would you deal with first?", "U-1", "q9")
    assert r["wells"] == ["WELL-0001"]
    assert "no crew on site since" in r["text"] and "Runner-up: **WELL-0002**" in r["text"] and "Assumption" in r["text"]
    assert [x["Well"] for x in r["visual"]["rows"]] == ["WELL-0001", "WELL-0002"]
