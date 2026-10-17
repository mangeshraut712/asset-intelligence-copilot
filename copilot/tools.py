"""Deterministic, tested tools over the SQLite store. Every result carries citations."""
import os, re, sqlite3, datetime as dt
from collections import defaultdict
from .loader import DB_PATH

TODAY = dt.date.fromisoformat(os.environ.get("AIC_TODAY", "2026-10-17"))

def db():
    c = sqlite3.connect(DB_PATH, check_same_thread=False); c.row_factory = sqlite3.Row; return c

def d(s): return dt.date.fromisoformat(s[:10])
def fmt(s): x = d(s) if isinstance(s, str) else s; return f"{x.day} {x.strftime('%b %Y')}"
def sub_months(x, n):
    m = x.month - 1 - n; y = x.year + m // 12; m = m % 12 + 1
    import calendar; return dt.date(y, m, min(x.day, calendar.monthrange(y, m)[1]))

def window(months=None, days=None, year=None):
    """'last N months/days' -> inclusive [start, end] ending yesterday (the last full day before 'today')."""
    end = TODAY - dt.timedelta(days=1)
    if year: return dt.date(year, 1, 1), min(dt.date(year, 12, 31), end)
    if months: return sub_months(end, months), end
    if days: return TODAY - dt.timedelta(days=days), end
    return dt.date(1900, 1, 1), end

def rule(c, key, default=None):
    r = c.execute("SELECT value, source FROM rules WHERE key=?", (key,)).fetchone()
    return (r["value"], r["source"]) if r else (default, "default")

def user_name(c, uid):
    r = c.execute("SELECT name FROM users WHERE user_id=?", (uid,)).fetchone(); return r["name"] if r else uid

def user_id(c, name):
    r = c.execute("SELECT user_id FROM users WHERE lower(name)=lower(?) OR user_id=?", (name, name)).fetchone(); return r["user_id"] if r else name

def area_id(c, text):
    """Resolve 'Northeast Block 7', 'NE-7', 'block 7' to an area_id."""
    if not text: return None
    t = text.lower()
    for r in c.execute("SELECT area_id, name FROM areas"):
        if r["area_id"].lower() == t or r["name"].lower() == t: return r["area_id"]
    m = re.search(r"(north ?east|south ?west|north ?west|south ?east|ne|sw|nw|se)?[ -]*(?:block)?[ -]*(\d+)", t)
    if m:
        for r in c.execute("SELECT area_id, name FROM areas"):
            num = re.search(r"(\d+)$", r["area_id"]).group(1)
            if num == m.group(2) and (not m.group(1) or r["name"].lower().replace(" ", "").startswith(m.group(1).replace(" ", "")[:5]) or r["area_id"].lower().startswith(m.group(1)[:2])):
                return r["area_id"]
    return None

def area_name(c, aid):
    r = c.execute("SELECT name FROM areas WHERE area_id=?", (aid,)).fetchone(); return r["name"] if r else aid

def wells_in(c, area=None, well_type=None):
    q, a = "SELECT * FROM wells WHERE 1=1", []
    if area: q += " AND area_id=?"; a.append(area)
    if well_type: q += " AND well_type=?"; a.append(well_type)
    return [dict(r) for r in c.execute(q + " ORDER BY asset_id", a)]

