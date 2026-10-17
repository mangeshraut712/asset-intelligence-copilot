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
    m = re.search(r"((?:north|south)[\s-]*(?:east|west)\s+block\s+\d+|\b(?:NE|SW|NW|SE)-?\d+\b|\bblock\s+\d+)", q, re.I)
    return T.area_id(c, m.group(1)) if m else None

def period_from(q):
    from .query import parse_window
    w = parse_window(q)
    if w: return w[0], w[1]
    return None

def _old_period_from(q):
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

HANDLERS = ["status", "area_status", "temps", "spills", "downtime", "heatmap", "compliance", "containment", "reportable", "rca", "costs", "spill_dispute",
            "planned", "repairs", "docs", "correction", "type_rule", "statement"]
HANDLER_RULES = {"status": ["%.producing_delta_c"], "area_status": ["%.producing_delta_c"], "temps": ["%.producing_delta_c"], "downtime": ["%.producing_delta_c"],
                 "compliance": ["SR-0%", "RC-04.days", "spill.reportable_bbl", "%.rca_repairs"], "containment": ["SR-02.hours"], "reportable": ["spill.reportable_bbl", "SR-01.hours", "SR-03.days"],
                 "rca": ["%.rca_repairs"], "correction": ["%.producing_delta_c", "spill.reportable_bbl", "SR-01.hours", "SR-03.days"], "statement": ["%.producing_delta_c"]}

