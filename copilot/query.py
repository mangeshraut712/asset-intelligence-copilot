"""Composable query tool: metric x scope (well/area/type/team/field) x window x group-by.
Parsing is deterministic; the LLM planner can also call run_query() directly with validated args."""
import re, calendar, datetime as dt
from collections import defaultdict
from . import tools as T
from .tools import TODAY, fmt

MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m} | {m.lower(): i for i, m in enumerate(calendar.month_abbr) if m}
NUMW = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twelve": 12}
METRICS = ["downtime", "spills", "spill_volume", "repairs", "repair_cost", "fines", "reg_events", "not_producing", "stale_status", "notes"]
GROUPS = [None, "well", "area", "type", "team", "month", "equipment"]

def _date(s, default_year=None):
    s = s.strip().lower().replace(",", "")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m: return dt.date(int(m[1]), int(m[2]), int(m[3]))
    m = re.match(r"(\d{1,2})(?:st|nd|rd|th)? ([a-z]+)(?: (\d{4}))?", s) or None
    if m and m[2] in MONTHS: return dt.date(int(m[3] or default_year or TODAY.year), MONTHS[m[2]], int(m[1]))
    m = re.match(r"([a-z]+) (\d{1,2})(?:st|nd|rd|th)?(?: (\d{4}))?", s)
    if m and m[1] in MONTHS: return dt.date(int(m[3] or default_year or TODAY.year), MONTHS[m[1]], int(m[2]))
    return None

def parse_window(q):
    """Return (start, end, label) or None. 'last N' windows end yesterday (the last full day before today)."""
    ql = q.lower(); end = TODAY - dt.timedelta(days=1)
    if re.search(r"right now|currently|at the moment|latest inspection", ql): return None
    m = re.search(r"between (.+?) and (.+?)(?:[?.,]|$| show| as | in a| on a)", ql)
    if m:
        a, b = _date(m[1]), _date(m[2])
        if a and b: return a, b, f"{fmt(a)} to {fmt(b)}"
    m = re.search(r"(?:from|since) (\d{1,2} [a-z]+(?: \d{4})?|[a-z]+ \d{1,2}(?: \d{4})?|\d{4}-\d{2}-\d{2})", ql)
    if m and _date(m[1]):
        a = _date(m[1]); return a, end, f"{fmt(a)} to {fmt(end)}"
    m = re.search(r"(?:last|past|previous) (\d+|" + "|".join(NUMW) + r") (day|week|month|year)s?", ql)
    if m:
        n = int(NUMW.get(m[1], m[1]) if not m[1].isdigit() else m[1]); u = m[2]
        s = T.sub_months(end, n) if u == "month" else T.sub_months(end, 12 * n) if u == "year" else TODAY - dt.timedelta(days=n * (7 if u == "week" else 1))
        return s, end, f"last {n} {u}s ({fmt(s)} to {fmt(end)})"
    if re.search(r"\blast year\b", ql): y = TODAY.year - 1; return dt.date(y, 1, 1), dt.date(y, 12, 31), str(y)
    if re.search(r"(?:last|past) (year|12 months)", ql): s = T.sub_months(end, 12); return s, end, f"last 12 months ({fmt(s)} to {fmt(end)})"
    if re.search(r"(?:last|past) (month)\b", ql): s = T.sub_months(end, 1); return s, end, f"last month ({fmt(s)} to {fmt(end)})"
    m = re.search(r"(summer|winter|spring|autumn|fall)(?: (?:of )?(\d{4}))?", ql)
    if m and ("this " + m[1] in ql or m[2] or "last " + m[1] in ql):
        y = int(m[2]) if m[2] else TODAY.year - (1 if "last " + m[1] in ql else 0)
        rng = {"summer": ((6, 1), (8, 31)), "spring": ((3, 1), (5, 31)), "autumn": ((9, 1), (11, 30)), "fall": ((9, 1), (11, 30))}.get(m[1])
        if m[1] == "winter": s, e = dt.date(y - 1, 12, 1), dt.date(y, 2, calendar.monthrange(y, 2)[1])
        else: s, e = dt.date(y, *rng[0]), dt.date(y, *rng[1])
        return s, min(e, end), f"{m[1]} {y} ({fmt(s)} to {fmt(min(e, end))})"
    mon = "|".join(k for k in MONTHS if len(k) > 3 or k in ("may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", "jan", "feb", "mar", "apr"))
    m = re.search(rf"\b(?:in|during|for|of)\s+({mon})\b(?:\s+(\d{{4}}))?", ql)
    if m:
        mo = MONTHS[m[1]]; y = int(m[2]) if m[2] else (TODAY.year if mo <= TODAY.month else TODAY.year - 1)
        s, e = dt.date(y, mo, 1), dt.date(y, mo, calendar.monthrange(y, mo)[1]); return s, min(e, end), f"{calendar.month_name[mo]} {y}"
    m = re.search(r"\b(first|second) half(?: of)?(?: (\d{4}))?|\bh([12])(?: (\d{4}))?", ql)
    if m:
        h = 1 if (m[1] == "first" or m[3] == "1") else 2; y = int(m[2] or m[4] or TODAY.year)
        s, e = (dt.date(y, 1, 1), dt.date(y, 6, 30)) if h == 1 else (dt.date(y, 7, 1), dt.date(y, 12, 31)); return s, min(e, end), f"H{h} {y} ({fmt(s)} to {fmt(min(e, end))})"
    m = re.search(r"\bq([1-4])(?: (\d{4}))?|\b(first|second|third|fourth) quarter(?: of)?(?: (\d{4}))?", ql)
    if m:
        k = int(m[1]) if m[1] else ["first", "second", "third", "fourth"].index(m[3]) + 1; y = int(m[2] or m[4] or TODAY.year)
        s = dt.date(y, 3 * k - 2, 1); e = dt.date(y, 3 * k, calendar.monthrange(y, 3 * k)[1]); return s, min(e, end), f"Q{k} {y} ({fmt(s)} to {fmt(min(e, end))})"
    if "this year" in ql or "year to date" in ql or "ytd" in ql: return dt.date(TODAY.year, 1, 1), end, f"{TODAY.year} to date"
    if "last year" in ql: y = TODAY.year - 1; return dt.date(y, 1, 1), dt.date(y, 12, 31), str(y)
    if "this month" in ql: return TODAY.replace(day=1), end, "this month"
    m = re.search(r"\b(20\d\d)\b", ql)
    if m: y = int(m[1]); return dt.date(y, 1, 1), min(dt.date(y, 12, 31), end), str(y)
    if re.search(r"all time|ever|in total|overall|whole history|4 years", ql): return dt.date(1900, 1, 1), end, "all records"
    return None

