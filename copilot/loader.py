"""Re-runnable loader: reads one or more dataset folders (sample-data layout) into SQLite.
Raw data tables are rebuilt on each run; runtime memory tables (memory_*) are preserved."""
import json, os, re, sqlite3, sys, glob

DB_PATH = os.environ.get("AIC_DB", os.path.join(os.path.dirname(__file__), "..", "data", "copilot.db"))

RAW_SCHEMA = """
DROP TABLE IF EXISTS areas; DROP TABLE IF EXISTS teams; DROP TABLE IF EXISTS users; DROP TABLE IF EXISTS wells;
DROP TABLE IF EXISTS equipment; DROP TABLE IF EXISTS inspections; DROP TABLE IF EXISTS maintenance;
DROP TABLE IF EXISTS reports; DROP TABLE IF EXISTS reg_events; DROP TABLE IF EXISTS notes; DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS rules;
CREATE TABLE areas(area_id TEXT PRIMARY KEY, name TEXT, team_id TEXT, lat REAL, lon REAL);
CREATE TABLE teams(team_id TEXT PRIMARY KEY, name TEXT, lead_user_id TEXT);
CREATE TABLE users(user_id TEXT PRIMARY KEY, name TEXT, role TEXT, team_id TEXT);
CREATE TABLE wells(asset_id TEXT PRIMARY KEY, name TEXT, well_type TEXT, area_id TEXT, team_id TEXT,
  in_charge_user_id TEXT, lat REAL, lon REAL, installed_on TEXT, recorded_status TEXT, last_inspection_id TEXT);
CREATE TABLE equipment(equipment_id TEXT, asset_id TEXT, kind TEXT, model TEXT);
CREATE TABLE inspections(inspection_id TEXT PRIMARY KEY, asset_id TEXT, inspected_at TEXT, date TEXT,
  inspector_user_id TEXT, method TEXT, ambient_temp_c REAL, wellhead_temp_c REAL, spill_detected INT,
  spill_area_pct REAL, spill_est_volume_bbl REAL, notes TEXT, evidence_images TEXT);
CREATE INDEX ix_ins ON inspections(asset_id, date);
CREATE TABLE maintenance(maintenance_id TEXT PRIMARY KEY, asset_id TEXT, started_at TEXT, completed_at TEXT,
  maintenance_type TEXT, equipment_kind TEXT, issue TEXT, action_taken TEXT, technician_user_id TEXT,
  contractor TEXT, downtime_hours REAL, cost_labor REAL, cost_parts REAL, cost_total REAL,
  triggered_by_inspection_id TEXT, report_file TEXT, contained_hours REAL, report_text TEXT);
CREATE INDEX ix_mnt ON maintenance(asset_id);
CREATE TABLE reg_events(event_id TEXT PRIMARY KEY, asset_id TEXT, date TEXT, agency TEXT, event_type TEXT,
  protocol_id TEXT, related_inspection_id TEXT, detail TEXT, hours_to_report REAL, fine_usd REAL, status TEXT);
CREATE TABLE notes(note_id TEXT PRIMARY KEY, asset_id TEXT, created_at TEXT, author_user_id TEXT, note_type TEXT,
  inspection_id TEXT, text TEXT, valid_from TEXT, valid_to TEXT);
CREATE TABLE documents(doc_id TEXT PRIMARY KEY, path TEXT, title TEXT, text TEXT);
CREATE TABLE rules(key TEXT PRIMARY KEY, value REAL, source TEXT);
"""

MEM_SCHEMA = """
CREATE TABLE IF NOT EXISTS memory_conversations(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, chat_id TEXT,
  ts TEXT, question TEXT, answer TEXT, wells TEXT);
CREATE TABLE IF NOT EXISTS memory_well_facts(id INTEGER PRIMARY KEY AUTOINCREMENT, asset_id TEXT, author_user_id TEXT,
  ts TEXT, text TEXT, kind TEXT, status TEXT, conflict TEXT);
CREATE TABLE IF NOT EXISTS memory_corrections(id INTEGER PRIMARY KEY AUTOINCREMENT, inspection_id TEXT, asset_id TEXT,
  field TEXT, original_value TEXT, corrected_value TEXT, author_user_id TEXT, ts TEXT, reason TEXT, conflict TEXT);
CREATE TABLE IF NOT EXISTS memory_type_rules(id INTEGER PRIMARY KEY AUTOINCREMENT, well_type TEXT, rule_key TEXT,
  value REAL, author_user_id TEXT, ts TEXT, text TEXT);
"""

