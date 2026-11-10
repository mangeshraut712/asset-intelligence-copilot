"""Composable query tool: metric x scope (well/area/type/team/field) x window x group-by.
Parsing is deterministic; the LLM planner can also call run_query() directly with validated args."""
import re, calendar, datetime as dt
from collections import defaultdict
from . import tools as T
from .tools import TODAY, fmt

MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m} | {m.lower(): i for i, m in enumerate(calendar.month_abbr) if m}
MONTHS["sept"] = 9  # common abbreviation; calendar.month_abbr only has "Sep"
NUMW = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twelve": 12}
METRICS = ["downtime", "spills", "spill_volume", "repairs", "repair_cost", "fines", "reg_events", "not_producing", "stale_status", "notes"]
GROUPS = [None, "well", "area", "type", "team", "month", "equipment"]

def _safe_date(y, m, d):
    """Calendar dates that do not exist (31 Feb, year 0) are None, not an exception."""
    try: return dt.date(int(y), int(m), int(d))
    except (TypeError, ValueError, OverflowError): return None

def _numeric_date(s):
    """Slash, dot or hyphen numeric dates. Day-month-year matches the product's '15 Oct 2026' form;
    month-day-year is used only when the first number cannot be a day-major month (e.g. 10/15/2026)."""
    s = s.strip()
    m = re.match(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$", s)
    if m: return _safe_date(m[1], m[2], m[3])
    m = re.match(r"^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$", s)
    if not m: return None
    a, b, y = int(m[1]), int(m[2]), int(m[3])
    dmy, mdy = _safe_date(y, b, a), _safe_date(y, a, b)
    if a > 12: return dmy
    if b > 12: return mdy
    return dmy  # both <= 12: prefer day-month-year

def _date(s, default_year=None):
    s = s.strip().lower().replace(",", "")
    num = _numeric_date(s)
    if num: return num
    s = re.sub(rf"\b({'|'.join(re.escape(m) for m in MONTHS)})\.", r"\1 ", s)
    s = re.sub(r"\s+", " ", s).strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m: return _safe_date(m[1], m[2], m[3])
    # "2026-10" / "2026/10" is the first day of that month, not an incomplete date.
    m = re.match(r"^(\d{4})[-/](\d{1,2})$", s)
    if m:
        y, mo = int(m[1]), int(m[2])
        if 1 <= mo <= 12:
            return dt.date(y, mo, 1)
    # Month + year must be tried before month + day, otherwise "October 2026"
    # is read as October 20 because the year matches \d{1,2} plus leftover digits.
    m = re.match(r"([a-z]+) (\d{4})$", s)
    if m and m[1] in MONTHS:
        return dt.date(int(m[2]), MONTHS[m[1]], 1)
    m = re.match(r"(\d{1,2})(?:st|nd|rd|th)? ([a-z]+)(?: (\d{4}))?", s) or None
    if m and m[2] in MONTHS: return _safe_date(m[3] or default_year or TODAY.year, MONTHS[m[2]], m[1])
    m = re.match(r"([a-z]+) (\d{1,2})(?:st|nd|rd|th)?(?: (\d{4}))?", s)
    if m and m[1] in MONTHS: return _safe_date(m[3] or default_year or TODAY.year, MONTHS[m[1]], m[2])
    return None

def _is_month_year(s):
    """True when the token names a month, not a specific day (October 2026, 2026-10)."""
    s = s.strip().lower().replace(",", "")
    m = re.match(r"^(\d{4})[-/](\d{1,2})$", s)
    if m:
        return 1 <= int(m[2]) <= 12
    m = re.match(r"^([a-z]+) (\d{4})$", s)
    return bool(m and m[1] in MONTHS)

def _month_end(d):
    return dt.date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])

def _month_only(s):
    """A bare month name such as 'October' or 'Oct', with no day or year."""
    return MONTHS.get(s.strip().lower().replace(",", ""))