def parse_scope(c, q):
    ql = q.lower(); s = {}
    w = sorted(set(x.upper() for x in re.findall(r"well-\d{4}", ql)))
    if w: s["wells"] = w
    from .agent import area_from
    a = area_from(c, q)
    if a: s["area"] = a
    m = re.search(r"\b(t\d{3})\b", ql)
    if m: s["well_type"] = m[1].upper()
    for t in c.execute("SELECT team_id, name FROM teams"):
        if t["name"].lower() in ql or re.search(rf"\b{t['name'].split()[0].lower()} (?:production )?team\b", ql): s["team"] = t["team_id"]
    return s

def parse_metric(q):
    ql = q.lower()
    if re.search(r"fine|penalt", ql): return "fines"
    if re.search(r"notice|violation|regulator|agency|site inspection|spill report", ql): return "reg_events"
    if re.search(r"says active|status says|system says|marked (as )?active|stale|out of date|outdated|recorded status|system of record", ql): return "stale_status"
    if re.search(r"cost|spent|spend|expens|usd|\$|dollar", ql): return "repair_cost"
    if re.search(r"repair|maintenance|job|fix|work order|corrective|scheduled|breaks?\b|broke|fail", ql): return "repairs"
    if re.search(r"barrel|bbl|volume|how much (oil|crude)", ql) and "spill" in ql or re.search(r"on the ground|crude (?:was |ended |got )?(?:spilled|released|leaked)|oil (?:spilled|released)", ql): return "spill_volume"
    if "spill" in ql or "leak" in ql: return "spills"
    if re.search(r"downtime|down for|days down|was down|were down|down the longest|not producing.*(days|longest)|lost days|days lost|production days|lost production|offline the longest", ql): return "downtime"
    if re.search(r"not producing|stopped|idle|shut.?in|down right now|are down|is down|producing", ql): return "not_producing"
    if re.search(r"note|planned|feedback|comment", ql): return "notes"
    return None

