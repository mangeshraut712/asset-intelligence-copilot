"""Proactive field briefing and evidence lookup."""
import re, json, time
from . import tools as T
from .tools import fmt, TODAY
from . import query as Q

_cache = {"key": None, "val": None}

def briefing():
    c = T.db()
    key = (c.execute("SELECT count(*) FROM memory_corrections").fetchone()[0], c.execute("SELECT count(*) FROM memory_type_rules").fetchone()[0], c.execute("SELECT count(*) FROM wells").fetchone()[0])
    if _cache["key"] == key: return _cache["val"]
    t0 = time.time(); s12, e = T.window(months=12)
    breaches = []
    for aid in sorted({r["asset_id"] for r in T.spill_rows(c, None, s12, e)}):
        for b in T.compliance(aid)["breaches"]:
            breaches.append({"well": aid, "rule": b["rule"], "detail": b["detail"], "spill": b.get("spill", "")})
    stale = Q.run_query("stale_status", {}, None, "well")["trace"]
    long_down = []
    for w in T.wells_in(c):
        ins = T.effective_inspections(c, [w["asset_id"]], TODAY.replace(year=TODAY.year - 1))
        n = 0
        for r in reversed(ins):
            if r["producing"]: break
            n += 1
        if n * 7 > 14: long_down.append({"well": w["asset_id"], "days": n * 7, "since": ins[-n]["date"], "citations": [r["inspection_id"] for r in ins[-n:]]})
    fines = [dict(r) for r in c.execute("SELECT * FROM reg_events WHERE status='open' AND fine_usd>0 ORDER BY date DESC")]
    reportable = []
    s90, _ = T.window(days=90)
    for r in T.spill_rows(c, None, s90, e):
        if (r["spill_est_volume_bbl"] or 0) >= T.rule(c, "spill.reportable_bbl", 5)[0] and not c.execute("SELECT 1 FROM reg_events WHERE related_inspection_id=? AND event_type='spill_report_filed'", (r["inspection_id"],)).fetchone():
            reportable.append({"well": r["asset_id"], "inspection": r["inspection_id"], "date": r["date"], "bbl": r["spill_est_volume_bbl"]})
    val = {"generated_in_s": round(time.time() - t0, 2), "as_of": str(TODAY),
           "cards": [
               {"id": "breaches", "title": "SOP breaches (12 mo)", "count": len(breaches), "severity": "high", "items": [{"text": f"{b['well']} · {b['rule']}: {b['detail']}", "cite": re.findall(r"(?:REG|MNT|INS)-\d{4}-\d{3,4}", b["detail"] + b["spill"])} for b in breaches]},
               {"id": "unreported", "title": "Reportable spills with no notice (90 d)", "count": len(reportable), "severity": "high", "items": [{"text": f"{x['well']} · {x['bbl']} bbl on {fmt(x['date'])}", "cite": [x["inspection"]]} for x in reportable]},
               {"id": "fines", "title": "Open fines", "count": len(fines), "severity": "med", "total": sum(f["fine_usd"] for f in fines), "items": [{"text": f"{f['asset_id']} · USD {f['fine_usd']:,.0f} · {f['protocol_id']} ({fmt(f['date'])})", "cite": [f["event_id"]]} for f in fines]},
               {"id": "down", "title": "Down > 14 days (RC-03)", "count": len(long_down), "severity": "med", "items": [{"text": f"{x['well']} · {x['days']} days since {fmt(x['since'])}", "cite": x["citations"][-1:]} for x in sorted(long_down, key=lambda x: -x["days"])]},
               {"id": "stale", "title": "Stale recorded status", "count": len(stale), "severity": "low", "items": [{"text": f"{x['well']} · recorded {x['recorded']}, inspection says {'producing' if x['producing'] else 'not producing'}", "cite": [x["inspection"]]} for x in stale]}]}
    _cache.update(key=key, val=val); return val

DOCMAP = [(r"spill response|SR-0\d", "fleet/sops/spill-response-sop.md"), (r"regulatory compliance|RC-0\d", "fleet/sops/regulatory-compliance-sop.md"),
          (r"field work|WS-0\d", "fleet/sops/field-work-sop.md"), (r"T350", "fleet/well-types/T350.md"), (r"T200", "fleet/well-types/T200.md")]

def evidence(ref):
    c = T.db(); ref = ref.strip()
    m = re.match(r"(INS|MNT|REG|CTX)-\d{4}-\d{3,4}", ref)
    if m:
        k = m.group(0); tbl, col = {"INS": ("inspections", "inspection_id"), "MNT": ("maintenance", "maintenance_id"), "REG": ("reg_events", "event_id"), "CTX": ("notes", "note_id")}[m.group(1)]
        r = c.execute(f"SELECT * FROM {tbl} WHERE {col}=?", (k,)).fetchone()
        if not r: return {"ref": ref, "error": "not found"}
        rec = dict(r); text = rec.pop("report_text", None)
        out = {"ref": k, "kind": tbl, "record": rec}
        if tbl == "inspections":
            out["corrections"] = [dict(x) for x in c.execute("SELECT * FROM memory_corrections WHERE inspection_id=?", (k,))] + [dict(x) for x in c.execute("SELECT note_id, author_user_id, text FROM notes WHERE inspection_id=? OR text LIKE ?", (k, f"%{k}%"))]
        if text:
            out["document"] = rec.get("report_file"); out["text"] = text
            out["highlight"] = [l for l in text.splitlines() if re.search(r"contained|Not met|Action required|reportable|moderate|root cause", l, re.I)][:8]
        return out
    m = re.match(r"memory_(corrections|well_facts)#(\d+)", ref)
    if m: r = c.execute(f"SELECT * FROM memory_{m.group(1)} WHERE id=?", (int(m.group(2)),)).fetchone(); return {"ref": ref, "kind": "runtime memory", "record": dict(r) if r else None}
    for pat, doc in DOCMAP:
        if re.search(pat, ref, re.I):
            d = c.execute("SELECT text FROM documents WHERE doc_id=?", (doc,)).fetchone()
            if not d: continue
            pid = re.search(r"(SR|RC|WS)-0\d", ref); sec = re.search(r"§\s*(\d+)", ref)
            hl = []
            if pid: hl = [l for l in d["text"].splitlines() if pid.group(0) in l][:3]
            elif sec: hl = [l for l in d["text"].splitlines() if re.match(rf"#+ {sec.group(1)}\.", l)]
            elif "production" in ref.lower() or "producing" in ref.lower(): hl = [l for l in d["text"].splitlines() if "above" in l and "°C" in l][:2]
            return {"ref": ref, "kind": "document", "document": doc, "text": d["text"], "highlight": hl}
    return {"ref": ref, "kind": "note", "text": ref}