def _closed_range(left, right):
    """Inclusive start/end from two date phrases, including whole months when given as month-year."""
    a, b = _date(left), _date(right)
    if a and b:
        if _is_month_year(left):
            a = dt.date(a.year, a.month, 1)
        if _is_month_year(right):
            b = _month_end(b)
        if a > b:
            a, b = b, a
        return a, b, f"{fmt(a)} to {fmt(b)}"
    ma, mb = _month_only(left), _month_only(right)
    if ma and mb:
        y = TODAY.year
        a = dt.date(y, ma, 1)
        end_year = y + 1 if mb < ma else y
        b = _month_end(dt.date(end_year, mb, 1))
        return a, b, f"{fmt(a)} to {fmt(b)}"
    if a and mb:
        if _is_month_year(left):
            a = dt.date(a.year, a.month, 1)
        # A bare end month earlier in the calendar belongs to the next year
        # ("between November 2026 and January" -> Jan 2027, not Jan 2026).
        end_year = a.year + 1 if mb < a.month else a.year
        b = _month_end(dt.date(end_year, mb, 1))
        if a > b:
            a, b = b, a
        return a, b, f"{fmt(a)} to {fmt(b)}"
    if b and ma:
        if _is_month_year(right):
            b = _month_end(b)
        # A bare start month later in the calendar belongs to the previous year
        # ("between Nov and Jan 2027" -> Nov 2026, not Nov 2027 swapped).
        start_year = b.year - 1 if ma > b.month else b.year
        a = dt.date(start_year, ma, 1)
        if a > b:
            a, b = b, a
        return a, b, f"{fmt(a)} to {fmt(b)}"
    return None


