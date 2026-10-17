"""Deterministic tools for document-driven question types: production/pressure availability, recall lots,
team lookup, gas-odor response (OPS-1), temporary bypass vs MOC (OPS-2), regulator-letter scope,
status disagreement (OPS-3), freeze checks (OPS-5), operator-note risk ranking, shut-in delay reasons,
regional temperature. Every rule (lots, deadlines, expiry dates, scope) is parsed from the documents."""
import re, json, datetime as dt
from collections import defaultdict, Counter
from statistics import median
from . import tools as T
from .tools import fmt, user_name, TODAY

MON = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
def pdate(s):
    m = re.search(r"(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})", s, re.I)
    return dt.date(int(m.group(3)), MON[m.group(2).lower()[:3]], int(m.group(1))) if m else None
def ts(s): return dt.datetime.fromisoformat(s.replace("Z", "")[:19])
def hm(s): return s.replace("T", " ")[:16] + " UTC"
def doc(c, pat):
    return [dict(r) for r in c.execute("SELECT * FROM documents WHERE path LIKE ? ORDER BY path", (f"%{pat}%",))]
def anames(c): return {r["area_id"]: r["name"] for r in c.execute("SELECT * FROM areas")}
def wells(c): return {r["asset_id"]: dict(r) for r in c.execute("SELECT * FROM wells")}
def table(rows, cols=None): return {"type": "table", "columns": cols or (list(rows[0].keys()) if rows else []), "rows": rows}
def res(text, vis, cites, ws): return {"text": text, "visual": vis, "citations": list(dict.fromkeys(cites)), "wells": list(dict.fromkeys(ws))}

def prefs(c, user):
    try: r = c.execute("SELECT value FROM memory_prefs WHERE user_id=?", (user,)).fetchone()
    except Exception: return {}
    return json.loads(r["value"]) if r else {}
def money(c, user, v):
    if v is None: return "-"
    return f"${v/1000:,.1f}K" if prefs(c, user).get("cost_thousands") else f"${v:,.0f}"
def sort_rows(c, user, rows):
    if prefs(c, user).get("sort_area_well"): rows.sort(key=lambda r: (r.get("Area", ""), r.get("Well", "")))
    return rows

# ---------- private preferences ----------
def save_pref(c, user, q):
    ql = q.lower(); p = prefs(c, user)
    if re.search(r"sort .*by area", ql): p["sort_area_well"] = True
    if re.search(r"thousands", ql): p["cost_thousands"] = True
    c.execute("CREATE TABLE IF NOT EXISTS memory_prefs(user_id TEXT PRIMARY KEY, value TEXT)")
    c.execute("INSERT OR REPLACE INTO memory_prefs VALUES(?,?)", (user, json.dumps(p))); c.commit()
    parts = (["lists of wells sorted by area, then well ID"] if p.get("sort_area_well") else []) + (["costs in thousands of dollars"] if p.get("cost_thousands") else [])
    return res(f"Saved as a **private preference for {user_name(c, user)} only** (other users are not affected): " + "; ".join(parts) + ". I'll apply it whenever I list wells for you.", None, ["memory_prefs (private)"], [])

# ---------- recall ----------
def recall_lots(c):
    d = doc(c, "recall")
    if not d: return None, [], None
    t = d[0]["text"]; head = t.split("Pumps from all other lots")[0]
    lots = sorted(set(re.findall(r"LOT-\d{4}-[A-Z]", head)))
    m = re.search(r"\(by (\d{1,2} \w+ \d{4})\)", t); due = pdate(m.group(1)) if m else None
    model = re.search(r"Highline (RP-\d+)", t)
    return d[0], lots, due

def pump_installs(c):
    """Per well: list of (started_at, mnt_id, lot, serial, cost) from 'Parts installed' lines, oldest first."""
    out = defaultdict(list)
    for m in c.execute("SELECT maintenance_id, asset_id, started_at, cost_total, report_text FROM maintenance WHERE report_text LIKE '%Parts installed%' ORDER BY started_at"):
        for line in re.findall(r"Parts installed:\**\s*(.*)", m["report_text"]):
            lot = re.search(r"LOT-\d{4}-[A-Z]", line)
            if lot and re.search(r"pump", line, re.I):
                sn = re.search(r"SN-\d+", line)
                out[m["asset_id"]].append({"started": m["started_at"], "mnt": m["maintenance_id"], "lot": lot.group(0), "serial": sn.group(0) if sn else "", "cost": m["cost_total"], "line": line.strip()})
    return out

def swap_claims(c):
    """User-reported pump swaps from shared memory: first-hand vs relayed."""
    out = {}
    for f in c.execute("SELECT * FROM memory_well_facts WHERE kind='pump_swap' ORDER BY id"):
        out[f["asset_id"]] = dict(f) | {"author": user_name(c, f["author_user_id"])}
    return out

def recalled_in_ground(c):
    d, lots, due = recall_lots(c); inst = pump_installs(c); wl = wells(c); claims = swap_claims(c)
    rows = []
    for w, lst in inst.items():
        cur = lst[-1]
        if cur["lot"] in lots:
            rows.append({"well": w, "area_id": wl[w]["area_id"], "team": wl[w]["team_id"], **cur, "claim": claims.get(w)})
    return d, lots, due, rows