# ---------- effective inspections (raw + note corrections + runtime corrections) ----------
def effective_inspections(c, asset_ids=None, start=None, end=None):
    q, a = "SELECT i.*, w.well_type, w.area_id FROM inspections i JOIN wells w USING(asset_id) WHERE 1=1", []
    if asset_ids is not None:
        q += f" AND i.asset_id IN ({','.join('?'*len(asset_ids))})"; a += list(asset_ids)
    if start: q += " AND i.date>=?"; a.append(str(start))
    if end: q += " AND i.date<=?"; a.append(str(end))
    rows = [dict(r) for r in c.execute(q + " ORDER BY i.asset_id, i.inspected_at", a)]
    corr_notes = {r["inspection_id"]: dict(r) for r in c.execute("SELECT * FROM notes WHERE note_type='correction' AND inspection_id IS NOT NULL")}
    mem = defaultdict(list)
    for r in c.execute("SELECT * FROM memory_corrections ORDER BY id"): mem[r["inspection_id"]].append(dict(r))
    thr = {k.split(".")[0]: v for k, v in c.execute("SELECT key, value FROM rules WHERE key LIKE '%.producing_delta_c'")}
    for r in rows:
        r["corrections"] = []
        if r["inspection_id"] in corr_notes and r["spill_detected"]:
            n = corr_notes[r["inspection_id"]]
            r["spill_detected"] = 0; r["spill_voided_by"] = n["note_id"]
            r["corrections"].append({"source": n["note_id"], "field": "spill_detected", "by": user_name(c, n["author_user_id"]), "text": n["text"]})
        for m in mem.get(r["inspection_id"], []):
            f = m["field"]; v = m["corrected_value"]
            r[f + "_original"] = r.get(f)
            r[f] = float(v) if f not in ("spill_detected",) else int(float(v))
            r["corrections"].append({"source": f"memory_corrections#{m['id']}", "field": f, "original": m["original_value"], "corrected": v,
                                     "by": user_name(c, m["author_user_id"]), "reason": m["reason"]})
        r["delta"] = round(r["wellhead_temp_c"] - r["ambient_temp_c"], 1)
        r["threshold"] = thr.get(r["well_type"], 15.0)
        r["producing"] = r["delta"] >= r["threshold"]
    return rows

def spill_rows(c, asset_ids=None, start=None, end=None):
    return [r for r in effective_inspections(c, asset_ids, start, end) if r["spill_detected"]]

# ---------- tools ----------
def well_status(asset_id):
    c = db(); w = c.execute("SELECT * FROM wells WHERE asset_id=?", (asset_id,)).fetchone()
    if not w: return {"error": f"{asset_id} not found"}
    w = dict(w); ins = effective_inspections(c, [asset_id])
    last = ins[-1]; cites = [last["inspection_id"], f"{w['well_type']} manual"]
    reasons = []
    if not last["producing"]:
        for m in c.execute("SELECT * FROM maintenance WHERE asset_id=? AND date(started_at)<=? AND (completed_at IS NULL OR date(completed_at)>=?) ORDER BY started_at",
                           (asset_id, last["date"], last["date"])):
            reasons.append(f"Repair {m['maintenance_id']}: {m['issue']} (started {fmt(m['started_at'])}, " + ("still open" if d(m["completed_at"]) >= TODAY else f"done {fmt(m['completed_at'])}") + ")")
            cites.append(m["maintenance_id"])
    for n in c.execute("SELECT * FROM notes WHERE asset_id=? AND note_type!='correction' AND (valid_to IS NULL OR valid_to>=?) AND valid_from<=? ORDER BY created_at",
                       (asset_id, last["date"], str(TODAY))):
        if n["valid_to"] and (not last["producing"] or "shut" in n["text"].lower()):
            reasons.append(f"Note {n['note_id']} by {user_name(c, n['author_user_id'])}: {n['text']}"); cites.append(n["note_id"])
    facts = shared_facts(c, asset_id)
    stale = (w["recorded_status"] == "active") != last["producing"]
    status = {"asset_id": asset_id, "well_type": w["well_type"], "area": area_name(c, w["area_id"]), "producing": last["producing"],
              "last_inspection_id": last["inspection_id"], "inspected_at": last["inspected_at"], "inspector": user_name(c, last["inspector_user_id"]),
              "method": last["method"], "wellhead_c": last["wellhead_temp_c"], "ambient_c": last["ambient_temp_c"], "delta_c": last["delta"],
              "threshold_c": last["threshold"], "recorded_status": w["recorded_status"], "recorded_status_stale": stale,
              "inspector_note": last["notes"], "reasons": reasons, "corrections": last["corrections"], "shared_facts": facts,
              "lat": w["lat"], "lon": w["lon"], "citations": cites}
    return status

def shared_facts(c, asset_id):
    return [dict(r) | {"author": user_name(c, r["author_user_id"])} for r in c.execute("SELECT * FROM memory_well_facts WHERE asset_id=? ORDER BY id", (asset_id,))]

def area_not_producing(area):
    c = db(); aid = area_id(c, area); out = []
    for w in wells_in(c, aid):
        s = well_status(w["asset_id"])
        if not s["producing"]: out.append(s)
    return {"area": area_name(c, aid), "wells": out, "citations": [s["last_inspection_id"] for s in out]}