class Copilot:
    def __init__(self):
        self.c = db(); self.steps = []; self.rules_used = []
        for h in HANDLERS:
            f = getattr(self, h)
            def wrap(*a, _f=f, _h=h, **k):
                self.steps.append({"tool": _h, "args": [x for x in a if isinstance(x, (str, int, float, list)) and len(str(x)) < 120][:3]})
                for pat in HANDLER_RULES.get(_h, []):
                    for r in self.c.execute("SELECT key, value, source FROM rules WHERE key LIKE ?", (pat,)):
                        self.rules_used.append(f"{r['key']} = {r['value']:g} ({r['source']})")
                return _f(*a, **k)
            setattr(self, h, wrap)

    # ---------------- memory ----------------
    def remember(self, user, chat, q, ans, wells):
        self.c.execute("INSERT INTO memory_conversations(user_id,chat_id,ts,question,answer,wells) VALUES(?,?,?,?,?,?)",
                       (user, chat, now(), q, ans[:4000], json.dumps(wells))); self.c.commit()

    def earlier_wells(self, user, chat, yesterday=True):
        """Most recent conversation of THIS user (never other users) in another chat that mentioned wells.
        'yesterday' restricts to earlier days; 'earlier/before' allows earlier chats today."""
        cutoff = now()[:10] if yesterday else "9999"
        rows = self.c.execute("SELECT * FROM memory_conversations WHERE user_id=? AND chat_id!=? AND wells!='[]' AND substr(ts,1,10)<? ORDER BY id DESC LIMIT 20", (user, chat, cutoff)).fetchall()
        n = getattr(self, "_want_n", None)
        r = next((x for x in rows if n and len(json.loads(x["wells"])) == n), rows[0] if rows else None)
        return (json.loads(r["wells"]), r) if r else (None, None)

    # ---------------- entry ----------------
    def ask(self, question, user="U-201", chat="default"):
        """Rule router first. It is authoritative when it matches confidently; the LLM is only consulted
        (to pick the tool / rewrite the question) when the router falls back. AIC_LLM=force sends every question
        through the LLM (used to evaluate the LLM path); AIC_LLM=0 disables it."""
        user = T.user_id(self.c, user); self.steps = []; self.rules_used = []
        mode = os.environ.get("AIC_LLM", "auto")
        self.confident = True
        res = None if mode == "force" else self.route(question, user, chat)
        if (res is None or not self.confident) and mode != "0" and llm_available():
            try:
                self.confident = True
                alt = llm_route(self, question, user, chat)
                if self.confident or res is None: res = alt
            except Exception as e:
                print("LLM failed, using rule router:", str(e)[:200])
        if res is None: self.confident = True; res = self.route(question, user, chat)
        res.setdefault("engine", "rules")
        v = asked_visual(question)
        if v and not res.get("visual") and res.get("alt_visual"): res["visual"] = res["alt_visual"]
        res.pop("alt_visual", None)
        if v and res.get("visual") and res["visual"]["type"] != v: res["visual"] = convert_visual(res["visual"], v)
        self.remember(user, chat, question, res["text"], res.get("wells", []))
        res["user"] = user_name(self.c, user)
        txt = res["text"]
        conflict = bool(re.search(r"⚠|disagree|contradict|unconfirmed|conflict", txt, re.I))
        res["confidence"] = "conflict" if conflict else ("low" if not self.confident else "medium" if res["engine"].startswith("llm") else "high")
        res["trace"] = {"engine": res["engine"], "steps": self.steps, "rules": list(dict.fromkeys(self.rules_used)), "citations": len(set(res["citations"]))}
        res["followups"] = followups(self.steps, res.get("wells", []), question)
        return res
    def route(self, q, user, chat):
        c = self.c; ql = q.lower(); wells = [w.upper() for w in WELL_RE.findall(q)]; area = area_from(c, q)
        is_q = q.strip().endswith("?") or re.match(r"^(is|are|was|were|which|what|how|show|list|when|who|why|did|does|do|give|find|can|could|plot|compare|chart|graph|map|draw|display|tell|summari[sz]e|rank|count|get|list|break ?down|where|who)\b", ql)
        # --- feedback / statements ---
        if not is_q:
            if re.search(r"all (t\d{3}) wells", ql): return self.type_rule(q, user)
            if wells and re.search(r"(wrong|faulty|re-?measured|measured|estimated|correct)", ql): return self.correction(q, user, wells[0])
            if wells: return self.statement(q, user, wells[0])
        if re.search(r"(discussed|talked about|we looked at).*(yesterday|earlier|before|last time)|wells we discussed", ql):
            mm = re.search(r"\b(two|three|four|five|\d+) wells", ql)
            self._want_n = ({"two": 2, "three": 3, "four": 4, "five": 5}.get(mm.group(1)) or int(mm.group(1))) if mm and not mm.group(1).isalpha() or (mm and mm.group(1) in ("two", "three", "four", "five")) else None
            ws, conv = self.earlier_wells(user, chat, yesterday="yesterday" in ql)
            if not ws: return {"text": f"I have no earlier conversation with {user_name(c, user)} that mentions wells, so I can't tell which wells you mean. (Private memory is per user; I don't use other users' chats.) Which wells do you mean?", "visual": None, "citations": [], "wells": []}
            pre = f"From your earlier conversation ({conv['ts'][:16]}: \"{conv['question']}\") the wells were {', '.join(ws)}. "
            if "cost" in ql or "spent" in ql: return self.costs(ws, q, pre)
            wells = ws
        if "heatmap" in ql or ("by" in ql and "month" in ql and ("area" in ql or "block" in ql)): return self.heatmap(q)
        if not wells and not area and not re.search(r"\b(which|list|show|how many|count)\b", ql) and re.search(r"how long do|how soon|threshold|limit|\brules?\b|\bsop\b|manual|deadline|how (long|soon|many hours)|protocol|what does|define|definition", ql):
            return self.docs(q)
        if re.search(r"root.cause|\brca\b", ql): return self.rca(q, area, wells)
        if re.search(r"contain", ql): return self.containment(q, area)
        if re.search(r"report(ed)? to the regulator|reportable|needed a report|regulator report", ql): return self.reportable(q, area)
        if re.search(r"rules?.*(broken|break|breach)|broken.*rules|compliance|violat", ql) and wells: return self.compliance(wells[0])
        if wells and re.search(r"real oil|was the .*spill|really (a )?spill", ql): return self.spill_dispute(wells[0], q)
        if re.search(r"planned|scheduled downtime|shut.?in planned", ql) and wells: return self.planned(wells[0])
        if "cost" in ql and wells: return self.costs(wells, q)
        if wells and re.search(r"repair|maintenance|problem|issue|fail|broke|flowline|pump jack|rod string|downhole|separator|gearbox|history", ql) and not re.search(r"spill|temperature", ql):
            return self.repairs(q, wells[0])
        g = self.maybe_generic(q, wells, area)
        if g: return g
        if re.search(r"down(time)?|days .*down|not producing.*(longest|most)", ql) and re.search(r"how many days|longest|most|downtime|days", ql):
            return self.downtime(q, wells, area)
        if "spill" in ql: return self.spills(q, wells, area)
        if re.search(r"temperature|line chart|trend", ql) and wells: return self.temps(q, wells[0])
        if area and re.search(r"producing|down|running|stopped", ql): return self.area_status(area)
        if wells: return self.status(wells[0])
        self.confident = False
        h = T.search_docs(q)
        return {"text": "I couldn't map this to a data tool. Relevant passages from the manuals/SOPs:\n\n" + "\n\n".join(f"**{x['doc']}**: {x['text']}" for x in h["hits"]),
                "visual": None, "citations": h["citations"], "wells": []}

    # ---------------- generic composable query ----------------
    def maybe_generic(self, q, wells, area):
        from . import query as Q
        c = self.c; scope = Q.parse_scope(c, q); metric = Q.parse_metric(q); group = Q.parse_group(q); win = Q.parse_window(q); ql = q.lower()
        if not metric: return None
        broad = bool(scope.get("well_type") or scope.get("team")) or (not wells and not area)
        use = broad or group in ("area", "type", "team", "month", "equipment") or metric in ("fines", "reg_events", "stale_status", "notes") \
              or (metric in ("repairs", "repair_cost") and not wells) or (metric in ("spills", "spill_volume", "downtime") and len(wells) > 1)
        if metric == "not_producing" and area and not broad and group in (None, "well"): use = False
        if metric in ("spills", "spill_volume") and re.search(r"\bmap\b|where", ql) and not broad: use = False
        if not use: return None
        return self.generic(q, metric, scope, win, group)

    def generic(self, q, metric, scope, win, group, top=None, filters=None):
        from . import query as Q
        c = self.c; ql = q.lower(); filters = dict(filters or {})
        if "corrective" in ql or re.search(r"\bbreaks?\b|broke|fail", ql): filters["maintenance_type"] = "corrective"
        elif "scheduled" in ql: filters["maintenance_type"] = "scheduled"
        kind = next((k for k in ["pump_jack", "flowline", "rod_string", "downhole_pump", "separator", "wellhead"] if k.replace("_", " ") in ql), None)
        if kind: filters["equipment_kind"] = kind
        if re.search(r"\bopen\b|unpaid|outstanding|still", ql): filters["open"] = True
        for et in ["notice_of_violation", "spill_report_filed", "site_inspection", "nov_response_filed"]:
            if et.replace("_", " ").replace("nov ", "")[:12] in ql or (et == "notice_of_violation" and re.search(r"notices? of violation|\bnovs?\b|violation", ql)): filters["event_type"] = et; break
        if metric in ("not_producing", "stale_status") and group is None: group = "well"
        if group is None and len(scope.get("wells", [])) > 1: group = "well"
        if group is None and metric in ("spills", "spill_volume", "fines", "reg_events", "notes", "repairs", "repair_cost", "downtime") and re.search(r"\bwhich\b|\blist\b", ql): group = "well"
        m = re.search(r"top (\d+)|\b(\d+) wells|\b(three|five|ten) wells", ql)
        if m: top = int(m[1] or m[2] or {"three": 3, "five": 5, "ten": 10}[m[3]])
        if metric == "downtime" and win is None: win = (dt.date(1900, 1, 1), TODAY - dt.timedelta(days=1), "all records")
        args = {"metric": metric, "scope": scope, "window": win, "group_by": group}
        probs = Q.validate(args)
        if probs: return {"text": "I couldn't build a valid query: " + "; ".join(probs), "visual": None, "citations": [], "wells": []}
        r = Q.run_query(metric, scope, win, group, top, filters)
        if not r["rows"] and r["n_wells"] == 0 and scope:   # self-check: empty scope -> retry once without the narrowest filter
            sc = dict(scope); sc.pop("team", None) or sc.pop("well_type", None); r = Q.run_query(metric, sc, win, group, top, filters); r["retried"] = True
        lab = {"downtime": ("downtime", "days"), "spills": ("real spills", ""), "spill_volume": ("spilled oil", "bbl"), "repairs": ("repair jobs", ""), "repair_cost": ("repair cost", "USD"),
               "fines": ("regulator fines", "USD"), "reg_events": ("regulator events", ""), "not_producing": ("wells not producing oil right now", ""), "stale_status": ("wells with an out-of-date recorded status", ""), "notes": ("human notes", "")}[metric]
        an = {x["area_id"]: x["name"] for x in c.execute("SELECT * FROM areas")}; tn = {x["team_id"]: x["name"] for x in c.execute("SELECT * FROM teams")}
        sl = ", ".join(filter(None, [", ".join(scope.get("wells", [])), an.get(scope.get("area"), ""), (scope.get("well_type", "") + " wells") if scope.get("well_type") else "", tn.get(scope.get("team"), "")])) or "the whole field"
        fl = ", ".join(f"{k.replace('_', ' ')}={v}" for k, v in filters.items())
        def fv(v): return f"USD {v:,.0f}" if lab[1] == "USD" else (f"{v:g} {lab[1]}".strip())
        txt = f"**{lab[0].capitalize()} — {sl}" + (f", {win[2]}" if win else "") + (f" ({fl})" if fl else "") + f": {fv(r['total'])} in total**"
        if metric in ("not_producing", "stale_status"): txt = f"**{int(r['total'])} {lab[0] if r['total'] != 1 else lab[0].replace('wells', 'well')} — {sl}.**"
        if r.get("retried"): txt += " (no wells matched the full scope; retried with a broader scope)"
        if group and len(r["rows"]) > 1 and metric not in ("stale_status", "not_producing") and re.search(r"\bwhich\b|most|highest|worst|longest|rank|top|more", ql):
            txt += f"\n\n**Highest: {r['rows'][0]['key']} ({fv(r['rows'][0]['value'])})**"
        if group and r["rows"] and metric not in ("stale_status", "not_producing"):
            txt += "\n\n" + "\n".join(f"- {x['key']}: {fv(x['value'])}" for x in r["rows"][:15]) + (f"\n- … {len(r['rows']) - 15} more" if len(r["rows"]) > 15 else "")
        if metric == "not_producing":
            txt += "\n\n" + "\n".join(f"- {t['well']}: {t['delta']} °C above air at {t['inspection']} ({fmt(t['date'])}), recorded status {t['recorded']}" for t in r["trace"][:40])
        if metric == "stale_status":
            txt += "\n\n" + "\n".join(f"- {t['well']}: recorded **{t['recorded']}**, but {t['inspection']} ({fmt(t['date'])}) shows {'producing' if t['producing'] else 'not producing'} ({t['delta']} °C above air)" for t in r["trace"][:25])
        if metric in ("fines", "reg_events") and r["trace"]:
            txt += "\n\n" + "\n".join(f"- {t['event']} ({t['well']}, {fmt(t['date'])}): {t['type'].replace('_', ' ')}, {t['protocol']}, fine USD {t['fine'] or 0:,.0f}, {t['status']}" for t in r["trace"][:25])
        if metric == "notes" and r["trace"]:
            txt += "\n\n" + "\n".join(f"- {t['note']} ({t['well']}, {t['by']}, {t['type']}): {t['text']}" for t in r["trace"][:20])
        if r["rules"]: txt += "\n\n_Rules applied: " + "; ".join(r["rules"]) + "._"
        if not r["rows"]: txt += "\n\nNo matching records."
        # visual
        rows = r["rows"]
        if group == "month": vis = {"type": "line", "x": [x["key"] for x in rows], "series": [{"name": lab[0], "data": [x["value"] for x in rows]}]}
        elif group in ("area", "type", "team", "equipment") or (group == "well" and 1 < len(rows) <= 12 and metric not in ("not_producing", "stale_status")):
            vis = {"type": "bar", "x": [str(x["key"]) for x in rows], "series": [{"name": lab[0] + (f" ({lab[1]})" if lab[1] else ""), "data": [x["value"] for x in rows]}]}
        elif group == "well" and rows:
            wl = {x["asset_id"]: x for x in c.execute("SELECT * FROM wells")}
            vis = {"type": "table", "columns": ["Well", "Type", "Area", lab[0].capitalize(), "Evidence"], "rows": [{"Well": x["key"], "Type": wl[x["key"]]["well_type"], "Area": an[wl[x["key"]]["area_id"]], lab[0].capitalize(): x["value"], "Evidence": ", ".join(x["citations"][:4]), "Lat": wl[x["key"]]["lat"], "Lon": wl[x["key"]]["lon"]} for x in rows]}
        elif r["trace"]:
            cols = list(r["trace"][0].keys()); vis = {"type": "table", "columns": cols, "rows": r["trace"][:200]}
        else: vis = None
        self.steps.append({"tool": "run_query", "args": {"metric": metric, "scope": scope, "window": r["window"], "group_by": group, "top": top, "filters": filters}, "result": f"{len(rows)} rows, total {r['total']}"})
        self.rules_used += r["rules"]
        ws = [x["key"] for x in rows if str(x["key"]).startswith("WELL-")][:10]
        return {"text": txt, "visual": vis, "citations": r["citations"], "wells": ws}

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
                         "Recorded status": s["recorded_status"] + (" (out of date)" if s["recorded_status_stale"] else ""), "Reason": reason, "Inspection": s["last_inspection_id"], "Lat": s["lat"], "Lon": s["lon"]})
        txt = f"**{len(rows)} wells in {r['area']} are not producing oil right now** (latest inspection per well): {', '.join(x['Well'] for x in rows)}."
        corrected = self.c.execute("SELECT mc.*, w.area_id FROM memory_corrections mc JOIN wells w USING(asset_id) WHERE w.area_id=? AND field='wellhead_temp_c'", (T.area_id(self.c, area),)).fetchall()
        for cr in corrected:
            if cr["asset_id"] not in [x["Well"] for x in rows]:
                txt += f"\n\n{cr['asset_id']} is no longer listed: its {cr['inspection_id']} wellhead reading was corrected by {user_name(self.c, cr['author_user_id'])} from {cr['original_value']} to {cr['corrected_value']} °C ({cr['reason']}), so it now counts as producing."
        return {"text": txt, "visual": {"type": "table", "columns": [k for k in rows[0].keys() if k not in ("Lat", "Lon")] if rows else [], "rows": rows}, "citations": r["citations"] + ["T200/T350 manual production rule"], "wells": [x["Well"] for x in rows]}

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
                    "alt_visual": {"type": "bar", "x": [x["asset_id"] for x in r], "series": [{"name": "Downtime (days)", "data": [x["days"] for x in r]}]} if len(r) > 1 and asked_visual(q) != "table" else
                                  {"type": "table", "columns": ["Well", "Date", "Delta °C", "Cause", "Inspection"], "rows": rows},
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
        txt = [f"**{w}: {len(r['breaches'])} rule breach(es) in the last 12 months**" + (f", USD {r['fines_open']:,.0f} in fines still open." if r["fines_open"] else ".")]
        txt += [f"- **{b['rule']}** ({b.get('spill', '')}): {b['detail']}" for b in r["breaches"]]
        txt.append("\n**Still open / pending:**"); txt += [f"- {o['rule']}" + (f" ({o['spill']})" if o.get("spill") else "") + f": {o['detail']}" for o in r["open"]]
        txt.append("\n**Met:**"); txt += [f"- {m['rule']}" + (f" ({m['spill']})" if m.get("spill") else "") + f": {m['detail']}" for m in r["met"]]
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

    def repairs(self, q, w):
        p = period_from(q) or ((TODAY - dt.timedelta(days=90), TODAY) if re.search(r"lately|recent", q.lower()) else window(months=12))
        kind = next((k for k in ["pump_jack", "flowline", "rod_string", "downhole_pump", "separator", "wellhead"] if k.replace("_", " ") in q.lower()), None)
        a = [w, str(p[0]), str(p[1])]; sql = "SELECT * FROM maintenance WHERE asset_id=? AND date(started_at)>=? AND date(started_at)<=?"
        if kind: sql += " AND equipment_kind=?"; a.append(kind)
        rows = [dict(r) for r in self.c.execute(sql + " ORDER BY started_at", a)]
        corr = [r for r in rows if r["maintenance_type"] == "corrective"]
        txt = f"**{w}: {len(rows)} repair jobs{' on the ' + kind.replace('_', ' ') if kind else ''} from {fmt(p[0])} to {fmt(p[1])}** ({len(corr)} corrective, USD {sum(r['cost_total'] or 0 for r in rows):,.0f})."
        rca = T.rca_check(asset_ids=[w], equipment_kind=kind)["wells"]
        for o in rca: txt += f"\n\nRoot-cause analysis due on {o['equipment_kind']}: {o['repairs']} corrective repairs in 12 months ({o['rule_source']})."
        tr = [{"Repair": r["maintenance_id"], "Started": fmt(r["started_at"]), "Type": r["maintenance_type"], "Equipment": r["equipment_kind"], "Issue": r["issue"], "Cost USD": r["cost_total"], "Contained (h)": r["contained_hours"] or ""} for r in rows]
        return {"text": txt, "visual": {"type": "table", "columns": list(tr[0].keys()) if tr else [], "rows": tr}, "citations": [r["maintenance_id"] for r in rows] + (["T200 manual §10"] if rca else []), "wells": [w]}

    def docs(self, q):
        h = T.search_docs(q, k=3)
        rules = [dict(r) for r in self.c.execute("SELECT * FROM rules")]
        ql = q.lower(); keymap = [(r"report", ["spill.reportable_bbl", "SR-01.hours"]), (r"contain", ["SR-02.hours"]), (r"verif|clean", ["SR-03.days"]),
            (r"produc|temperature|warm", ["T200.producing_delta_c", "T350.producing_delta_c"]), (r"root|rca", ["T200.rca_repairs", "T350.rca_repairs"]), (r"notice|violation|nov", ["RC-04.days"])]
        rd = {r["key"]: r for r in rules}
        keys = [k for pat, ks in keymap if re.search(pat, ql) for k in ks if k in rd]
        lead = ("**Answer:** " + "; ".join(f"{k} = {rd[k]['value']:g} ({rd[k]['source']})" for k in keys) + "\n\n") if keys else ""
        if keys: rules = [rd[k] for k in keys] + [r for r in rules if r["key"] not in keys]
        txt = lead + "From the manuals and SOPs:\n\n" + "\n\n".join(f"**{x['doc']}**\n> " + x["text"].replace("\n", "\n> ") for x in h["hits"])
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