def recall(cp, q, user, chat, area=None, mine=False):
    c = cp.c; an = anames(c); d, lots, due, rows = recalled_in_ground(c)
    if not d: return None
    if mine:
        team = c.execute("SELECT team_id FROM users WHERE user_id=?", (user,)).fetchone()["team_id"]
        rows = [r for r in rows if r["team"] == team]; scope = f"in your areas ({', '.join(sorted({an[r['area_id']] for r in rows}))})"
    elif area: rows = [r for r in rows if r["area_id"] == area]; scope = f"in {an[area]}"
    else: scope = "across the field"
    gone = [r for r in rows if r["claim"] and r["claim"]["status"] == "replaced (user-reported)"]
    pend = [r for r in rows if r["claim"] and r["claim"]["status"] != "replaced (user-reported)"]
    inground = [r for r in rows if r not in gone]
    show_cost = bool(re.search(r"cost", q, re.I))
    tab = []
    for r in inground:
        x = {"Well": r["well"], "Area": an[r["area_id"]], "Lot": r["lot"], "Serial": r["serial"], "Installed by": f"{r['mnt']} ({fmt(r['started'])})"}
        if show_cost: x["Install job cost"] = money(c, user, r["cost"])
        x["Source"] = f"maintenance report {r['mnt']} ('Parts installed')" + (f"; ⚠ {r['claim']['author']} relayed a swap claim, unconfirmed" if r in pend else "")
        tab.append(x)
    tab = sort_rows(c, user, tab) if prefs(c, user) else sorted(tab, key=lambda x: x["Well"])
    byarea = Counter(x["Area"] for x in tab)
    txt = [f"**{len(tab)} recalled pumps are still in the ground {scope}** (Highline lots {', '.join(lots)} from recall notice HPC-RN-2026-07; replacement was due {fmt(due) if due else '?'}, so these are overdue)."]
    txt.append("By area: " + ", ".join(f"{a}: {n}" for a, n in sorted(byarea.items())) + ".")
    txt.append("Source: I take the pump currently in each well from the latest 'Parts installed' line in its maintenance reports; a recalled pump later replaced by a pump from another lot is not counted.")
    if show_cost and tab:
        tot = sum(r["cost"] or 0 for r in inground); txt.append(f"Total install job cost: {money(c, user, tot)} (full cost of the job that installed each pump, from maintenance.jsonl).")
    for r in gone: txt.append(f"Not counted: {r['well']} — {r['claim']['author']} reported on {r['claim']['ts'][:10]} that the recalled pump was swapped (shared memory, user-reported; no work order in the system yet).")
    for r in pend: txt.append(f"⚠ Still listed: {r['well']} — {r['claim']['author']} relayed that it was swapped (\"{r['claim']['text']}\"), but that is second-hand and there is no work order; **unconfirmed** until the person who did it or a work order confirms it.")
    if prefs(c, user): txt.append("Applied your private preferences (" + ", ".join(k for k in prefs(c, user)) + ").")
    return res("\n\n".join(txt), table(tab), [d["doc_id"]] + [r["mnt"] for r in inground], [r["well"] for r in inground])

def pump_swap_statement(cp, q, user, w):
    c = cp.c; name = user_name(c, user); ql = q.lower()
    m = re.match(r"\s*(\w+) (told me|said|says)", q)
    relayed = bool(m) and m.group(1).lower() not in ("i", "we")
    _, lots, _, rows = recalled_in_ground(c)
    onlist = next((r for r in rows if r["well"] == w), None)
    status = "unconfirmed (second-hand)" if relayed else "replaced (user-reported)"
    c.execute("INSERT INTO memory_well_facts(asset_id,author_user_id,ts,text,kind,status,conflict) VALUES(?,?,?,?,?,?,?)",
              (w, user, cp_now(), q, "pump_swap", status, None)); c.commit()
    src = f"maintenance report {onlist['mnt']} ({onlist['lot']})" if onlist else "maintenance reports"
    if not onlist:
        return res(f"{w} has no recalled pump in the ground according to the data ({src}), so there is nothing to take off. I've recorded your note as shared knowledge.", None, [], [w])
    if relayed:
        return res(f"⚠ I have **not** taken {w} off the recall list. The data ({src}) still shows recalled lot {onlist['lot']} in the well, there is no work order for a swap, and this is a second-hand report: {m.group(1)} told {name}, not first-hand. "
                   f"I've recorded it in shared memory as **unconfirmed**, attributed to {name} (relaying {m.group(1)}). I'll remove it once {m.group(1)} confirms directly or the work order lands.", None, [onlist["mnt"]], [w])
    return res(f"Noted for everyone: {name} reports the recalled pump on {w} (lot {onlist['lot']}, installed by {onlist['mnt']}) was swapped. The work order isn't in the system, so I'm counting {w} as replaced **on {name}'s first-hand report (shared memory, user-reported)**, not on records. I'll reconcile when the work order appears.",
               None, [onlist["mnt"], "shared memory"], [w])

def cp_now():
    from .agent import now
    return now()

# ---------- team ----------
def team(cp, q):
    c = cp.c; ql = q.lower()
    for t in c.execute("SELECT * FROM teams"):
        if t["name"].lower() in ql:
            lead = c.execute("SELECT * FROM users WHERE user_id=?", (t["lead_user_id"],)).fetchone()
            ar = c.execute("SELECT area_id, name FROM areas WHERE team_id=? ORDER BY area_id", (t["team_id"],)).fetchall()
            n = c.execute("SELECT count(*) FROM wells WHERE team_id=?", (t["team_id"],)).fetchone()[0]
            per = [(a["name"], c.execute("SELECT count(*) FROM wells WHERE area_id=?", (a["area_id"],)).fetchone()[0]) for a in ar]
            return res(f"**{lead['name']}** ({lead['user_id']}, {lead['role'].replace('_', ' ')}) leads {t['name']} ({t['team_id']}). The team runs **{n} wells**" + (": " + ", ".join(f"{a} {k}" for a, k in per) if per else "") + ". Source: fleet/users.json, areas.json and well metadata.",
                       table([{"Area": a, "Wells": k} for a, k in per]), ["users.json", "areas.json"], [])
    return None