def temp_series(asset_id, weeks=13):
    c = db(); ins = effective_inspections(c, [asset_id])[-weeks:]
    return {"asset_id": asset_id, "points": [{"date": r["date"], "inspection_id": r["inspection_id"], "wellhead": r["wellhead_temp_c"], "ambient": r["ambient_temp_c"],
            "delta": r["delta"], "producing": r["producing"]} for r in ins], "threshold": ins[-1]["threshold"] if ins else None,
            "citations": [ins[0]["inspection_id"] + " … " + ins[-1]["inspection_id"]] if ins else []}

def spills(asset_ids=None, area=None, start=None, end=None):
    c = db()
    if area: asset_ids = [w["asset_id"] for w in wells_in(c, area_id(c, area))]
    allrows = [r for r in effective_inspections(c, asset_ids, start, end)]
    real = [r for r in allrows if r["spill_detected"]]
    voided = [r for r in allrows if r.get("spill_voided_by")]
    wl = {w["asset_id"]: w for w in wells_in(c)}
    rows = [{"asset_id": r["asset_id"], "date": r["date"], "inspected_at": r["inspected_at"], "inspection_id": r["inspection_id"], "volume_bbl": r["spill_est_volume_bbl"],
             "volume_original": r.get("spill_est_volume_bbl_original"), "area_pct": r["spill_area_pct"], "lat": wl[r["asset_id"]]["lat"], "lon": wl[r["asset_id"]]["lon"],
             "corrections": r["corrections"]} for r in real]
    return {"spills": rows, "count": len(rows), "total_bbl": round(sum(r["volume_bbl"] or 0 for r in rows), 1),
            "excluded": [{"inspection_id": r["inspection_id"], "date": r["date"], "by": r["spill_voided_by"]} for r in voided],
            "citations": [r["inspection_id"] for r in rows] + [r["spill_voided_by"] for r in voided]}

def downtime(asset_ids, start, end):
    """7 days per non-producing inspection in [start,end]; cause = overlapping repair or valid note."""
    c = db(); res = []
    for aid in asset_ids:
        ins = [r for r in effective_inspections(c, [aid], start, end) if not r["producing"]]
        events = []
        for r in ins:
            cause = []
            for m in c.execute("SELECT * FROM maintenance WHERE asset_id=? AND (triggered_by_inspection_id=? OR (date(started_at)<=? AND date(completed_at)>=date(?,'-6 day')))",
                               (aid, r["inspection_id"], r["date"], r["date"])):
                cause.append(f"{m['issue']} ({m['maintenance_id']})")
            for n in c.execute("SELECT * FROM notes WHERE asset_id=? AND note_type!='correction' AND valid_from<=? AND (valid_to IS NULL OR valid_to>=?)", (aid, r["date"], r["date"])):
                cause.append(f"{n['text']} ({n['note_id']})")
            events.append({"date": r["date"], "inspection_id": r["inspection_id"], "wellhead": r["wellhead_temp_c"], "ambient": r["ambient_temp_c"], "delta": r["delta"],
                           "cause": "; ".join(dict.fromkeys(cause)) or "no recorded cause"})
        w = c.execute("SELECT well_type FROM wells WHERE asset_id=?", (aid,)).fetchone()
        res.append({"asset_id": aid, "well_type": w["well_type"] if w else None, "days": 7 * len(ins), "events": events})
    return res

def downtime_ranking(area, start, end, n=3):
    c = db(); ids = [w["asset_id"] for w in wells_in(c, area_id(c, area))]
    r = sorted(downtime(ids, start, end), key=lambda x: (-x["days"], x["asset_id"]))
    return {"area": area_name(c, area_id(c, area)), "start": str(start), "end": str(end), "top": r[:n], "next": r[n] if len(r) > n else None, "all": r}

def spill_heatmap(year):
    c = db(); s, e = window(year=year)
    rows = spill_rows(c, None, s, e); grid = defaultdict(lambda: defaultdict(int))
    for r in rows: grid[area_name(c, r["area_id"])][int(r["date"][5:7])] += 1
    months = list(range(1, e.month + 1))
    areas = [area_name(c, a["area_id"]) for a in c.execute("SELECT area_id FROM areas ORDER BY rowid")]
    return {"x": [dt.date(2000, m, 1).strftime("%b") for m in months], "y": areas,
            "z": [[grid[a][m] for m in months] for a in areas], "totals": {a: sum(grid[a].values()) for a in areas},
            "citations": ["inspections (spill_detected, corrections applied)", "context.jsonl correction notes"]}