def followups(steps, wells, q):
    h = steps[0]["tool"] if steps else ""; w = wells[0] if wells else "WELL-0001"; out = []
    if h in ("status", "statement", "correction"): out = [f"How many days was {w} down this year?", f"Which rules has {w} broken in the last 12 months?", f"Show {w}'s temperature for the last 13 weeks"]
    elif h in ("area_status", "downtime", "run_query"): out = [f"What did repairs cost for {', '.join(wells[:3]) or w} this year?", f"Is {w} producing oil right now?", "Show downtime by area this year as a bar chart"]
    elif h in ("spills", "heatmap", "reportable", "containment"): out = [f"Which rules has {w} broken in the last 12 months?", "Which spills in the last 90 days needed a report to the regulator?", "Show spills by month in 2026"]
    elif h == "compliance": out = [f"What repairs were done on {w} in the last 12 months?", "Which wells have open fines?", "Which wells have an out-of-date recorded status?"]
    else: out = ["Which wells have an out-of-date recorded status?", "Show downtime by area this year", "Which wells have open fines?"]
    return [x for x in out if x.lower() != q.lower()][:3]

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
    """Open-weight Gemma 4 is the default: Gemini API (GEMINI_API_KEY) first, then OpenRouter, then Ollama; others only if set explicitly."""
    pref = os.environ.get("AIC_LLM_PROVIDER")
    provs = [("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/", "gemma-4-31b-it"), ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1", "google/gemma-4-31b-it:free"),
             ("OPENAI_API_KEY", None, "gpt-4o-mini"), ("XAI_API_KEY", "https://api.x.ai/v1", "grok-4-fast"), ("GROQ_API_KEY", "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile")]
    if pref: provs.sort(key=lambda p: p[0] != pref)
    for k, base, model in provs:
        if os.environ.get(k): return os.environ[k], os.environ.get("AIC_LLM_BASE", base), os.environ.get("AIC_LLM_MODEL", model)
    if os.environ.get("AIC_LLM_BASE"): return "ollama", os.environ["AIC_LLM_BASE"], os.environ.get("AIC_LLM_MODEL", "gemma4:e4b")
    return None