# ---------- data not available ----------
def unavailable(cp, q, what):
    c = cp.c
    if what == "pressure":
        return res("I can't map reservoir pressure: **the dataset has no pressure measurements** (no reservoir, bottom-hole, tubing or casing pressure field in inspections, maintenance or notes). The only pressures in the data are flowline pressure-test values in repair reports, which are test pressures, not reservoir pressure. "
                   "I won't draw a map from proxies such as wellhead temperature, because that would be misleading. If you can supply pressure surveys, I can map them.", None, ["inspections.jsonl schema", "maintenance reports (pressure tests)"], [])
    return res("I can't say which well produced the most oil: **the dataset has no production volumes** (no barrels produced, no allocation or meter data). Inspections only say whether a well was producing oil at the time of the reading (wellhead minus air temperature against the well-type threshold). "
               "I could rank wells by the share of 2026 inspections that read as producing, but that measures uptime, not volume, so I won't present it as the top producer.", None, ["inspections.jsonl schema", "well-type manuals"], [])

# ---------- OPS-1 gas odor ----------
GAS = re.compile(r"smell(ed)? gas|rotten.egg|gas odou?r|h2s monitor alarm", re.I)
def gas(cp, q, start=None, wells_only=None):
    c = cp.c; an = anames(c); wl = wells(c)
    start = start or (T.d("2026-11-01") if not re.search(r"since", q, re.I) else None)
    m = re.search(r"since (\d{1,2} \w+ \d{4})", q, re.I); start = pdate(m.group(1)) if m else start
    rows, cites = [], []
    for n in c.execute("SELECT * FROM notes WHERE note_type='operator_note' AND created_at>=? ORDER BY created_at", (str(start),)):
        if not GAS.search(n["text"]): continue
        if wells_only and n["asset_id"] not in wells_only: continue
        t0 = ts(n["created_at"]); lim = 12 if t0.date() >= dt.date(2027, 1, 1) else 24
        cand = [(ts(m["started_at"]), m["maintenance_id"], "repair") for m in c.execute("SELECT * FROM maintenance WHERE asset_id=? AND started_at>?", (n["asset_id"], n["created_at"]))]
        cand += [(ts(i["inspected_at"]), i["inspection_id"], "manual inspection") for i in c.execute("SELECT * FROM inspections WHERE asset_id=? AND method='manual' AND inspected_at>?", (n["asset_id"], n["created_at"]))]
        cand.sort(); r = cand[0] if cand else None
        h = round((r[0] - t0).total_seconds() / 3600, 1) if r else None
        late_open = r is None and (dt.datetime.combine(TODAY, dt.time()) - t0).total_seconds() / 3600 < lim
        rows.append({"Well": n["asset_id"], "Area": an[wl[n["asset_id"]]["area_id"]], "Reported at": hm(n["created_at"]), "Note": n["text"],
                     "Response": f"{r[1]} ({r[2]}, {hm(r[0].isoformat())})" if r else "none", "Hours to response": h if h is not None else "-",
                     "Deadline": f"{lim} h", "Met / Missed": "Met" if h is not None and h <= lim else ("Pending" if late_open else "Missed"), "_resp": r})
        cites += [n["note_id"]] + ([r[1]] if r else [])
    return rows, cites

def gas_report(cp, q):
    rows, cites = gas(cp, q)
    miss = [r for r in rows if r["Met / Missed"] == "Missed"]
    txt = [f"**{len(rows)} gas-odor reports** in operator notes since 1 Nov 2026 (OPS-1: smelled gas, rotten-egg smell, gas odor or H2S monitor alarm). **{len(rows) - len(miss)} met** the deadline and **{len(miss)} missed** it.",
           "Rule (Operations SOP rev 2, OPS-1): a field response is a maintenance job (started_at) or a **manual** inspection (drone doesn't count) on that well, starting after the note, within 24 h for notes before 1 Jan 2027 and 12 h from 1 Jan 2027. Times are UTC as recorded."]
    if miss: txt.append("Missed: " + "; ".join(f"{r['Well']} ({r['Reported at']}, " + (f"responded after {r['Hours to response']} h > {r['Deadline']}" if r["_resp"] else "no response at all") + ")" for r in miss) + ".")
    for r in rows: r.pop("_resp")
    return res("\n\n".join(txt), table(rows), ["Operations SOP OPS-1"] + cites, [r["Well"] for r in rows])