def classify(c, vol):
    rep, _ = rule(c, "spill.reportable_bbl", 5); maj, _ = rule(c, "spill.major_bbl", 25); mod, _ = rule(c, "spill.moderate_bbl", 1)
    return "major" if vol >= maj else "reportable" if vol >= rep else "moderate" if vol >= mod else "minor"

def spill_compliance(c, r):
    """Check one effective spill row against SR-01/02/03 and RC-04."""
    out = {"breaches": [], "open": [], "met": [], "citations": [r["inspection_id"]]}
    vol = r["spill_est_volume_bbl"] or 0; cls = classify(c, vol); disc = dt.datetime.fromisoformat(r["inspected_at"].replace("Z", "+00:00"))
    sr01, _ = rule(c, "SR-01.hours", 24); sr02, _ = rule(c, "SR-02.hours", 4); sr03, _ = rule(c, "SR-03.days", 60); rc04, _ = rule(c, "RC-04.days", 30)
    evs = [dict(e) for e in c.execute("SELECT * FROM reg_events WHERE related_inspection_id=? ORDER BY date", (r["inspection_id"],))]
    out["citations"] += [e["event_id"] for e in evs]
    if cls in ("reportable", "major"):
        limit = 2 if cls == "major" else sr01
        rep = [e for e in evs if e["event_type"] == "spill_report_filed"]
        if rep:
            h = rep[0]["hours_to_report"]
            (out["breaches"] if h > limit else out["met"]).append({"rule": "SR-01", "detail": f"written notice after {h:g} h vs {limit:g} h limit ({rep[0]['event_id']})"})
        else:
            due = disc + dt.timedelta(hours=limit)
            out["breaches" if due.date() < TODAY else "open"].append({"rule": "SR-01", "detail": f"no written notice on record; was due by {due.strftime('%d %b %Y %H:%M')} UTC, {limit:g} h after discovery at the {disc.strftime('%d %b %Y %H:%M')} inspection"})
        vdue = disc.date() + dt.timedelta(days=sr03)
        ver = [e for e in evs if e["protocol_id"] == "SR-03"]
        closed = any(e["status"] == "closed" and "pass" in (e["detail"] or "").lower() for e in ver)
        if not closed:
            item = {"rule": "SR-03", "detail": f"agency clean-up verification due by {fmt(vdue)}" + (f", still open ({', '.join(e['event_id'] for e in ver)})" if ver else ", none recorded")}
            (out["breaches"] if vdue < TODAY else out["open"]).append(item)
    for nov in [e for e in evs if e["event_type"] == "notice_of_violation"]:
        due = d(nov["date"]) + dt.timedelta(days=rc04)
        resp = [e for e in evs if e["event_type"] == "nov_response_filed"]
        if nov["status"] == "open": out["open"].append({"rule": nov["protocol_id"], "detail": f"notice of violation {nov['event_id']}, fine USD {nov['fine_usd']:,.0f}, still open", "fine": nov["fine_usd"]})
        if not resp and due < TODAY: out["breaches"].append({"rule": "RC-04", "detail": f"response to {nov['event_id']} was due by {fmt(due)}; none recorded"})
    m = c.execute("SELECT * FROM maintenance WHERE triggered_by_inspection_id=? AND contained_hours IS NOT NULL", (r["inspection_id"],)).fetchone()
    if m:
        out["contained_hours"] = m["contained_hours"]; out["citations"].append(m["maintenance_id"])
        (out["breaches"] if m["contained_hours"] > sr02 else out["met"]).append({"rule": "SR-02", "detail": f"contained after about {m['contained_hours']:g} h vs {sr02:g} h limit (report {m['maintenance_id']})"})
        if cls in ("reportable", "major") and re.search(r"moderate", m["report_text"] or "", re.I) and r.get("spill_est_volume_bbl_original") is not None:
            out["open"].append({"rule": "note", "detail": f"report {m['maintenance_id']} classed the spill as moderate based on the old estimate ({r['spill_est_volume_bbl_original']} bbl); that no longer holds"})
    out["class"] = cls; out["volume_bbl"] = vol
    return out