def parse_group(q):
    ql = q.lower()
    for g, pat in [("month", r"by month|per month|each month|monthly|over time|trend"), ("area", r"by (geographic )?area|per area|each area|by block|which area|which block|\b(?:the|our|all|four|each|across) (?:\w+ )?(?:blocks|areas)\b|blocks\b|areas\b"),
                   ("type", r"by (well )?type|per type|each type|t200 vs|t350 vs|which type"), ("team", r"by team|per team|each team|which team"),
                   ("equipment", r"by equipment|per equipment|which equipment|equipment kind|what equipment"), ("well", r"which wells?|by well|per well|each well|top \d+|most|least|longest|rank|list")]:
        if re.search(pat, ql): return g
    return None

def scope_wells(c, scope):
    q, a = "SELECT asset_id, well_type, area_id, team_id FROM wells WHERE 1=1", []
    if scope.get("wells"): q += f" AND asset_id IN ({','.join('?' * len(scope['wells']))})"; a += scope["wells"]
    if scope.get("area"): q += " AND area_id=?"; a.append(scope["area"])
    if scope.get("well_type"): q += " AND well_type=?"; a.append(scope["well_type"])
    if scope.get("team"): q += " AND team_id=?"; a.append(scope["team"])
    return {r["asset_id"]: dict(r) for r in c.execute(q + " ORDER BY asset_id", a)}

def validate(args):
    """Self-check of planner args. Returns list of problems (empty = ok)."""
    p = []
    if args.get("metric") not in METRICS: p.append(f"unknown metric {args.get('metric')}")
    if args.get("group_by") not in GROUPS: p.append(f"unknown group_by {args.get('group_by')}")
    w = args.get("window")
    if w and (w[0] > w[1]): p.append("window start after end")
    return p