def _num(pattern, text, default=None):
    m = re.search(pattern, text, re.I | re.S)
    return float(m.group(1)) if m else default

def parse_rules(fleet):
    """Extract thresholds/deadlines from manuals and SOPs (not hard-coded)."""
    rules = []
    for p in sorted(glob.glob(os.path.join(fleet, "well-types", "*.md"))):
        t = os.path.splitext(os.path.basename(p))[0]
        txt = open(p).read()
        thr = _num(r"producing \(active\)\*\*.*?at least \*\*([\d.]+)\s*°C above", txt)
        rules.append((f"{t}.producing_delta_c", thr, f"{t} manual (production temperature rule)"))
        rca = _num(r"(\w+) or more \*\*corrective\*\*", txt.replace("Three", "3"))
        if rca is None and re.search(r"after three corrective", txt, re.I): rca = 3
        rules.append((f"{t}.rca_repairs", rca or 3, f"{t} manual (maintenance escalation, RCA)"))
    s = open(os.path.join(fleet, "sops", "spill-response-sop.md")).read()
    rules += [
        ("spill.reportable_bbl", _num(r"Reportable \| ([\d.]+) bbl", s, 5), "Spill Response SOP §3"),
        ("spill.major_bbl", _num(r"Major \| ([\d.]+) bbl", s, 25), "Spill Response SOP §3"),
        ("spill.moderate_bbl", _num(r"Moderate \| ([\d.]+) bbl", s, 1), "Spill Response SOP §3"),
        ("SR-01.hours", _num(r"within \*\*([\d.]+) hours\*\* of discovery, or", s, 24), "Spill Response SOP SR-01"),
        ("SR-02.hours", _num(r"contained within \*\*([\d.]+) hours", s, 4), "Spill Response SOP SR-02"),
        ("SR-03.days", _num(r"verified within ([\d.]+) days", s, 60), "Spill Response SOP SR-03"),
    ]
    r = open(os.path.join(fleet, "sops", "regulatory-compliance-sop.md")).read()
    rules.append(("RC-04.days", _num(r"answered within \*\*([\d.]+) days", r, 30), "Regulatory Compliance SOP RC-04"))
    return rules

_CONTAINED = re.compile(r"contained\W*(?:about|after about|after|within|in)?\s*(?:about\s*)?\**\s*(\d+(?:\.\d+)?)\s*(hours?|hrs?|h|minutes?|mins?)\b", re.I)

def parse_contained_hours(text):
    """Containment time (hours) from the narrative of a free-text repair report.
    Prefers the 'What happened' narrative over the compliance table; converts minutes."""
    if not text: return None
    t = text.replace("**", "")
    m = _CONTAINED.search(t)
    if not m: return None
    v = float(m.group(1))
    return round(v / 60, 2) if m.group(2).lower().startswith("m") else v

