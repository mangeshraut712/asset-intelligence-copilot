"""Copilot agent: memory + feedback handling, intent routing (rule-based or LLM tool-calling), answer + visual composition."""
import json, os, re, datetime as dt
from . import tools as T
from .tools import db, fmt, window, user_name, TODAY

WELL_RE = re.compile(r"WELL-\d{4}", re.I)
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
VISUALS = [("heatmap", "heatmap"), ("map", "map"), ("bar chart", "bar"), ("bar", "bar"), ("line chart", "line"), ("line", "line"), ("table", "table"), ("card", "card"), ("list", "table")]

SIM_DAY = None  # evaluation can simulate "day N" so that "yesterday" works in one run
def now():
    t = dt.datetime.now()
    if SIM_DAY is not None: t = dt.datetime.combine(TODAY + dt.timedelta(days=SIM_DAY), t.time())
    return t.isoformat(timespec="seconds")

def parse_date(text):
    m = re.search(r"(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:\s+(\d{4}))?", text, re.I)
    if not m: return None
    y = int(m.group(3)) if m.group(3) else TODAY.year
    x = dt.date(y, MONTHS[m.group(2).lower()[:3]], int(m.group(1)))
    if not m.group(3) and x > TODAY + dt.timedelta(days=60): x = x.replace(year=y - 1)
    return x

def asked_visual(q):
    ql = q.lower()
    for k, v in VISUALS:
        if re.search(rf"\b{k}\b", ql): return v
    return None

def area_from(c, q):
    m = re.search(r"((?:north|south)\s*(?:east|west)\s+block\s+\d+|\b(?:NE|SW|NW|SE)-\d+\b)", q, re.I)
    return T.area_id(c, m.group(1)) if m else None

def period_from(q):
    ql = q.lower()
    m = re.search(r"last (\d+) (month|day|week|year)s?", ql)
    if m:
        n, u = int(m.group(1)), m.group(2)
        return window(months=n) if u == "month" else window(days=n) if u == "day" else window(days=7 * n) if u == "week" else window(months=12 * n)
    if "last 12 months" in ql or "past year" in ql: return window(months=12)
    m = re.search(r"\b(?:in|during|for)\s+(20\d\d)\b", ql) or re.search(r"\b(20\d\d)\b", ql)
    if m: return window(year=int(m.group(1)))
    if "this summer" in ql: return dt.date(TODAY.year, 6, 1), dt.date(TODAY.year, 8, 31)
    if "this year" in ql: return window(year=TODAY.year)
    return None