def rca_check(area=None, equipment_kind=None, asset_ids=None, ref_date=None):
    """Wells with >= N corrective repairs on the same equipment kind in the 12 months before today. N from manual, overridable per well type by users."""
    c = db(); ids = asset_ids or [w["asset_id"] for w in wells_in(c, area_id(c, area) if area else None)]
    s = sub_months(TODAY, 12); out = []; applied_rules = {}
    for aid in ids:
        wt = c.execute("SELECT well_type FROM wells WHERE asset_id=?", (aid,)).fetchone()["well_type"]
        n, src = rule(c, f"{wt}.rca_repairs", 3)
        ur = c.execute("SELECT * FROM memory_type_rules WHERE well_type=? AND rule_key='rca_repairs' ORDER BY id DESC", (wt,)).fetchone()
        if ur: n, src = ur["value"], f"rule from {user_name(c, ur['author_user_id'])} ({ur['ts'][:10]}), overrides manual"; applied_rules[wt] = src
        q = "SELECT equipment_kind, group_concat(maintenance_id) ids, count(*) n FROM maintenance WHERE asset_id=? AND maintenance_type='corrective' AND date(started_at)>=? AND date(started_at)<?"
        a = [aid, str(s), str(TODAY)]
        if equipment_kind: q += " AND equipment_kind=?"; a.append(equipment_kind)
        for r in c.execute(q + " GROUP BY equipment_kind", a):
            if r["n"] >= n: out.append({"asset_id": aid, "well_type": wt, "equipment_kind": r["equipment_kind"], "repairs": r["n"], "threshold": int(n), "rule_source": src, "maintenance_ids": r["ids"].split(",")})
    return {"wells": out, "user_rules": applied_rules, "citations": [i for o in out for i in o["maintenance_ids"]] + ["T200 manual §10", "T350 manual §6"]}

def compliance(asset_id, months=12):
    c = db(); s, e = window(months=months)
    res = {"asset_id": asset_id, "breaches": [], "open": [], "met": [], "citations": []}
    for r in spill_rows(c, [asset_id], s, e):
        x = spill_compliance(c, r)
        for k in ("breaches", "open", "met"):
            for i in x[k]: res[k].append(i | {"spill": f"{fmt(r['date'])} ({r['spill_est_volume_bbl']} bbl, {r['inspection_id']})"})
        res["citations"] += x["citations"]
    for o in rca_check(asset_ids=[asset_id])["wells"]:
        res["open"].append({"rule": "RCA", "detail": f"root-cause analysis due on {o['equipment_kind']}: {o['repairs']} corrective repairs in 12 months ({', '.join(o['maintenance_ids'])})"})
        res["citations"] += o["maintenance_ids"]
    ft = c.execute("SELECT * FROM maintenance WHERE asset_id=? AND issue LIKE '%flowline integrity test%' ORDER BY started_at DESC", (asset_id,)).fetchone()
    if ft:
        (res["met"] if d(ft["started_at"]).year == TODAY.year else res["open"]).append({"rule": "RC-02", "detail": (f"annual flowline integrity test done {fmt(ft['started_at'])}" if d(ft['started_at']).year == TODAY.year else f"no flowline integrity test yet in {TODAY.year}; last one {fmt(ft['started_at'])}") + f" ({ft['maintenance_id']})"})
        res["citations"].append(ft["maintenance_id"])
    for n in c.execute("SELECT * FROM notes WHERE asset_id=? AND text LIKE '%not yet in the maintenance system%' AND (valid_to IS NULL OR valid_to>=?)", (asset_id, str(TODAY - dt.timedelta(days=7)))):
        res["open"].append({"rule": "Manual §4", "detail": f"planned shut-in not yet recorded in the maintenance system, which the manual requires before work starts ({n['note_id']})"}); res["citations"].append(n["note_id"])
    res["fines_open"] = sum(i.get("fine", 0) for i in res["open"])
    return res