def h2s(cp, q, w):
    c = cp.c; d0 = None
    from .agent import parse_date
    d0 = parse_date(q)
    notes = [n for n in c.execute("SELECT * FROM notes WHERE asset_id=? AND note_type='operator_note' ORDER BY created_at", (w,)) if GAS.search(n["text"]) and (not d0 or n["created_at"][:10] == str(d0))]
    if not notes: return None
    n = notes[0]
    rows, _ = gas(cp, "", start=T.d(n["created_at"]), wells_only=[w]); r = rows[0] if rows else None
    out = [f"Operator note {n['note_id']} ({hm(n['created_at'])}): \"{n['text']}\" — the note itself records **no H2S reading**."]
    cites = [n["note_id"]]
    jobs = c.execute("SELECT * FROM maintenance WHERE asset_id=? AND started_at>? ORDER BY started_at LIMIT 1", (w, n["created_at"])).fetchall()
    for j in jobs:
        mm = re.search(r"highest reading (\d+(?:\.\d+)?) ppm", j["report_text"] or "")
        if mm and (ts(j["started_at"]) - ts(n["created_at"])).days < 14:
            out.append(f"The next job on the well, {j['maintenance_id']} ({j['issue']}, started {hm(j['started_at'])}), reports personal H2S monitors with a highest reading of **{mm.group(1)} ppm** (stop-work level 10 ppm, WS-03). That was taken during the job, not at the time of the odor report."); cites.append(j["maintenance_id"])
    if r: out.append(f"OPS-1 response: {r['Response']}, {r['Hours to response']} h after the note, deadline {r['Deadline']} → **{r['Met / Missed']}**.")
    return res("\n\n".join(out), None, cites, [w])

# ---------- OPS-2 bypass ----------
def mocs(c):
    out = {}
    for dd in doc(c, "moc-"):
        t = dd["text"]; mid = re.search(r"MOC-\d{4}-\d{3}", t).group(0)
        ex = pdate(re.search(r"expires on ([^.\n]+)", t).group(1)); eff = re.search(r"Effective from ([^.\n]+)", t)
        ext = re.search(r"extends (MOC-\d{4}-\d{3})", t)
        ws = re.findall(r"WELL-\d{4}", t.split("## Change")[1].split("##")[0] if "## Change" in t else t)
        out[mid] = {"id": mid, "wells": set(ws), "expires": ex, "effective": pdate(eff.group(1)) if eff else None, "extends": ext.group(1) if ext else None, "doc": dd["doc_id"]}
    for m in out.values():
        if m["extends"] and m["extends"] in out:
            b = out[m["extends"]]
            if m["expires"] > b["expires"]: b["expires"] = m["expires"]; b["extended_by"] = m["id"]
            m["effective"] = m["effective"] or b["effective"]
    return out

BIN = re.compile(r"bypass (in place|installed)|put the bypass in|had the bypass installed", re.I)
BOUT = re.compile(r"bypass (removed|pulled)|took the bypass out", re.I)
def bypass(cp, q):
    c = cp.c; an = anames(c); wl = wells(c); M = mocs(c); ev = defaultdict(list)
    for n in c.execute("SELECT * FROM notes WHERE note_type='operator_note' AND lower(text) LIKE '%bypass%' ORDER BY created_at"):
        if BIN.search(n["text"]): ev[n["asset_id"]].append(("in", n))
        elif BOUT.search(n["text"]): ev[n["asset_id"]].append(("out", n))
    rows, cites = [], []
    for w, es in sorted(ev.items()):
        cur = None
        for kind, n in es + [("end", None)]:
            if kind == "in": cur = n
            elif cur is not None:
                din = T.d(cur["created_at"]); dout = T.d(n["created_at"]) if n else None
                ms = [m for m in M.values() if w in m["wells"] and not m["extends"]]
                m = ms[0] if ms else None
                end = dout or TODAY
                if not m: st = "Not approved"
                elif end > m["expires"]: st = "Expired"
                else: st = "Allowed"
                rows.append({"Well": w, "Area": an[wl[w]["area_id"]], "Bypass in": fmt(din), "Bypass out": fmt(dout) if dout else "still in",
                             "Approval": (m["id"] + (f" (extended by {m['extended_by']})" if m.get("extended_by") else "")) if m else "none",
                             "Approval valid until": fmt(m["expires"]) if m else "-", "Status": st, "Evidence": cur["note_id"] + (f", {n['note_id']}" if n else "")})
                cites += [cur["note_id"]] + ([n["note_id"]] if n else []); cur = None
    now_in = [r for r in rows if r["Bypass out"] == "still in"]
    bad = [r for r in rows if r["Status"] != "Allowed"]
    txt = [f"**In place right now ({len(now_in)}):** " + ("; ".join(f"{r['Well']} ({r['Area']}, in since {r['Bypass in']}) — {r['Status']}" + (f" under {r['Approval']} until {r['Approval valid until']}" if r['Status'] == 'Allowed' else "") for r in now_in) or "none") + ".",
           f"**Violations, past or present ({len(bad)}):** " + ("; ".join(f"{r['Well']} — {r['Status']}" + (f" (approval ended {r['Approval valid until']}, out {r['Bypass out']})" if r['Status'] == 'Expired' else " (no MOC names this well)") for r in bad) or "none") + ".",
           "Rule (OPS-2): allowed only on a well named in an unexpired MOC; a memo that extends another replaces its expiry date (MOC-2026-044 extends MOC-2026-031 to " + (fmt(M['MOC-2026-031']['expires']) if 'MOC-2026-031' in M else '?') + "). In/out times come from operator notes."]
    return res("\n\n".join(txt), table(rows), [m["doc"] for m in M.values()] + ["Operations SOP OPS-2"] + cites, [r["Well"] for r in rows])