def load(data_dirs, db_path=DB_PATH):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    con = sqlite3.connect(db_path)
    con.executescript(RAW_SCHEMA + MEM_SCHEMA)
    for d in data_dirs:
        fleet = os.path.join(d, "fleet")
        a = json.load(open(os.path.join(fleet, "areas.json")))
        for x in a["areas"]:
            con.execute("INSERT OR REPLACE INTO areas VALUES(?,?,?,?,?)", (x["area_id"], x["name"], x["team_id"], x["center"]["lat"], x["center"]["lon"]))
        for x in a.get("teams", []):
            con.execute("INSERT OR REPLACE INTO teams VALUES(?,?,?)", (x["team_id"], x["name"], x.get("lead_user_id")))
        for x in json.load(open(os.path.join(fleet, "users.json")))["users"]:
            con.execute("INSERT OR REPLACE INTO users VALUES(?,?,?,?)", (x["user_id"], x["name"], x["role"], x.get("team_id")))
        for k, v, src in parse_rules(fleet):
            con.execute("INSERT OR REPLACE INTO rules VALUES(?,?,?)", (k, v, src))
        for p in glob.glob(os.path.join(fleet, "**", "*.md"), recursive=True):
            txt = open(p).read(); rel = os.path.relpath(p, d)
            title = (re.search(r"^# (.+)$", txt, re.M) or [None, rel])[1]
            con.execute("INSERT OR REPLACE INTO documents VALUES(?,?,?,?)", (rel, rel, title, txt))
        for wd in sorted(glob.glob(os.path.join(d, "assets", "*"))):
            m = json.load(open(os.path.join(wd, "metadata.json")))
            con.execute("INSERT OR REPLACE INTO wells VALUES(?,?,?,?,?,?,?,?,?,?,?)", (m["asset_id"], m.get("name"), m["well_type"], m["area_id"], m.get("team_id"),
                m.get("in_charge_user_id"), m["location"]["lat"], m["location"]["lon"], m.get("installed_on"), m.get("recorded_status"),
                (m.get("last_inspection") or {}).get("inspection_id")))
            con.execute("DELETE FROM equipment WHERE asset_id=?", (m["asset_id"],))
            for e in m.get("equipment", []):
                con.execute("INSERT INTO equipment VALUES(?,?,?,?)", (e["equipment_id"], m["asset_id"], e["kind"], e.get("model")))
            def rows(name):
                p = os.path.join(wd, name)
                return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
            for x in rows("inspections.jsonl"):
                con.execute("INSERT OR REPLACE INTO inspections VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (x["inspection_id"], x["asset_id"], x["inspected_at"], x["inspected_at"][:10],
                    x.get("inspector_user_id"), x.get("method"), x.get("ambient_temp_c"), x.get("wellhead_temp_c"), 1 if x.get("spill_detected") else 0,
                    x.get("spill_area_pct"), x.get("spill_est_volume_bbl"), x.get("notes") or "", json.dumps(x.get("evidence_images") or [])))
            for x in rows("maintenance.jsonl"):
                rt, ch = None, None
                if x.get("report_file"):
                    rp = os.path.join(wd, x["report_file"])
                    if os.path.exists(rp):
                        rt = open(rp).read()
                        ch = parse_contained_hours(rt)
                c = x.get("cost_usd") or {}
                con.execute("INSERT OR REPLACE INTO maintenance VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (x["maintenance_id"], x["asset_id"], x.get("started_at"), x.get("completed_at"),
                    x.get("maintenance_type"), x.get("equipment_kind"), x.get("issue"), x.get("action_taken"), x.get("technician_user_id"), x.get("contractor"),
                    x.get("downtime_hours"), c.get("labor"), c.get("parts"), c.get("total"), x.get("triggered_by_inspection_id"), x.get("report_file"), ch, rt))
            for x in rows("regulatory-events.jsonl"):
                con.execute("INSERT OR REPLACE INTO reg_events VALUES(?,?,?,?,?,?,?,?,?,?,?)", (x["event_id"], x["asset_id"], x.get("date"), x.get("agency"), x.get("event_type"),
                    x.get("protocol_id"), x.get("related_inspection_id"), x.get("detail"), x.get("hours_to_report"), x.get("fine_usd"), x.get("status")))
            for x in rows("context.jsonl"):
                con.execute("INSERT OR REPLACE INTO notes VALUES(?,?,?,?,?,?,?,?,?)", (x["note_id"], x["asset_id"], x.get("created_at"), x.get("author_user_id"),
                    x.get("note_type"), x.get("inspection_id"), x.get("text"), x.get("valid_from"), x.get("valid_to")))
    con.commit()
    n = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ["wells", "inspections", "maintenance", "reg_events", "notes", "documents"]}
    con.close()
    return n

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--reset-memory"]
    if "--reset-memory" in sys.argv and os.path.exists(DB_PATH):
        c = sqlite3.connect(DB_PATH)
        for t in ["memory_conversations", "memory_well_facts", "memory_corrections", "memory_type_rules"]:
            c.execute(f"DROP TABLE IF EXISTS {t}")
        c.commit(); c.close()
    print(load(args or [os.path.join(os.path.dirname(__file__), "..", "..", "dataset", "sample-data")]))