def containment_breaches(area, days=90):
    c = db(); s, e = window(days=days); ids = [w["asset_id"] for w in wells_in(c, area_id(c, area))]
    lim, src = rule(c, "SR-02.hours", 4); out = []
    for r in spill_rows(c, ids, s, e):
        m = c.execute("SELECT * FROM maintenance WHERE triggered_by_inspection_id=? AND contained_hours IS NOT NULL", (r["inspection_id"],)).fetchone()
        if m and m["contained_hours"] > lim:
            out.append({"asset_id": r["asset_id"], "date": r["date"], "inspection_id": r["inspection_id"], "volume_bbl": r["spill_est_volume_bbl"], "contained_hours": m["contained_hours"], "report": m["maintenance_id"]})
    return {"area": area_name(c, area_id(c, area)), "limit_h": lim, "rows": out, "citations": [x["report"] for x in out] + [x["inspection_id"] for x in out] + [src]}

def reportable_spills(area, days=90):
    c = db(); s, e = window(days=days); ids = [w["asset_id"] for w in wells_in(c, area_id(c, area))]
    rep, _ = rule(c, "spill.reportable_bbl", 5); out = []
    for r in spill_rows(c, ids, s, e):
        if (r["spill_est_volume_bbl"] or 0) >= rep:
            out.append({"asset_id": r["asset_id"], "date": r["date"], "inspection_id": r["inspection_id"], "volume_bbl": r["spill_est_volume_bbl"], "corrections": r["corrections"], "compliance": spill_compliance(c, r)})
    return {"area": area_name(c, area_id(c, area)), "threshold": rep, "rows": out, "citations": [x["inspection_id"] for x in out] + ["Spill Response SOP SR-01"]}

def repair_costs(asset_ids, year=None):
    c = db(); year = year or TODAY.year; out = []
    for aid in asset_ids:
        rows = [dict(r) for r in c.execute("SELECT maintenance_id, cost_total FROM maintenance WHERE asset_id=? AND substr(started_at,1,4)=?", (aid, str(year)))]
        out.append({"asset_id": aid, "total_usd": sum(r["cost_total"] or 0 for r in rows), "jobs": len(rows), "maintenance_ids": [r["maintenance_id"] for r in rows]})
    return {"year": year, "rows": out, "citations": [f"maintenance.jsonl ({len(o['maintenance_ids'])} jobs for {o['asset_id']})" for o in out]}

def spill_detail(asset_id, date_text=None):
    """Spill on a given date with all notes on that inspection (to surface disagreements)."""
    c = db(); ins = effective_inspections(c, [asset_id])
    cand = [r for r in ins if r["spill_detected"] or r.get("spill_voided_by")]
    if date_text: cand = [r for r in cand if date_text in r["date"]] or cand
    if not cand: return {"error": "no spill found"}
    r = cand[-1]
    notes = [dict(n) | {"author": user_name(c, n["author_user_id"])} for n in c.execute("SELECT * FROM notes WHERE asset_id=? AND (inspection_id=? OR text LIKE ?)", (asset_id, r["inspection_id"], f"%{r['inspection_id']}%"))]
    rep = [dict(m) for m in c.execute("SELECT maintenance_id, issue FROM maintenance WHERE triggered_by_inspection_id=?", (r["inspection_id"],))]
    return {"asset_id": asset_id, "inspection_id": r["inspection_id"], "date": r["date"], "volume_bbl": r["spill_est_volume_bbl"], "inspector_note": r["notes"],
            "stands": bool(r["spill_detected"]), "notes": notes, "repairs": rep, "corrections": r["corrections"],
            "citations": [r["inspection_id"]] + [n["note_id"] for n in notes] + [m["maintenance_id"] for m in rep]}

def search_docs(query, k=3):
    """Simple keyword retrieval over manuals/SOPs and repair reports (section-level)."""
    c = db(); stop = {"the", "what", "which", "how", "does", "for", "and", "are", "is", "when", "with", "this", "that", "our", "any", "must", "within", "show", "tell"}
    terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2 and t not in stop]; hits = []
    for r in c.execute("SELECT doc_id, text FROM documents"):
        for sec in re.split(r"\n(?=#+ |\| \*\*)", r["text"]):
            s = sum(sec.lower().count(t) for t in terms)
            if s: hits.append((s, r["doc_id"], sec.strip()[:600]))
    hits.sort(reverse=True)
    return {"hits": [{"doc": h[1], "text": h[2]} for h in hits[:k]], "citations": [h[1] for h in hits[:k]]}