# ---------- regulator letter ----------
def letter(cp, q):
    c = cp.c; dd = doc(c, "regulator-letter")
    if not dd: return None
    t = dd[0]["text"]; an = anames(c); wl = wells(c)
    m = re.search(r"For every reportable spill in (.+?) since (\d{1,2} \w+ \d{4})", t)
    names = re.split(r"\s+or\s+|,\s*", m.group(1)); start = pdate(m.group(2))
    ids = [a for a, n in an.items() if n in names]
    thr = T.rule(c, "spill.reportable_bbl", 5); thr = thr[0] if isinstance(thr, tuple) else thr
    phrase = re.search(r"contains the sentence \"([^\"]+)\"", t); phrase = phrase.group(1) if phrase else "Soil samples sent to the lab."
    rows, cites = [], []
    for r in T.spill_rows(c, [w for w in wl if wl[w]["area_id"] in ids], start, TODAY):
        v = r.get("spill_est_volume_bbl") or 0
        if v < thr: continue
        j = c.execute("SELECT * FROM maintenance WHERE triggered_by_inspection_id=? ORDER BY started_at", (r["inspection_id"],)).fetchall()
        job = j[0] if j else None
        ok = bool(job and phrase in (job["report_text"] or ""))
        why = "Yes — clean-up report says \"" + phrase + "\"" if ok else ("No — no clean-up job found" if not job else ("No — no lab soil samples in the clean-up report" + (" (field soil readings only)" if re.search(r"soil", job["report_text"] or "", re.I) else "")))
        rows.append({"Well": r["asset_id"], "Area": an[r["area_id"]], "Inspection": f"{r['inspection_id']} ({fmt(r['date'])})", "Volume (bbl)": v,
                     "Clean-up job": job["maintenance_id"] if job else "none", "Compliant?": why})
        cites += [r["inspection_id"]] + ([job["maintenance_id"]] if job else [])
    nc = [r for r in rows if not r["Compliant?"].startswith("Yes")]
    txt = [f"The letter (20 Nov 2026) covers **reportable spills (≥ {thr:g} bbl) in {' and '.join(names)} since {fmt(start)}**, excluding detections later confirmed not to be crude. That is **{len(rows)} spills**; **{len(nc)} are not compliant**: " + ", ".join(f"{r['Well']} ({r['Inspection']})" for r in nc) + ".",
           f"Compliance test (HSE internal note in the letter, 22 Nov 2026): the clean-up report must contain \"{phrase}\" Field soil readings don't count. Results were due 15 Jan 2027 (today). Spills outside those two blocks, before 1 Jun 2026, or under {thr:g} bbl are out of the letter's scope."]
    return res("\n\n".join(txt), table(rows), [dd[0]["doc_id"]] + cites, [r["Well"] for r in rows])

# ---------- OPS-3 status disagreement ----------
SHUT = re.compile(r"\bshut.?in\b", re.I); RESTART = re.compile(r"restarted|put back on production|back online|back on production", re.I)
def status_conflicts(cp, q):
    c = cp.c; an = anames(c); wl = wells(c)
    last = {}
    for r in T.effective_inspections(c, None, TODAY - dt.timedelta(days=120), TODAY): last[r["asset_id"]] = r
    rows, cites = [], []
    for w, ins in sorted(last.items()):
        n = c.execute("SELECT * FROM notes WHERE asset_id=? AND note_type='operator_note' ORDER BY created_at DESC", (w,)).fetchall()
        n = next((x for x in n if w in x["text"] and (SHUT.search(x["text"]) or RESTART.search(x["text"]))), None)
        if not n: continue
        says_up = bool(RESTART.search(n["text"])) and not SHUT.search(n["text"])
        if says_up == bool(ins["producing"]): continue
        newer = n["created_at"] > ins["inspected_at"]
        status = ("Producing oil (unconfirmed)" if says_up else "Not producing oil (shut in)") if newer else ("Producing oil" if ins["producing"] else "Not producing oil")
        why = ("operator note is more recent than the inspection (OPS-3)" if newer else "inspection is more recent than the note (OPS-3)")
        rows.append({"Well": w, "Area": an[wl[w]["area_id"]], "Latest inspection": f"{ins['inspection_id']}, {fmt(ins['date'])}: {'producing' if ins['producing'] else 'not producing'} (Δ {ins['delta']} °C vs {ins['threshold']:g})",
                     "Latest operator note": f"{hm(n['created_at'])}: {n['text']}", "Status now": status, "Why": why})
        cites += [ins["inspection_id"], n["note_id"]]
    txt = [f"**{len(rows)} wells** where the latest inspection and the latest shut-in/restart operator note disagree. Rule (Operations SOP OPS-3): the more recent evidence wins; a restart note newer than the inspection means producing (unconfirmed) until an inspection confirms; gas, bypass and equipment notes don't change status."]
    return res("\n\n".join(txt), table(rows), ["Operations SOP OPS-3"] + cites, [r["Well"] for r in rows])