def parse_window(q):
    """Return (start, end, label) or None. 'last N' windows end yesterday (the last full day before today)."""
    ql = q.lower()
    # "Oct. 15, 2026" / "Sept. 2026": a period after a month abbreviation is punctuation, not part of the name.
    ql = re.sub(rf"\b({'|'.join(re.escape(m) for m in MONTHS)})\.", r"\1 ", ql)
    ql = re.sub(r"\s+", " ", ql).strip()
    end = TODAY - dt.timedelta(days=1)
    if re.search(r"right now|currently|at the moment|latest inspection", ql): return None
    # "between 15 and 20 October 2026" names the month only once.
    m = re.search(r"between (\d{1,2})(?:st|nd|rd|th)? and (\d{1,2})(?:st|nd|rd|th)? ([a-z]+)(?: (\d{4}))?(?:[?.,]|$| show| as | in a| on a)", ql)
    if m and m[3] in MONTHS:
        y = int(m[4]) if m[4] else TODAY.year
        a, b = _safe_date(y, MONTHS[m[3]], m[1]), _safe_date(y, MONTHS[m[3]], m[2])
        if a and b:
            if a > b:
                a, b = b, a
            return a, b, f"{fmt(a)} to {fmt(b)}"
        if m[4]:
            return None
    m = re.search(r"between (.+?) and (.+?)(?:[?.,]|$| show| as | in a| on a)", ql)
    if m:
        rng = _closed_range(m[1], m[2])
        if rng:
            return rng
        if re.search(r"\d", m[1] + m[2]): return None  # a dated "between" that is not a real range
    # "from START to/through END" is a closed range, not "from START until yesterday".
    m = re.search(r"(?:from|since) (.+?) (?:to|through|until|till) (.+?)(?:[?.,]|$| show| as | in a| on a)", ql)
    if m:
        rng = _closed_range(m[1], m[2])
        if rng:
            return rng
        if re.search(r"\d", m[1] + m[2]): return None
    m = re.search(r"(?:from|since) (\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{4}|\d{1,2} [a-z]+(?: \d{4})?|[a-z]+ \d{4}|[a-z]+ \d{1,2}(?:st|nd|rd|th)?(?: \d{4})?|\d{4}[-/.]\d{1,2})", ql)
    if m:
        a = _date(m[1])
        if a: return a, end, f"{fmt(a)} to {fmt(end)}"
        if re.search(r"\d", m[1]): return None
    m = re.search(r"(?:last|past|previous) (\d+|" + "|".join(NUMW) + r") (day|week|month|year)s?", ql)
    if m:
        n = int(NUMW.get(m[1], m[1]) if not m[1].isdigit() else m[1]); u = m[2]
        s = T.sub_months(end, n) if u == "month" else T.sub_months(end, 12 * n) if u == "year" else T.sub_days(TODAY, n * (7 if u == "week" else 1))
        return s, end, f"last {n} {u}s ({fmt(s)} to {fmt(end)})"
    if re.search(r"\blast year\b", ql): y = TODAY.year - 1; return dt.date(y, 1, 1), dt.date(y, 12, 31), str(y)
    if re.search(r"(?:last|past) (year|12 months)", ql): s = T.sub_months(end, 12); return s, end, f"last 12 months ({fmt(s)} to {fmt(end)})"
    if re.search(r"(?:last|past) (month)\b", ql): s = T.sub_months(end, 1); return s, end, f"last month ({fmt(s)} to {fmt(end)})"
    # "last week" (no count) is the same 7-day window as "last 1 week", ending yesterday.
    if re.search(r"\b(?:last|past|previous) week\b", ql):
        s = T.sub_days(TODAY, 7)
        return s, end, f"last week ({fmt(s)} to {fmt(end)})"
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
    # "this quarter" / "quarter-to-date" / "qtd", and the previous calendar quarter.
    if re.search(r"\bthis quarter\b|\bquarter[\s\u2010-\u2015\-]+to[\s\u2010-\u2015\-]+date\b|\bqtd\b", ql):
        k = (TODAY.month - 1) // 3 + 1
        s = dt.date(TODAY.year, 3 * k - 2, 1)
        return s, end, f"Q{k} {TODAY.year} to date"
    if re.search(r"\b(?:last|past|previous) quarter\b", ql):
        k = (TODAY.month - 1) // 3
        y = TODAY.year
        if k == 0:
            k, y = 4, y - 1
        s = dt.date(y, 3 * k - 2, 1)
        e = dt.date(y, 3 * k, calendar.monthrange(y, 3 * k)[1])
        return s, min(e, end), f"Q{k} {y} ({fmt(s)} to {fmt(min(e, end))})"
    # Accept "year-to-date" / "year—to—date" as well as the spaced and "ytd" forms.
    if "this year" in ql or re.search(r"\byear[\s\u2010-\u2015\-]+to[\s\u2010-\u2015\-]+date\b", ql) or re.search(r"\bytd\b", ql):
        return dt.date(TODAY.year, 1, 1), end, f"{TODAY.year} to date"
    if "last year" in ql: y = TODAY.year - 1; return dt.date(y, 1, 1), dt.date(y, 12, 31), str(y)
    if re.search(r"\btoday\b", ql): return TODAY, TODAY, "today"
    if re.search(r"\byesterday\b", ql): return end, end, "yesterday"
    if re.search(r"\bthis week\b", ql) or re.search(r"\bweek[\s\u2010-\u2015\-]+to[\s\u2010-\u2015\-]+date\b", ql):
        start = TODAY - dt.timedelta(days=TODAY.weekday())
        return start, end if start <= end else start, f"this week ({fmt(start)} to {fmt(end if start <= end else start)})"
    if "this month" in ql or re.search(r"\bmonth[\s\u2010-\u2015\-]+to[\s\u2010-\u2015\-]+date\b", ql):
        return TODAY.replace(day=1), end, "this month"
    mon3 = "|".join(k for k in MONTHS if len(k) == 3 or k == "sept")
    # Month + 4-digit year must be tried before Month + 1-2 day digits, otherwise
    # "December 2026" is consumed as "December 20".
    date_token = (
        rf"(?:\d{{4}}[-/.]\d{{1,2}}[-/.]\d{{1,2}}|\d{{1,2}}[-/.]\d{{1,2}}[-/.]\d{{4}}|"
        rf"\d{{1,2}}(?:st|nd|rd|th)? (?:{mon3})[a-z]*(?: \d{{4}})?|"
        rf"(?:{mon3})[a-z]* (?:\d{{4}}|\d{{1,2}}(?:st|nd|rd|th)?(?:,)?(?: \d{{4}})?))"
    )
    # "on 15 Oct 2026" / "on 2026-10-15" is that day, not the whole year the digits mention.
    m = re.search(rf"\b(?:on|dated)\s+({date_token})", ql)
    if m:
        a = _date(m[1])
        if a:
            if _is_month_year(m[1]):
                e = _month_end(a)
                return a, min(e, end) if a.year == TODAY.year else e, f"{calendar.month_name[a.month]} {a.year}"
            return a, a, fmt(a)
        if re.search(r"\d", m[1]): return None
    # "in 2026-10" / "during 2026-10" is that month, not the whole of 2026.
    m = re.search(r"\b(?:in|during|for|of) (\d{4})[-/](\d{1,2})\b", ql)
    if m:
        y, mo = int(m[1]), int(m[2])
        if 1 <= mo <= 12:
            s, e = dt.date(y, mo, 1), dt.date(y, mo, calendar.monthrange(y, mo)[1])
            return s, min(e, end), f"{calendar.month_name[mo]} {y}"
    m = re.search(r"\b(20\d\d)\b", ql)
    if m:
        # A year that is only there as part of a more specific date must not become a year-long window.
        if re.search(rf"{date_token}|\d{{4}}[-/]\d{{1,2}}\b", ql):
            tok = re.search(date_token, ql)
            a = _date(tok.group(0)) if tok else None
            if a:
                if _is_month_year(tok.group(0)):
                    e = _month_end(a)
                    return a, min(e, end) if a <= end else e, f"{calendar.month_name[a.month]} {a.year}"
                return a, a, fmt(a)
            return None
        y = int(m[1]); return dt.date(y, 1, 1), min(dt.date(y, 12, 31), end), str(y)
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
    wells = scope.get("wells") or []
    if wells:
        q += f" AND asset_id IN ({','.join('?' * len(wells))})"; a += list(wells)
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
    if w:
        if not isinstance(w, (list, tuple)) or len(w) < 2: p.append("window must be a start and end")
        elif not isinstance(w[0], dt.date) or not isinstance(w[1], dt.date): p.append("window bounds must be dates")
        elif w[0] > w[1]: p.append("window start after end")
    scope = args.get("scope") or {}
    if not isinstance(scope, dict): p.append("scope must be an object")
    else:
        for wid in scope.get("wells") or []:
            if not re.fullmatch(r"WELL-\d{4}", str(wid), re.I): p.append(f"bad well id {wid}")
    if "top" in args and args["top"] is not None:
        top = args["top"]
        if isinstance(top, bool) or not isinstance(top, int) or top < 1 or top > 50: p.append("top must be an integer from 1 to 50")
    return p

def run_query(metric, scope=None, window=None, group_by=None, top=None, filters=None):
    """Compute a metric. Returns rows [{key, value, detail, citations}], total, rule notes and a trace."""
    c = T.db(); scope = scope or {}; filters = filters or {}
    if metric not in METRICS:
        return {"metric": metric, "scope": scope, "window": None, "group_by": group_by, "rows": [], "total": 0,
                "n_wells": 0, "rules": [], "trace": [], "citations": [], "error": f"unknown metric {metric}"}
    wl = scope_wells(c, scope); ids = list(wl)
    s, e = (window[0], window[1]) if window else (None, None)
    if s and e and s > e: s, e = e, s
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