def run_query(metric, scope=None, window=None, group_by=None, top=None, filters=None):
    """Compute a metric. Returns rows [{key, value, detail, citations}], total, rule notes and a trace."""
    c = T.db(); scope = scope or {}; filters = filters or {}
    wl = scope_wells(c, scope); ids = list(wl)
    s, e = (window[0], window[1]) if window else (None, None)
    an = {r["area_id"]: r["name"] for r in c.execute("SELECT * FROM areas")}; tn = {r["team_id"]: r["name"] for r in c.execute("SELECT * FROM teams")}
    def key_of(aid, date=None, extra=None):
        w = wl[aid]
        return {"well": aid, "area": an.get(w["area_id"], w["area_id"]), "type": w["well_type"], "team": tn.get(w["team_id"], w["team_id"]),
                "month": (date or "")[:7], "equipment": extra or "?", None: "total"}[group_by]
    agg = defaultdict(float); cites = defaultdict(list); trace = []; rules = []
    if metric in ("downtime", "not_producing", "stale_status"):
        rows = T.effective_inspections(c, ids, s if metric == "downtime" else None, e if metric == "downtime" else None)
        thr = sorted({(r["well_type"], r["threshold"]) for r in rows}); rules += [f"{t}: producing when wellhead − air ≥ {v:g} °C ({t} manual)" for t, v in thr]
        if metric == "downtime":
            rules.append("Downtime = 7 days per non-producing weekly inspection (Dataset Guide)")
            for r in rows:
                if not r["producing"]: k = key_of(r["asset_id"], r["date"]); agg[k] += 7; cites[k].append(r["inspection_id"])
            if group_by in ("well", None) or group_by is None:
                for a in ids: agg.setdefault(key_of(a), 0) if group_by == "well" else None
        else:
            last = {}
            for r in rows: last[r["asset_id"]] = r
            st = {a: dict(c.execute("SELECT recorded_status FROM wells WHERE asset_id=?", (a,)).fetchone())["recorded_status"] for a in last}
            for a, r in last.items():
                hit = (not r["producing"]) if metric == "not_producing" else ((st[a] == "active") != r["producing"])
                if hit:
                    k = key_of(a, r["date"]) if group_by not in (None,) else "total"; agg[k] += 1; cites[k].append(r["inspection_id"])
                    trace.append({"well": a, "delta": r["delta"], "producing": r["producing"], "recorded": st[a], "inspection": r["inspection_id"], "date": r["date"]})
            if metric == "stale_status": rules.append("recorded_status is refreshed monthly and can be stale; the latest inspection is the truth (Dataset Guide)")
    elif metric in ("spills", "spill_volume"):
        for r in T.spill_rows(c, ids, s, e):
            k = key_of(r["asset_id"], r["date"]); agg[k] += 1 if metric == "spills" else (r["spill_est_volume_bbl"] or 0); cites[k].append(r["inspection_id"])
            trace.append({"well": r["asset_id"], "date": r["date"], "bbl": r["spill_est_volume_bbl"], "inspection": r["inspection_id"]})
        rules.append("Detections voided by correction notes are excluded; runtime corrections applied")
    elif metric in ("repairs", "repair_cost"):
        sql = f"SELECT * FROM maintenance WHERE asset_id IN ({','.join('?' * len(ids))})"; a = list(ids)
        if s: sql += " AND date(started_at)>=? AND date(started_at)<=?"; a += [str(s), str(e)]
        if filters.get("maintenance_type"): sql += " AND maintenance_type=?"; a.append(filters["maintenance_type"])
        if filters.get("equipment_kind"): sql += " AND equipment_kind=?"; a.append(filters["equipment_kind"])
        for r in c.execute(sql, a) if ids else []:
            k = key_of(r["asset_id"], r["started_at"], r["equipment_kind"]); agg[k] += 1 if metric == "repairs" else (r["cost_total"] or 0); cites[k].append(r["maintenance_id"])
        rules.append("A repair belongs to a period by its start date")
    elif metric in ("fines", "reg_events"):
        sql = f"SELECT * FROM reg_events WHERE asset_id IN ({','.join('?' * len(ids))})"; a = list(ids)
        if s: sql += " AND date>=? AND date<=?"; a += [str(s), str(e)]
        if filters.get("open"): sql += " AND status='open'"
        if filters.get("event_type"): sql += " AND event_type=?"; a.append(filters["event_type"])
        for r in c.execute(sql, a) if ids else []:
            if metric == "fines" and not r["fine_usd"]: continue
            k = key_of(r["asset_id"], r["date"]); agg[k] += (r["fine_usd"] or 0) if metric == "fines" else 1; cites[k].append(r["event_id"])
            trace.append({"well": r["asset_id"], "event": r["event_id"], "type": r["event_type"], "date": r["date"], "fine": r["fine_usd"], "status": r["status"], "protocol": r["protocol_id"]})
    elif metric == "notes":
        sql = f"SELECT * FROM notes WHERE asset_id IN ({','.join('?' * len(ids))})"; a = list(ids)
        if s: sql += " AND date(created_at)>=? AND date(created_at)<=?"; a += [str(s), str(e)]
        for r in c.execute(sql, a) if ids else []:
            k = key_of(r["asset_id"], r["created_at"]); agg[k] += 1; cites[k].append(r["note_id"])
            trace.append({"well": r["asset_id"], "note": r["note_id"], "type": r["note_type"], "text": r["text"], "by": T.user_name(c, r["author_user_id"])})
    out = sorted(({"key": k, "value": round(v, 1), "citations": cites[k]} for k, v in agg.items()), key=lambda x: (-x["value"], str(x["key"])) if group_by not in ("month",) else x["key"])
    if group_by == "month": out = sorted(out, key=lambda x: x["key"])
    total = round(sum(agg.values()), 1)
    if top: out = out[:top]
    return {"metric": metric, "scope": scope, "window": [str(s), str(e)] if s else None, "group_by": group_by, "rows": out, "total": total,
            "n_wells": len(ids), "rules": rules, "trace": trace, "citations": [i for r in out for i in r["citations"]][:200]}