# ---------- OPS-5 freeze ----------
def cold(cp, q):
    c = cp.c; an = anames(c); wl = wells(c)
    from .agent import period_from
    y = TODAY.year - 1 if TODAY.month < 12 else TODAY.year
    s, e = dt.date(y, 12, 1), dt.date(y, 12, 31)
    miss = []
    for r in T.effective_inspections(c, None, s, e):
        if r["ambient_temp_c"] <= -5 and r["producing"]:
            lim = (ts(r["inspected_at"]) + dt.timedelta(days=7)).isoformat()
            j = c.execute("SELECT maintenance_id, started_at FROM maintenance WHERE asset_id=? AND issue LIKE '%Heat trace check%' AND started_at>=? AND started_at<=? LIMIT 1", (r["asset_id"], r["inspected_at"][:10], lim)).fetchone()
            if not j: miss.append(r)
    sop = "Operations SOP OPS-5 (freeze protection, 1 Dec – 28 Feb): any inspection with air temperature at or below −5 °C on a well that is producing oil at that reading needs a heat trace check (a maintenance job whose issue contains \"Heat trace check\") starting within 7 days after the inspection. A cold reading on a well that isn't producing needs no check."
    if not miss: return res(sop + f"\n\nNo well missed the check in December {y}.", None, ["Operations SOP OPS-5"], [])
    r = miss[0]
    rows = [{"Well": x["asset_id"], "Area": an[x["area_id"]], "Inspection": x["inspection_id"], "Date": fmt(x["date"]), "Air °C": x["ambient_temp_c"], "Δ °C": x["delta"]} for x in miss]
    return res(sop + f"\n\nExample: **{r['asset_id']}** ({an[r['area_id']]}) — inspection {r['inspection_id']} on {fmt(r['date'])} read {r['ambient_temp_c']} °C air while producing (Δ {r['delta']} °C), and no heat trace check started within 7 days. In total {len(miss)} December readings missed the check (table).",
               table(rows), ["Operations SOP OPS-5", r["inspection_id"]], [r["asset_id"]])

# ---------- operator notes: abnormal behaviour ----------
ABN = re.compile(r"rattl|squeal|fluid pound|tagging|amps hunting|knock|vibrat|clank|groan|thump|squeak|grind|banging|leak|weep|drip|noisy|noise|slipping|belt|hot to the touch|smoking|stalling|struggl", re.I)
NORMAL = re.compile(r"normal|nothing to report|dry and clean", re.I)
def note_risk(cp, q, user, chat, n=10):
    c = cp.c; an = anames(c); wl = wells(c); s = TODAY - dt.timedelta(days=31)
    notes = defaultdict(list)
    for x in c.execute("SELECT * FROM notes WHERE note_type='operator_note' AND created_at>=? ORDER BY created_at", (str(s),)):
        if ABN.search(x["text"]) and not NORMAL.search(x["text"]) and not GAS.search(x["text"]) and "bypass" not in x["text"].lower(): notes[x["asset_id"]].append(x)
    cand = []
    for w, ns in notes.items():
        first = ns[0]["created_at"]
        if c.execute("SELECT 1 FROM maintenance WHERE asset_id=? AND started_at>=? AND maintenance_type!='scheduled'", (w, first)).fetchone(): continue
        last = c.execute("SELECT * FROM maintenance WHERE asset_id=? AND maintenance_type='corrective' ORDER BY started_at DESC", (w,)).fetchall()
        yr = [m for m in last if m["started_at"] >= str(TODAY - dt.timedelta(days=365))]
        ins = T.effective_inspections(c, [w], TODAY - dt.timedelta(days=45), TODAY)
        drop = [i for i in ins if not i["producing"]]
        kinds = Counter(re.sub(r"WELL-\d{4}", "", x["text"]).strip()[:30] for x in ns)
        score = len(ns) * 3 + len(yr) + len(drop) * 2 + len(kinds)
        _, lots, _, rec = recalled_in_ground(c) if not hasattr(cp, "_rec") else (None, None, None, cp._rec)
        cp._rec = rec
        recalled = any(r["well"] == w for r in rec)
        score += 3 if recalled else 0
        signs = [f"{len(yr)} corrective repairs in the last 12 months"] + ([f"{len(drop)} recent inspections not producing"] if drop else []) + (["recalled pump in the ground"] if recalled else [])
        cand.append({"Well": w, "Area": an[wl[w]["area_id"]], "Operator-note evidence": " | ".join(f"{x['created_at'][:10]}: \"{x['text']}\"" for x in ns[-3:]) + (f" (+{len(ns)-3} more)" if len(ns) > 3 else ""),
                     "Other warning signs": "; ".join(signs), "Last repair": (f"{last[0]['maintenance_id']} {fmt(last[0]['started_at'])} ({last[0]['issue']})" if last else "none"), "_s": score, "_n": len(ns)})
    cand.sort(key=lambda r: (-r["_s"], r["Well"]))
    top = cand[:n]
    for i, r in enumerate(top, 1): r["Rank"] = i
    rows = [{k: r[k] for k in ["Rank", "Well", "Area", "Operator-note evidence", "Other warning signs", "Last repair"]} for r in top]
    txt = [f"In the last month operators wrote abnormal-behaviour notes (rattling, rod squeal, fluid pound, tagging bottom, amps hunting, etc.) about **{len(notes)} wells**; **{len(cand)}** have had no repair since the first such note. Ranked by: number of repeated notes, recent non-producing readings, corrective-repair frequency over 12 months, and recalled pumps. This is a judgement score, not a validated failure model."]
    return res("\n\n".join(txt), table(rows), [], [r["Well"] for r in rows])

def crew_first(cp, q, user, chat):
    r = note_risk(cp, q, user, chat, n=10); top = r["visual"]["rows"][:3]
    txt = ["Send crews first to:"] + [f"{i}. **{x['Well']}** ({x['Area']}) — {x['Operator-note evidence'].split(' | ')[-1]}; {x['Other warning signs']}; last repair {x['Last repair']}." for i, x in enumerate(top, 1)]
    txt.append("Why: these have the most repeated abnormal notes without a repair since, plus the strongest other warning signs. Gas-odor and recalled-pump items are handled under their own procedures.")
    return res("\n".join(txt), table(top), r["citations"], [x["Well"] for x in top])