def llm_available():
    try: import openai  # noqa
    except ImportError: return False
    return llm_config() is not None

INTENTS = ["query", "status", "area_status", "temps", "spills", "downtime", "heatmap", "compliance", "containment", "reportable", "rca", "costs", "spill_dispute", "planned", "feedback", "memory_recall", "docs"]

CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "llm_cache.json")

def _cache():
    try: return json.load(open(CACHE_PATH))
    except Exception: return {}

def llm_pick(q):
    """One tool-call per *new* question; results cached on disk so reruns cost no requests.
    Tries a chain of free models; any error -> caller falls back to the rule router."""
    cache = _cache(); key = q.strip().lower()
    if key in cache: return cache[key]
    from openai import OpenAI
    k, base, model = llm_config(); cl = OpenAI(api_key=k, base_url=base, max_retries=0)
    fb = "google/gemma-4-26b-a4b-it:free,nvidia/nemotron-3-super-120b-a12b:free" if base and "openrouter" in base else "gemma-4-26b-a4b-it" if base and "googleapis" in base else ""
    models = [model] + [m for m in os.environ.get("AIC_LLM_FALLBACKS", fb).split(",") if m]
    tool = {"type": "function", "function": {"name": "route", "description": "Pick the copilot tool for the question.",
            "parameters": {"type": "object", "properties": {"intent": {"type": "string", "enum": INTENTS},
                "metric": {"type": "string", "enum": ["downtime", "spills", "spill_volume", "repairs", "repair_cost", "fines", "reg_events", "not_producing", "stale_status", "notes"], "description": "for intent=query"},
                "well_ids": {"type": "array", "items": {"type": "string"}}, "area": {"type": "string", "description": "area name or id"}, "well_type": {"type": "string", "enum": ["T200", "T350"]},
                "team": {"type": "string", "enum": ["TEAM-SW", "TEAM-NE"]}, "start": {"type": "string", "description": "YYYY-MM-DD"}, "end": {"type": "string", "description": "YYYY-MM-DD"},
                "group_by": {"type": "string", "enum": ["well", "area", "type", "team", "month", "equipment"]}, "top": {"type": "integer"}, "rewritten_question": {"type": "string", "description": "The question rewritten in plain words for a keyword router: keep exact well IDs (WELL-0001), write areas as 'Northeast Block 7' / 'Southwest Block 23', write periods as 'last N months', 'last N days' or 'in 2025', and keep any requested visual (table, bar chart, line chart, map, heatmap)."}}, "required": ["intent", "rewritten_question"]}}}
    sysmsg = ("You route oil-field operator questions to deterministic tools. Never compute numbers. Intents: status (one well now), area_status (wells not producing in an area), "
              "temps (temperature over time), spills, downtime, heatmap, compliance (rules broken), containment (spill containment time), reportable (spills needing regulator report), "
              "rca (root-cause analysis), costs (repair cost), spill_dispute (was a spill real), repairs (repair/maintenance history of a well), planned (planned downtime), feedback (user states a fact/correction), memory_recall, docs (manual/SOP rule). "
              f"Today is {TODAY}. Area IDs: SW-23=Southwest Block 23, SW-24=Southwest Block 24, NE-7=Northeast Block 7, NE-8=Northeast Block 8.")
    err = None
    for m in models:
        try:
            try:
                r = cl.chat.completions.create(model=m, messages=[{"role": "system", "content": sysmsg}, {"role": "user", "content": q}], tools=[tool], tool_choice="required", timeout=float(os.environ.get('AIC_LLM_TIMEOUT', 20)))
                tc = r.choices[0].message.tool_calls
                args = json.loads(tc[0].function.arguments) if tc else {}
            except Exception as e1:   # endpoints without tool calling: ask for the same JSON in plain text
                r = cl.chat.completions.create(model=m, messages=[{"role": "system", "content": sysmsg + " Reply ONLY with a JSON object with keys matching this schema: " + json.dumps(tool["function"]["parameters"]["properties"])}, {"role": "user", "content": q}], timeout=float(os.environ.get('AIC_LLM_TIMEOUT', 20)))
                mm = re.search(r"\{.*\}", r.choices[0].message.content or "", re.S); args = json.loads(mm.group(0)) if mm else {}
            if args.get("intent"):
                args["model"] = m; cache[key] = args
                json.dump(cache, open(CACHE_PATH, "w"), indent=1); return args
        except Exception as e: err = e
    raise RuntimeError(f"all LLM models failed: {err}")