class Copilot:
    def __init__(self):
        self.c = db()

    # ---------------- memory ----------------
    def remember(self, user, chat, q, ans, wells):
        self.c.execute("INSERT INTO memory_conversations(user_id,chat_id,ts,question,answer,wells) VALUES(?,?,?,?,?,?)",
                       (user, chat, now(), q, ans[:4000], json.dumps(wells))); self.c.commit()

    def earlier_wells(self, user, chat):
        r = self.c.execute("SELECT * FROM memory_conversations WHERE user_id=? AND chat_id!=? AND wells!='[]' AND substr(ts,1,10)<? ORDER BY id DESC LIMIT 1", (user, chat, now()[:10])).fetchone()
        return (json.loads(r["wells"]), r) if r else (None, None)

    # ---------------- entry ----------------
    def ask(self, question, user="U-201", chat="default"):
        user = T.user_id(self.c, user)
        res = None
        if os.environ.get("AIC_LLM", "1") != "0" and llm_available():
            try: res = llm_route(self, question, user, chat)
            except Exception as e: res = None; print("LLM failed, falling back:", e)
        if res is None: res = self.route(question, user, chat)
        v = asked_visual(question)
        if v and not res.get("visual") and res.get("alt_visual"): res["visual"] = res["alt_visual"]
        res.pop("alt_visual", None)
        if v and res.get("visual") and res["visual"]["type"] != v: res["visual"] = convert_visual(res["visual"], v)
        self.remember(user, chat, question, res["text"], res.get("wells", []))
        res["user"] = user_name(self.c, user); res["engine"] = res.get("engine", "rules")
        return res

    def route(self, q, user, chat):
        c = self.c; ql = q.lower(); wells = [w.upper() for w in WELL_RE.findall(q)]; area = area_from(c, q)
        is_q = q.strip().endswith("?") or re.match(r"^(is|are|was|were|which|what|how|show|list|when|who|why|did|does|do|give|find|can)\b", ql)
        # --- feedback / statements ---
        if not is_q:
            if re.search(r"all (t\d{3}) wells", ql): return self.type_rule(q, user)
            if wells and re.search(r"(wrong|faulty|re-?measured|measured|estimated|correct)", ql): return self.correction(q, user, wells[0])
            if wells: return self.statement(q, user, wells[0])
        if re.search(r"(discussed|talked about|we looked at).*(yesterday|earlier|before|last time)|wells we discussed", ql):
            ws, conv = self.earlier_wells(user, chat)
            if not ws: return {"text": f"I have no earlier conversation with {user_name(c, user)} that mentions wells, so I can't tell which wells you mean. (Private memory is per user; I don't use other users' chats.) Which wells do you mean?", "visual": None, "citations": [], "wells": []}
            pre = f"From your earlier conversation ({conv['ts'][:16]}: \"{conv['question']}\") the wells were {', '.join(ws)}. "
            if "cost" in ql or "spent" in ql: return self.costs(ws, q, pre)
            wells = ws
        if "heatmap" in ql or ("by" in ql and "month" in ql and ("area" in ql or "block" in ql)): return self.heatmap(q)
        if re.search(r"root.cause|\brca\b", ql): return self.rca(q, area, wells)
        if re.search(r"contain", ql): return self.containment(q, area)
        if re.search(r"report(ed)? to the regulator|reportable|needed a report|regulator report", ql): return self.reportable(q, area)
        if re.search(r"rules?.*(broken|break|breach)|broken.*rules|compliance|violat", ql) and wells: return self.compliance(wells[0])
        if wells and re.search(r"real oil|was the .*spill|really (a )?spill", ql): return self.spill_dispute(wells[0], q)
        if re.search(r"planned|scheduled downtime|shut.?in planned", ql) and wells: return self.planned(wells[0])
        if "cost" in ql and wells: return self.costs(wells, q)
        if re.search(r"down(time)?|days .*down|not producing.*(longest|most)", ql) and re.search(r"how many days|longest|most|downtime|days", ql):
            return self.downtime(q, wells, area)
        if not wells and not area and re.search(r"threshold|limit|\brules?\b|\bsop\b|manual|deadline|how (long|soon|many hours)|protocol|what does|define|definition", ql):
            return self.docs(q)
        if "spill" in ql: return self.spills(q, wells, area)
        if re.search(r"temperature|line chart|trend", ql) and wells: return self.temps(q, wells[0])
        if area and re.search(r"producing|down|running|stopped", ql): return self.area_status(area)
        if wells: return self.status(wells[0])
        h = T.search_docs(q)
        return {"text": "I couldn't map this to a data tool. Relevant passages from the manuals/SOPs:\n\n" + "\n\n".join(f"**{x['doc']}**: {x['text']}" for x in h["hits"]),
                "visual": None, "citations": h["citations"], "wells": []}

    # ---------------- answers ----------------
    def status(self, w):
        s = T.well_status(w)
        if "error" in s: return {"text": s["error"], "visual": None, "citations": [], "wells": []}
        t = [f"**{w} is {'producing' if s['producing'] else 'not producing'} oil** (as of its latest inspection)."]
        t.append(f"Latest inspection {s['last_inspection_id']} on {fmt(s['inspected_at'])}, by {s['method']}, by {s['inspector']}. Wellhead {s['wellhead_c']} °C vs air {s['ambient_c']} °C: {s['delta_c']} °C warmer, {'at/above' if s['producing'] else 'below'} the {s['well_type']} limit of {s['threshold_c']:g} °C.")
        for cr in s["corrections"]:
            if cr.get("original") is not None:
                t.append(f"⚠ This reading was corrected by {cr['by']}: {cr['field']} {cr['original']} → {cr['corrected']} ({cr['reason']}). Original kept for reference.")
        if s["inspector_note"]:
            conflict = s["producing"] and re.search(r"not moving|no stroke|stopped|not running", s["inspector_note"], re.I)
            t.append(f"Inspector note on that inspection: \"{s['inspector_note']}\"" + (" — this disagrees with the corrected reading; please confirm." if conflict else ""))
        if not s["producing"]:
            t.append("Reason: " + (" ".join(s["reasons"]) if s["reasons"] else "no recorded reason in repairs or notes. Suggest a site check."))
        for f in s["shared_facts"]:
            t.append(f"Shared context from {f['author']} ({f['ts'][:10]}, {f['status']}): \"{f['text']}\"" + (f" — {f['conflict']}" if f["conflict"] else ""))
        if s["recorded_status_stale"]: t.append(f"The recorded status still says **{s['recorded_status']}**, which is out of date.")
        cites = s["citations"] + [x["source"] for x in s["corrections"]]
        return {"text": "\n\n".join(t), "visual": {"type": "card", "data": s}, "citations": cites, "wells": [w]}

    def area_status(self, area):
        r = T.area_not_producing(area); rows = []
        for s in r["wells"]:
            reason = "; ".join(s["reasons"]) or "No recorded reason" + (f". Inspector noted \"{s['inspector_note']}\"" if s["inspector_note"] else "") + " — suggest a site check"
            corr = [f"{x['field']} corrected by {x['by']}" for x in s["corrections"] if x.get("original") is not None]
            rows.append({"Well": s["asset_id"], "Type": s["well_type"], "Last inspected": fmt(s["inspected_at"]), "Wellhead above air (°C)": s["delta_c"],
                         "Recorded status": s["recorded_status"] + (" (out of date)" if s["recorded_status_stale"] else ""), "Reason": reason, "Inspection": s["last_inspection_id"]})
        txt = f"**{len(rows)} wells in {r['area']} are not producing oil right now** (latest inspection per well): {', '.join(x['Well'] for x in rows)}."
        corrected = self.c.execute("SELECT mc.*, w.area_id FROM memory_corrections mc JOIN wells w USING(asset_id) WHERE w.area_id=? AND field='wellhead_temp_c'", (T.area_id(self.c, area),)).fetchall()
        for cr in corrected:
            if cr["asset_id"] not in [x["Well"] for x in rows]:
                txt += f"\n\n{cr['asset_id']} is no longer listed: its {cr['inspection_id']} wellhead reading was corrected by {user_name(self.c, cr['author_user_id'])} from {cr['original_value']} to {cr['corrected_value']} °C ({cr['reason']}), so it now counts as producing."
        return {"text": txt, "visual": {"type": "table", "columns": list(rows[0].keys()) if rows else [], "rows": rows}, "citations": r["citations"] + ["T200/T350 manual production rule"], "wells": [x["Well"] for x in rows]}

    def temps(self, q, w):
        m = re.search(r"(\d+)\s*weeks", q.lower()); n = int(m.group(1)) if m else 13
        r = T.temp_series(w, n); down = [fmt(p["date"]) for p in r["points"] if not p["producing"]]
        txt = f"{len(r['points'])} readings for {w} ({fmt(r['points'][0]['date'])} to {fmt(r['points'][-1]['date'])}). Not producing oil on: {', '.join(down) or 'none'} (wellhead less than {r['threshold']:g} °C above air)."
        return {"text": txt, "visual": {"type": "line", "x": [p["date"] for p in r["points"]], "series": [{"name": "Wellhead °C", "data": [p["wellhead"] for p in r["points"]]}, {"name": "Air °C", "data": [p["ambient"] for p in r["points"]]}],
                "marks": [p["date"] for p in r["points"] if not p["producing"]], "mark_label": "not producing"}, "citations": r["citations"], "wells": [w]}

    def spills(self, q, wells, area):
        p = period_from(q) or (None, None); ql = q.lower()
        r = T.spills(wells or None, area if not wells else None, p[0], p[1])
        rows = [{"Well": s["asset_id"], "Date": fmt(s["date"]), "Barrels": s["volume_bbl"], "Inspection": s["inspection_id"], "Lat": s["lat"], "Lon": s["lon"]} for s in r["spills"]]
        scope = ", ".join(wells) if wells else T.area_name(self.c, area) if area else "the field"
        txt = f"**{r['count']} real spills for {scope}" + (f" ({fmt(p[0])} to {fmt(p[1])})" if p[0] else "") + f", {r['total_bbl']} barrels in total.**"
        if r["excluded"]: txt += f" {len(r['excluded']) + r['count']} detections; excluded as corrected: " + ", ".join(f"{e['inspection_id']} ({fmt(e['date'])}, {e['by']})" for e in r["excluded"]) + "."
        for s in r["spills"]:
            for cr in s["corrections"]:
                if cr.get("original"): txt += f"\n\n{s['inspection_id']}: volume corrected by {cr['by']} from {cr['original']} to {cr['corrected']} bbl."
        vis = {"type": "map", "points": [{"lat": s["lat"], "lon": s["lon"], "label": f"{s['asset_id']} · {fmt(s['date'])} · {s['volume_bbl']} bbl"} for s in r["spills"]]} if ("map" in ql or "where" in ql) else \
              {"type": "table", "columns": ["Well", "Date", "Barrels", "Inspection"], "rows": rows}
        if vis["type"] == "map":
            latest = {}
            for s in r["spills"]: latest[s["asset_id"]] = s
            vis["points"] = [{"lat": s["lat"], "lon": s["lon"], "label": f"{s['asset_id']} · {fmt(s['date'])} · {s['volume_bbl']} bbl"} for s in latest.values()]
            txt += f" {len(latest)} wells: " + "; ".join(f"{s['asset_id']} ({fmt(s['date'])}, {s['volume_bbl']} bbl, {s['lat']}, {s['lon']})" for s in latest.values())
        return {"text": txt, "visual": vis, "citations": r["citations"] + ["Dataset Guide: correction notes override detections"], "wells": sorted({s["asset_id"] for s in r["spills"]})}

    def downtime(self, q, wells, area):
        p = period_from(q) or window(); ql = q.lower()
        if wells and not area:
            r = T.downtime(wells, *p); rows = []
            txt = []
            for x in r:
                txt.append(f"**{x['asset_id']} was down {x['days']} days** ({fmt(p[0])}–{fmt(p[1])}), from {len(x['events'])} weekly inspections where it was not producing oil:")
                for e in x["events"]:
                    txt.append(f"- {fmt(e['date'])} ({e['inspection_id']}): wellhead {e['wellhead']} °C vs air {e['ambient']} °C, only {e['delta']} °C warmer. Cause: {e['cause']}.")
                    rows.append({"Well": x["asset_id"], "Date": fmt(e["date"]), "Delta °C": e["delta"], "Cause": e["cause"], "Inspection": e["inspection_id"]})
            return {"text": "\n".join(txt) + "\n\nDowntime = 7 days per non-producing weekly inspection (Dataset Guide).", "visual": None,
                    "alt_visual": {"type": "table", "columns": ["Well", "Date", "Delta °C", "Cause", "Inspection"], "rows": rows},
                    "citations": [e["inspection_id"] for x in r for e in x["events"]] + ["Dataset Guide (downtime)", "well-type manual"], "wells": wells}
        m = re.search(r"\b(\d+|three|five|ten)\b (?:wells|assets)", ql); n = int({"three": "3", "five": "5", "ten": "10"}.get(m.group(1), m.group(1))) if m else 5
        r = T.downtime_ranking(area, *p, n=n)
        txt = f"**Top {n} wells in {r['area']} by downtime ({fmt(p[0])} to {fmt(p[1])}):** " + ", ".join(f"{x['asset_id']}: {x['days']} days ({x['well_type']})" for x in r["top"])
        if r["next"]: txt += f". Next is {r['next']['asset_id']} at {r['next']['days']}."
        for x in r["top"]:
            causes = list(dict.fromkeys(e["cause"] for e in x["events"]))[:3]
            txt += f"\n- {x['asset_id']} why: " + "; ".join(causes)
        return {"text": txt, "visual": {"type": "bar", "x": [x["asset_id"] for x in r["top"]], "series": [{"name": "Downtime (days)", "data": [x["days"] for x in r["top"]]}]},
                "citations": [e["inspection_id"] for x in r["top"] for e in x["events"]] + ["Dataset Guide (downtime = 7 d per non-producing inspection)"], "wells": [x["asset_id"] for x in r["top"]]}

    def heatmap(self, q):
        m = re.search(r"(20\d\d)", q); y = int(m.group(1)) if m else TODAY.year
        h = T.spill_heatmap(y)
        txt = f"Real spills in {y} by area and month (corrected detections removed). Totals: " + ", ".join(f"{a}: {t}" for a, t in h["totals"].items())
        return {"text": txt, "visual": {"type": "heatmap", "x": h["x"], "y": h["y"], "z": h["z"]}, "citations": h["citations"], "wells": []}

    def compliance(self, w):
        r = T.compliance(w)
        txt = [f"**{w}: {len(r['breaches'])} rule breaches in the last 12 months**" + (f", USD {r['fines_open']:,.0f} in fines still open." if r["fines_open"] else ".")]
        txt += [f"- **{b['rule']}** ({b.get('spill', '')}): {b['detail']}" for b in r["breaches"]]
        txt.append("\n**Still open / pending:**"); txt += [f"- {o['rule']}: {o['detail']}" for o in r["open"]]
        txt.append("\n**Met:**"); txt += [f"- {m['rule']}: {m['detail']}" for m in r["met"]]
        rows = [{"Status": "Breach", "Rule": b["rule"], "Detail": b["detail"]} for b in r["breaches"]] + [{"Status": "Open", "Rule": o["rule"], "Detail": o["detail"]} for o in r["open"]]
        return {"text": "\n".join(txt), "visual": {"type": "table", "columns": ["Status", "Rule", "Detail"], "rows": rows}, "citations": list(dict.fromkeys(r["citations"])) + ["Spill Response SOP", "Regulatory Compliance SOP"], "wells": [w]}

    def containment(self, q, area):
        p = re.search(r"last (\d+) days", q.lower()); r = T.containment_breaches(area, int(p.group(1)) if p else 90)
        rows = [{"Well": x["asset_id"], "Date": fmt(x["date"]), "Contained after (h)": x["contained_hours"], "Report": x["report"], "Inspection": x["inspection_id"]} for x in r["rows"]]
        txt = f"**{len(rows)} spills in {r['area']} were not contained within the {r['limit_h']:g}-hour SOP limit (SR-02):** " + "; ".join(f"{x['Well']} after about {x['Contained after (h)']:g} h (report {x['Report']}, inspection {x['Inspection']})" for x in rows) + ". Containment times come from the free-text repair reports."
        return {"text": txt, "visual": {"type": "table", "columns": list(rows[0].keys()) if rows else [], "rows": rows}, "citations": r["citations"], "wells": [x["Well"] for x in rows]}

    def reportable(self, q, area):
        p = re.search(r"last (\d+) days", q.lower()); r = T.reportable_spills(area, int(p.group(1)) if p else 90); rows = []; txt = []
        for x in r["rows"]:
            corr = [cr for cr in x["corrections"] if cr.get("original")]
            br = [b for b in x["compliance"]["breaches"] + x["compliance"]["open"] if b["rule"] in ("SR-01", "SR-03")]
            txt.append(f"- {x['asset_id']}: {x['volume_bbl']} bbl on {fmt(x['date'])} ({x['inspection_id']})" + (f", volume corrected by {corr[0]['by']} from {corr[0]['original']}" if corr else "") + ". " + " ".join(f"{b['rule']}: {b['detail']}." for b in br))
            rows.append({"Well": x["asset_id"], "Date": fmt(x["date"]), "Barrels": x["volume_bbl"], "Status": "; ".join(f"{b['rule']}: {b['detail']}" for b in br)})
        head = f"**{len(rows)} spill(s) in {r['area']} in the last 90 days reached the {r['threshold']:g} bbl reporting threshold (Spill Response SOP SR-01):**" if rows else f"No spill in {r['area']} reached {r['threshold']:g} bbl."
        return {"text": head + "\n" + "\n".join(txt) + ("\nNo other spill in that period reached the threshold." if rows else ""), "visual": {"type": "table", "columns": list(rows[0].keys()) if rows else [], "rows": rows},
                "citations": r["citations"] + [i for x in r["rows"] for i in x["compliance"]["citations"]], "wells": [x["Well"] for x in rows]}

    def rca(self, q, area, wells):
        kind = next((k for k in ["pump_jack", "flowline", "rod_string", "downhole_pump", "separator", "wellhead"] if k.replace("_", " ") in q.lower() or k in q.lower()), None)
        r = T.rca_check(area, kind, wells or None)
        rows = [{"Well": x["asset_id"], "Type": x["well_type"], "Equipment": x["equipment_kind"], "Corrective repairs (12 mo)": x["repairs"], "Threshold": x["threshold"], "Rule source": x["rule_source"], "Repairs": ", ".join(x["maintenance_ids"])} for x in r["wells"]]
        txt = f"**{len(rows)} wells need a root-cause analysis{' on their ' + kind.replace('_', ' ') if kind else ''}:** " + ", ".join(f"{x['Well']} ({x['Corrective repairs (12 mo)']} repairs, {x['Type']})" for x in rows) + ". Rule: T200 manual §10 (≥3 corrective repairs on the same equipment in 12 months; the T350 manual refers to it)."
        for wt, src in r["user_rules"].items(): txt += f"\n\nFor {wt} wells I applied a {src}, not the manual."
        return {"text": txt, "visual": {"type": "table", "columns": list(rows[0].keys()) if rows else [], "rows": rows}, "citations": r["citations"], "wells": [x["Well"] for x in rows]}

    def costs(self, ws, q, pre=""):
        p = period_from(q); y = p[0].year if p else TODAY.year
        r = T.repair_costs(ws, y)
        txt = pre + f"**Repair costs in {y}:** " + " · ".join(f"{x['asset_id']}: USD {x['total_usd']:,.0f} ({x['jobs']} jobs)" for x in r["rows"])
        return {"text": txt, "visual": {"type": "bar", "x": [x["asset_id"] for x in r["rows"]], "series": [{"name": f"Repair cost {y} (USD)", "data": [x["total_usd"] for x in r["rows"]]}]}, "citations": [i for x in r["rows"] for i in x["maintenance_ids"]], "wells": ws}

    def spill_dispute(self, w, q):
        dd = parse_date(q); r = T.spill_detail(w, str(dd)[5:] if dd else None)
        if "error" in r: return {"text": r["error"], "visual": None, "citations": [], "wells": [w]}
        disagree = len(r["notes"]) >= 2
        txt = f"**{'Yes' if r['stands'] else 'No'}** — the AI flagged a {r['volume_bbl']} bbl spill at {r['inspection_id']} on {fmt(r['date'])} (\"{r['inspector_note']}\")."
        if r["notes"]:
            txt += " Notes on it:\n" + "\n".join(f"- {n['author']} ({n['note_id']}, {n['note_type']}): \"{n['text']}\"" for n in r["notes"])
        if disagree: txt += "\n\nThese notes **disagree**. Neither is a formal correction"
        if r["repairs"]: txt += f"{'' if disagree else chr(10)}, and a spill repair ({', '.join(m['maintenance_id'] for m in r['repairs'])}) was done, so the detection stands."
        if r["corrections"]: txt += "\nCorrections: " + "; ".join(json.dumps(x) for x in r["corrections"])
        return {"text": txt, "visual": {"type": "table", "columns": ["Source", "Author", "Says"], "rows": [{"Source": n["note_id"], "Author": n["author"], "Says": n["text"]} for n in r["notes"]]}, "citations": r["citations"], "wells": [w]}

    def planned(self, w):
        facts = T.shared_facts(self.c, w)
        notes = self.c.execute("SELECT * FROM notes WHERE asset_id=? AND note_type!='correction' AND (valid_to IS NULL OR valid_to>=?) AND valid_from IS NOT NULL ORDER BY created_at DESC", (w, str(TODAY))).fetchall()
        mnt = self.c.execute("SELECT * FROM maintenance WHERE asset_id=? AND date(completed_at)>=?", (w, str(TODAY))).fetchall()
        items = [f"{f['text']} — according to {f['author']} ({f['ts'][:10]}, shared note)" for f in facts if re.search(r"shut|planned|workover|maintenance|down", f["text"], re.I)]
        items += [f"{n['text']} — note {n['note_id']} by {user_name(self.c, n['author_user_id'])}" for n in notes if re.search(r"shut|planned|workover|down", n["text"], re.I)]
        items += [f"Repair {m['maintenance_id']} ({m['issue']}) planned until {fmt(m['completed_at'])}" for m in mnt]
        txt = (f"**Yes, downtime is planned for {w}:**\n" + "\n".join("- " + i for i in items)) if items else f"No planned downtime is recorded for {w}."
        return {"text": txt, "visual": None, "citations": [f"memory_well_facts#{f['id']}" for f in facts] + [n["note_id"] for n in notes] + [m["maintenance_id"] for m in mnt], "wells": [w]}

    def docs(self, q):
        h = T.search_docs(q, k=3)
        rules = [dict(r) for r in self.c.execute("SELECT * FROM rules")]
        txt = "From the manuals and SOPs:\n\n" + "\n\n".join(f"**{x['doc']}**\n> " + x["text"].replace("\n", "\n> ") for x in h["hits"])
        return {"text": txt, "visual": {"type": "table", "columns": ["Rule", "Value", "Source"], "rows": [{"Rule": r["key"], "Value": r["value"], "Source": r["source"]} for r in rules]},
                "citations": h["citations"], "wells": []}

    # ---------------- feedback ----------------
    def correction(self, q, user, w):
        c = self.c; ql = q.lower(); dd = parse_date(q); name = user_name(c, user)
        nums = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*(?:°\s*c|bbl|barrels|c\b)", ql)]
        ins = T.effective_inspections(c, [w]); target = None
        if dd: target = next((r for r in ins if r["date"] == str(dd)), None)
        if "spill" in ql or "bbl" in ql:
            field = "spill_est_volume_bbl"; target = target or next((r for r in reversed(ins) if r["spill_detected"]), None)
        else:
            field = "ambient_temp_c" if re.search(r"\b(air|ambient)\b", ql) and "wellhead" not in ql else "wellhead_temp_c"; target = target or ins[-1]
        if not target or not nums: return {"text": "I couldn't tell which inspection or value to correct. Please name the well, the date and the corrected value.", "visual": None, "citations": [], "wells": [w]}
        new = nums[-1]; orig = target.get(field + "_original", target[field])
        reason = re.sub(r"\s+", " ", q.strip())
        c.execute("INSERT INTO memory_corrections(inspection_id,asset_id,field,original_value,corrected_value,author_user_id,ts,reason) VALUES(?,?,?,?,?,?,?,?)",
                  (target["inspection_id"], w, field, str(orig), str(new), user, now(), reason)); c.commit()
        after = next(r for r in T.effective_inspections(c, [w]) if r["inspection_id"] == target["inspection_id"])
        txt = [f"Recorded: **{target['inspection_id']}** ({fmt(target['date'])}) {field} corrected from {orig} to {new} by {name}. The original value is kept; the correction applies to every later answer for every user."]
        cites = [target["inspection_id"]]
        if field != "spill_est_volume_bbl":
            txt.append(f"With {after['wellhead_temp_c']} °C against {after['ambient_temp_c']} °C air ({after['delta']} °C warmer, {'above' if after['producing'] else 'below'} the {after['well_type']} limit of {after['threshold']:g} °C), {w} is **{'producing' if after['producing'] else 'not producing'} oil**.")
            if after["notes"] and after["producing"] and re.search(r"not moving|no stroke|stopped|not running", after["notes"], re.I):
                cf = f"inspection note \"{after['notes']}\" ({user_name(c, after['inspector_user_id'])}) disagrees"
                txt.append(f"⚠ Conflict: the same inspection has the note \"{after['notes']}\" by {user_name(c, after['inspector_user_id'])}, which disagrees with the corrected reading. {name}, can you confirm?")
                c.execute("UPDATE memory_corrections SET conflict=? WHERE id=(SELECT max(id) FROM memory_corrections)", (cf,)); c.commit()
        else:
            comp = T.spill_compliance(c, after); cls = comp["class"]
            txt.append(f"At {new} bbl the spill is **{cls}** under the Spill Response SOP.")
            for b in comp["breaches"] + comp["open"]: txt.append(f"- {b['rule']}: {b['detail']}" + (" — possible breach" if b in comp["breaches"] else ""))
            cites += comp["citations"] + ["Spill Response SOP"]
        return {"text": "\n\n".join(txt), "visual": None, "citations": cites, "wells": [w]}

    def type_rule(self, q, user):
        c = self.c; wt = re.search(r"(t\d{3})", q.lower()).group(1).upper()
        m = re.search(r"after (\d+|two|three|four|one) repairs", q.lower()); n = {"one": 1, "two": 2, "three": 3, "four": 4}.get(m.group(1), None) if m else None
        n = n or (int(m.group(1)) if m else None)
        if n is None: return {"text": "I couldn't parse the rule value. Please state e.g. 'RCA after 2 repairs'.", "visual": None, "citations": [], "wells": []}
        c.execute("INSERT INTO memory_type_rules(well_type,rule_key,value,author_user_id,ts,text) VALUES(?,?,?,?,?,?)", (wt, "rca_repairs", n, user, now(), q)); c.commit()
        man, src = T.rule(c, f"{wt}.rca_repairs", 3)
        return {"text": f"Recorded a team rule for **all {wt} wells only**: root-cause analysis after {n} corrective repairs (manual: {man:g}, {src}). Set by {user_name(c, user)}; it applies to every user's later answers, and not to other well types.", "visual": None, "citations": [src], "wells": []}

    def statement(self, q, user, w):
        """Shared well fact. Compare with the latest inspection and other users' facts; flag conflicts."""
        c = self.c; ql = q.lower(); name = user_name(c, user); s = T.well_status(w); dd = parse_date(q)
        claims_down = bool(re.search(r"shut.?in|down|stopped|offline|workover|maintenance", ql)) and not re.search(r"back online|running fine|is running|producing", ql)
        claims_up = bool(re.search(r"back online|running|producing|is up\b|restarted", ql))
        future = dd is not None and dd > dt.date.fromisoformat(s["inspected_at"][:10])
        conflict, status, txt = None, "confirmed by data" if not future else "planned (future)", []
        if not future and (claims_up or claims_down):
            if claims_up and not s["producing"]:
                conflict = f"latest inspection {s['last_inspection_id']} ({fmt(s['inspected_at'])}, by {s['inspector']}) shows the wellhead only {s['delta_c']} °C above air, so not producing"
            if claims_down and s["producing"]:
                conflict = f"latest inspection {s['last_inspection_id']} ({fmt(s['inspected_at'])}) shows it producing ({s['delta_c']} °C above air)"
            if conflict: status = "unconfirmed (contradicts data)"
        others = [f for f in T.shared_facts(c, w) if f["author_user_id"] != user]
        c.execute("INSERT INTO memory_well_facts(asset_id,author_user_id,ts,text,kind,status,conflict) VALUES(?,?,?,?,?,?,?)", (w, user, now(), q, "down" if claims_down else "up" if claims_up else "info", status, conflict)); c.commit()
        txt.append(f"Noted for everyone: \"{q}\" — recorded as shared knowledge about {w} from {name} ({status}).")
        cites = [s["last_inspection_id"]]
        if conflict:
            txt.append(f"⚠ **This contradicts the data**: the {conflict}.")
            agree = [f for f in others if (f["kind"] == "down") == (not s["producing"])]
            for f in agree: txt.append(f"That matches {f['author']}'s note (\"{f['text']}\"), not your claim.")
            for n in s["reasons"]:
                if "Note" in n: txt.append(f"Also on record: {n}")
            txt.append(f"I've kept both statements on record and marked yours as **unconfirmed**. Can you confirm, {name}?")
        else:
            for f in others:
                if f["kind"] in ("up", "down") and f["kind"] != ("down" if claims_down else "up"):
                    txt.append(f"⚠ Note: {f['author']} said \"{f['text']}\" — these statements disagree.")
        return {"text": "\n\n".join(txt), "visual": None, "citations": cites, "wells": [w]}