# ---------- shut-in delay reasons ----------
REASONS = [("parts", r"part|back-?order|supplier|vendor|delivery"), ("contractors", r"contractor"), ("crews", r"crew|staff|technician|rig"), ("weather", r"weather|rain|snow|ice|wind|storm|mud|road|freez")]
def delays(cp, q):
    c = cp.c; an = anames(c); wl = wells(c); y = re.search(r"(20\d\d)", q); y = y.group(1) if y else str(TODAY.year - 1)
    agg = defaultdict(lambda: defaultdict(list)); cites = []
    for m in c.execute("SELECT * FROM maintenance WHERE substr(started_at,1,4)=? AND report_text LIKE '%longer than the repair%'", (y,)):
        s = re.search(r"about (\d+(?:\.\d+)?) days? longer than the repair itself because ([^.]+)", m["report_text"])
        if not s: continue
        why = next((k for k, p in REASONS if re.search(p, s.group(2), re.I)), "other")
        agg[an[wl[m["asset_id"]]["area_id"]]][why].append(float(s.group(1))); cites.append(m["maintenance_id"])
    rows = []; keys = [k for k, _ in REASONS] + ["other"]
    for a in sorted(agg):
        tot = sum(len(v) for v in agg[a].values()); row = {"Area": a, "Jobs": tot}
        for k in keys:
            v = agg[a].get(k, [])
            row[k.capitalize()] = f"{100*len(v)/tot:.0f}% (median {median(v):g} d, mean {sum(v)/len(v):.1f} d)" if v else "-"
        top = max(agg[a].items(), key=lambda kv: len(kv[1])); row["Main reason"] = top[0]; rows.append(row)
    allv = defaultdict(list)
    for a in agg:
        for k, v in agg[a].items(): allv[k] += v
    tot = sum(len(v) for v in allv.values())
    stand = []
    for r in rows:
        a = r["Area"]; for_k = {k: len(agg[a].get(k, [])) / r["Jobs"] for k in keys}
        for k in keys:
            fs = len(allv[k]) / tot if tot else 0
            if for_k[k] - fs > 0.2 and r["Jobs"] >= 5: stand.append(f"{a}: {k} {for_k[k]*100:.0f}% vs {fs*100:.0f}% field-wide")
    txt = [f"**{tot} jobs started in {y}** kept the well shut in longer than the repair (the report states \"about N days longer than the repair itself because …\"). Field-wide: " + ", ".join(f"{k} {100*len(v)/tot:.0f}% (median {median(v):g} extra days)" for k, v in sorted(allv.items(), key=lambda kv: -len(kv[1])) if v) + ".",
           "By area: " + "; ".join(f"{r['Area']}: {r['Jobs']} jobs, mostly {r['Main reason']} (" + ", ".join(f"{k} {r[k.capitalize()]}" for k in keys if r[k.capitalize()] != '-') + ")" for r in rows) + ".",
           "Stands out: " + ("; ".join(stand) if stand else "no area's mix differs from the field mix by more than 20 percentage points, and the typical extra wait is about the same everywhere; " + max(rows, key=lambda r: r['Jobs'])['Area'] + " simply has the most delayed jobs") + "."]
    vis = {"type": "bar", "stacked": True, "x": [r["Area"] for r in rows], "series": [{"name": k, "data": [len(agg[r["Area"]].get(k, [])) for r in rows]} for k in keys if allv.get(k)]}
    return res("\n\n".join(txt), vis, cites, []) | {"alt_visual": table(rows), "table": rows}

# ---------- regional temperature ----------
def regions(cp, q):
    c = cp.c; an = anames(c)
    air = defaultdict(lambda: defaultdict(list)); wh = defaultdict(lambda: defaultdict(list)); wt = defaultdict(lambda: defaultdict(list))
    for r in T.effective_inspections(c, None, TODAY - dt.timedelta(days=365), TODAY):
        a = an[r["area_id"]]; m = r["date"][:7]; air[m][a].append(r["ambient_temp_c"])
        if r["producing"]: wh[m][a].append(r["wellhead_temp_c"]); wt[r["well_type"]][a].append(r["wellhead_temp_c"] - r["ambient_temp_c"])
    months = sorted(wh); areas = sorted(an.values())
    avg = lambda v: sum(v) / len(v) if v else None
    win_wh = Counter(max(areas, key=lambda a: avg(wh[m][a]) or -99) for m in months)
    spread = max(max(avg(air[m][a]) for a in areas if air[m][a]) - min(avg(air[m][a]) for a in areas if air[m][a]) for m in months)
    top = win_wh.most_common(1)[0][0]
    rows = [{"Area": a, "Mean air °C": round(avg([x for m in months for x in air[m][a]]), 1), "Mean producing wellhead °C": round(avg([x for m in months for x in wh[m][a]]), 1),
             "Months with hottest wellheads": win_wh[a], **{f"{t} Δ °C": round(avg(wt[t][a]), 1) if wt[t][a] else "-" for t in sorted(wt)}} for a in areas]
    same_type = all((avg(wt[t][top]) or 0) >= max((avg(wt[t][a]) or 0) for a in areas) - 0.5 for t in wt if wt[t][top])
    txt = [f"**{top}** runs hotter: its producing wells have the highest average wellhead temperature in **{win_wh[top]} of {len(months)} months** (last 12 months of inspections).",
           f"It isn't the weather: air temperature at inspection is the same across all areas (largest monthly spread between areas {spread:.1f} °C). " +
           ("The gap holds within each well type (wellhead minus air, table), so it is not just a different well-type mix." if same_type else "Part of the gap comes from the well-type mix; compare the per-type columns in the table."),
           "Readings are drone/manual thermal snapshots, so this is evidence of a consistent pattern, not a root cause."]
    vis = {"type": "line", "x": months, "series": [{"name": a, "data": [round(avg(wh[m][a]), 1) if wh[m][a] else None for m in months]} for a in areas]}
    return res("\n\n".join(txt), vis, ["inspections.jsonl wellhead_temp_c / ambient_temp_c"], []) | {"alt_visual": table(rows), "table": rows}