def llm_route(cp, q, user, chat):
    """LLM as planner: either a structured composable query (validated, self-checked) or a tool intent + rewritten question."""
    from . import query as Q
    args = llm_pick(q); intent = args.get("intent"); eng = f"llm:{args.get('model')} -> {intent}"
    if intent == "query" and args.get("metric") in Q.METRICS and re.match(r"^(is|are|was|were|which|what|how|show|list|when|who|why|did|does|do|give|find|can|could|plot|compare|rank|count|tell|where|total)\b", q.lower()):
        cp.confident = True; probe = cp.route(q, user, chat)
        if cp.confident:   # rule router is authoritative when it matches confidently
            probe["engine"] = eng + " (rule router confident; used its tool)"; return probe
        cp.steps.clear()
    if intent == "query" and args.get("metric") in Q.METRICS:
        scope = {}
        if args.get("well_ids"): scope["wells"] = [w.upper() for w in args["well_ids"]]
        if args.get("area"): scope["area"] = T.area_id(cp.c, args["area"]) or args["area"]
        if args.get("well_type"): scope["well_type"] = args["well_type"]
        if args.get("team"): scope["team"] = args["team"]
        win = None
        try:
            if args.get("start") and args.get("end"):
                s, e = dt.date.fromisoformat(args["start"]), min(dt.date.fromisoformat(args["end"]), TODAY - dt.timedelta(days=1)); win = (s, e, f"{fmt(s)} to {fmt(e)}")
        except ValueError: win = None
        win = Q.parse_window(q) or win   # deterministic parse wins when it finds a window
        plan = {"metric": args["metric"], "scope": scope, "window": win, "group_by": args.get("group_by") or Q.parse_group(q)}
        if not Q.validate(plan) and (not scope.get("area") or scope["area"] in [r["area_id"] for r in cp.c.execute("SELECT area_id FROM areas")]):
            res = cp.generic(q, args["metric"], scope, win, plan["group_by"], args.get("top"))
            if res.get("visual") or "No matching records" not in res["text"]:
                res["engine"] = eng; return res
        cp.steps.append({"tool": "self_check", "result": "planner query invalid or empty; retrying with rewritten question"})
    rq = q if intent == "feedback" else (args.get("rewritten_question") or q)
    res = cp.route(rq, user, chat); res["engine"] = eng
    return res