def convert_visual(v, to):
    """Honor a user-requested visual type when the data allows it."""
    if to == "table":
        if v["type"] in ("bar", "line"): return {"type": "table", "columns": ["Label"] + [s["name"] for s in v["series"]], "rows": [dict([("Label", x)] + [(s["name"], s["data"][i]) for s in v["series"]]) for i, x in enumerate(v["x"])]}
        if v["type"] == "map": return {"type": "table", "columns": ["Label", "Lat", "Lon"], "rows": [{"Label": p["label"], "Lat": p["lat"], "Lon": p["lon"]} for p in v["points"]]}
        if v["type"] == "heatmap": return {"type": "table", "columns": ["Row"] + v["x"], "rows": [dict([("Row", y)] + list(zip(v["x"], v["z"][i]))) for i, y in enumerate(v["y"])]}
    if to == "bar" and v["type"] == "table":
        num = [k for k in v["columns"] if v["rows"] and isinstance(v["rows"][0].get(k), (int, float)) and k not in ("Lat", "Lon")]
        if num: return {"type": "bar", "x": [str(list(r.values())[0]) for r in v["rows"]], "series": [{"name": num[0], "data": [r[num[0]] for r in v["rows"]]}]}
    if to == "map" and v["type"] == "table" and v["rows"] and "Lat" in v["rows"][0]:
        return {"type": "map", "points": [{"lat": r["Lat"], "lon": r["Lon"], "label": str(list(r.values())[0])} for r in v["rows"]]}
    return v