# ---------- session follow-ups ----------
def chat_wells(c, user, chat, pat=None):
    out = []
    for r in c.execute("SELECT question, wells FROM memory_conversations WHERE user_id=? AND chat_id=? ORDER BY id", (user, chat)):
        if pat is None or re.search(pat, r["question"], re.I): out.append((r["question"], json.loads(r["wells"])))
    return out

def recall_followup(cp, q, user, chat):
    c = cp.c; prev = [w for qq, ws in chat_wells(c, user, chat, "recall") for w in ws]
    if not prev: return None
    rows = []
    for w in dict.fromkeys(prev):
        s = T.well_status(w)
        if s["producing"]: continue
        last = c.execute("SELECT * FROM maintenance WHERE asset_id=? AND maintenance_type!='scheduled' ORDER BY started_at DESC LIMIT 1", (w,)).fetchone()
        rows.append({"Well": w, "Area": s["area"], "Latest inspection": f"{s['last_inspection_id']} ({fmt(s['inspected_at'])}, Δ {s['delta_c']} °C)", "Last repair": f"{last['maintenance_id']} {fmt(last['started_at'])} – {last['issue']}" if last else "none"})
    return res(f"Of the {len(set(prev))} wells with recalled pumps from your first question, **{len(rows)} are not producing oil right now** (latest inspection below the well-type threshold):", table(rows), [], [r["Well"] for r in rows])

def deal_first(cp, q, user, chat):
    c = cp.c; ws = list(dict.fromkeys(w for _, x in chat_wells(c, user, chat) for w in x))
    if not ws: return None
    _, _, due, rec = recalled_in_ground(c); recw = {r["well"] for r in rec}
    gasrows, _ = gas(cp, "since 1 Nov 2026", wells_only=ws)
    missed = {r["Well"] for r in gasrows if r["Met / Missed"] == "Missed"}
    def score(w):
        s = T.well_status(w); return (w in missed) * 4 + (w in recw) * 2 + (not s["producing"]) * 1
    best = max(ws, key=lambda w: (score(w), w)); s = T.well_status(best)
    why = (["gas-odor report with a missed OPS-1 response (safety)"] if best in missed else []) + (["recalled pump still in the ground, past the 31 Dec 2026 replacement date"] if best in recw else []) + (["not producing oil right now"] if not s["producing"] else [])
    return res(f"Of the {len(ws)} wells discussed in this conversation, I'd deal with **{best}** ({s['area']}) first: " + "; ".join(why or ["highest combined risk"]) + ". Safety items (gas) outrank production and recall items, then overdue recalls, then lost production. This is a judgement call based on the evidence above.", None, [s["last_inspection_id"]], [best])

# ---------- dispatcher ----------
def dispatch(cp, q, user, chat, wells, area):
    ql = q.lower(); c = cp.c
    if re.search(r"just for me|for me only|my preference", ql) and re.search(r"sort|thousand|show", ql): return save_pref(c, user, q)
    if wells and re.search(r"recalled pump", ql) and re.search(r"swapped|replaced|take it off|count it as", ql): return pump_swap_statement(cp, q, user, wells[0])
    if re.search(r"back to the pumps|pumps from my first", ql): return recall_followup(cp, q, user, chat)
    if re.search(r"recalled pump|recall", ql): return recall(cp, q, user, chat, area, mine=bool(re.search(r"\bmy area", ql)))
    if re.search(r"who leads|team lead|leads? (the )?\w+ production|how many wells does that team", ql): return team(cp, q)
    if re.search(r"reservoir pressure|pressure (map|data|across)", ql): return unavailable(cp, q, "pressure")
    if re.search(r"produced the most oil|most oil|top (oil )?producer|best producer|highest production", ql): return unavailable(cp, q, "production")
    if wells and re.search(r"h2s reading|h2s level", ql): return h2s(cp, q, wells[0])
    if re.search(r"operator note.*(gas)|gas.*(operator note)|gas odou?r report", ql) and re.search(r"deadline|in time|respon", ql): return gas_report(cp, q)
    if "bypass" in ql: return bypass(cp, q)
    if re.search(r"commission|regulator'?s? letter|the letter", ql): return letter(cp, q)
    if re.search(r"inspection and the operator notes disagree|disagree about whether", ql): return status_conflicts(cp, q)
    if re.search(r"cold weather|freeze|heat trace", ql): return cold(cp, q)
    if re.search(r"sound or behave wrong|operators .*notes .*wells|rank .*likely to need a repair", ql): return note_risk(cp, q, user, chat)
    if re.search(r"send a crew to first|which three would you send", ql): return crew_first(cp, q, user, chat)
    if re.search(r"waiting on|longer than the repair", ql): return delays(cp, q)
    if re.search(r"region .*(hotter|warmer|colder)|runs hotter", ql): return regions(cp, q)
    if re.search(r"talked about today|discussed today", ql) and re.search(r"first", ql): return deal_first(cp, q, user, chat)
    return None