# ---------------- optional LLM tool-calling layer ----------------
def llm_config():
    for k, base, model in [("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1", "google/gemma-4-31b-it:free"), ("OPENAI_API_KEY", None, "gpt-4o-mini"),
                           ("XAI_API_KEY", "https://api.x.ai/v1", "grok-4-fast"), ("GROQ_API_KEY", "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"),
                           ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/", "gemma-4-31b-it")]:
        if os.environ.get(k): return os.environ[k], os.environ.get("AIC_LLM_BASE", base), os.environ.get("AIC_LLM_MODEL", model)
    if os.environ.get("AIC_LLM_BASE"): return "ollama", os.environ["AIC_LLM_BASE"], os.environ.get("AIC_LLM_MODEL", "gemma4:e4b")
    return None

def llm_available():
    try: import openai  # noqa
    except ImportError: return False
    return llm_config() is not None

INTENTS = ["status", "area_status", "temps", "spills", "downtime", "heatmap", "compliance", "containment", "reportable", "rca", "costs", "spill_dispute", "planned", "feedback", "memory_recall", "docs"]

def llm_route(cp, q, user, chat):
    """LLM picks the tool (function call); deterministic tools compute numbers; LLM may then rewrite the prose, keeping the facts and citations."""
    from openai import OpenAI
    key, base, model = llm_config(); cl = OpenAI(api_key=key, base_url=base)
    tool = {"type": "function", "function": {"name": "route", "description": "Pick the copilot tool for the question.",
            "parameters": {"type": "object", "properties": {"intent": {"type": "string", "enum": INTENTS}, "rewritten_question": {"type": "string", "description": "Question rewritten with explicit well IDs (WELL-0001), area names (Northeast Block 7) and period words (last 4 months / in 2025) the deterministic router understands."}}, "required": ["intent", "rewritten_question"]}}}
    sysmsg = "You route oil-field operator questions to deterministic tools. Never compute numbers yourself."
    r = cl.chat.completions.create(model=model, messages=[{"role": "system", "content": sysmsg}, {"role": "user", "content": q}], tools=[tool], tool_choice="required", timeout=30)
    args = json.loads(r.choices[0].message.tool_calls[0].function.arguments)
    rq = args.get("rewritten_question") or q
    if args.get("intent") == "feedback": rq = q  # statements must be stored verbatim
    res = cp.route(rq, user, chat); res["engine"] = f"llm:{model} -> {args.get('intent')}"
    return res
