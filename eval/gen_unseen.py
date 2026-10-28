"""Generate 40+ unseen-style questions with expected answers computed INDEPENDENTLY from the raw dataset files
(plain json/re, no copilot code). Usage: python eval/gen_unseen.py <sample-data> > eval/unseen.json"""
import json, glob, os, re, sys, datetime as dt
from collections import defaultdict
D = sys.argv[1] if len(sys.argv) > 1 else "../dataset/sample-data"
TODAY = dt.date(2026, 10, 17); Y = TODAY - dt.timedelta(days=1)
THR = {}
for p in glob.glob(f"{D}/fleet/well-types/*.md"):
    THR[os.path.basename(p)[:-3]] = float(re.search(r"at least \*\*([\d.]+) °C above", open(p).read()).group(1))
areas = json.load(open(f"{D}/fleet/areas.json")); AN = {a["area_id"]: a["name"] for a in areas["areas"]}
UN = {u["user_id"]: u["name"] for u in json.load(open(f"{D}/fleet/users.json"))["users"]}
W = {}
for d in sorted(glob.glob(f"{D}/assets/*")):
    rd = lambda n: [json.loads(l) for l in open(f"{d}/{n}") if l.strip()] if os.path.exists(f"{d}/{n}") else []
    m = json.load(open(f"{d}/metadata.json")); notes = rd("context.jsonl")
    void = {n["inspection_id"] for n in notes if n["note_type"] == "correction"}
    ins = rd("inspections.jsonl")
    for i in ins: i["prod"] = i["wellhead_temp_c"] - i["ambient_temp_c"] >= THR[m["well_type"]]; i["d"] = i["inspected_at"][:10]; i["spill"] = i["spill_detected"] and i["inspection_id"] not in void
    mnt = rd("maintenance.jsonl")
    for x in mnt:
        x["contained"] = None
        if x.get("report_file") and os.path.exists(f"{d}/{x['report_file']}"):
            mm = re.search(r"contained (?:about )?([\d.]+) hours", open(f"{d}/{x['report_file']}").read(), re.I); x["contained"] = float(mm.group(1)) if mm else None
    W[m["asset_id"]] = {"m": m, "ins": ins, "mnt": mnt, "reg": rd("regulatory-events.jsonl"), "notes": notes}
def sel(area=None, wt=None, team=None): return [k for k, v in W.items() if (not area or v["m"]["area_id"] == area) and (not wt or v["m"]["well_type"] == wt) and (not team or v["m"]["team_id"] == team)]
def down(ids, a, b): return {k: 7 * sum(1 for i in W[k]["ins"] if a <= i["d"] <= b and not i["prod"]) for k in ids}
def spills(ids, a="0", b="9"): return [(k, i) for k in ids for i in W[k]["ins"] if i["spill"] and a <= i["d"] <= b]
def cost(ids, a, b, **f): return sum(x["cost_usd"]["total"] for k in ids for x in W[k]["mnt"] if a <= x["started_at"][:10] <= b and all(x.get(kk) == vv for kk, vv in f.items()))
def nrep(ids, a, b, **f): return sum(1 for k in ids for x in W[k]["mnt"] if a <= x["started_at"][:10] <= b and all(x.get(kk) == vv for kk, vv in f.items()))
def g(v): return f"{v:g}"
def usd(v): return f"USD {v:,.0f}"
Q = []
def add(q, expect, visual=None, reject=None, user="Emily Carter"):
    Q.append({"id": f"U{len(Q) + 1}", "user": user, "chat": f"u{len(Q) + 1}", "q": q, "expect": [str(e) for e in expect], **({"visual": visual} if visual else {}), **({"reject": reject} if reject else {})})
# --- producing status, one well
for w in ["WELL-0050", "WELL-0013", "WELL-0172", "WELL-0120"]:
    l = W[w]["ins"][-1]; add(f"Is {w} producing oil right now?", ["is producing" if l["prod"] else "is not producing", l["inspection_id"], UN[l["inspector_user_id"]]], "card")
# --- not producing now per area
for a in ["SW-23", "SW-24", "NE-07"]:
    ids = [k for k in sel(a) if not W[k]["ins"][-1]["prod"]]
    add(f"Which wells in {AN[a]} are not producing oil right now?", [f"{len(ids)} wells"] + ids, "table")
ids = [k for k in W if not W[k]["ins"][-1]["prod"]]; add("How many wells across the whole field are not producing oil right now?", [str(len(ids))])
# --- stale recorded status
st = [k for k in W if (W[k]["m"]["recorded_status"] == "active") != W[k]["ins"][-1]["prod"]]
add("Which wells have an out-of-date recorded status?", [str(len(st))] + st[:5])
st2 = [k for k in st if W[k]["m"]["area_id"] == "SW-24"]; add(f"Which wells in Southwest Block 24 have a stale recorded status?", [str(len(st2))] + st2)
# --- downtime
for w, yr in [("WELL-0121", 2025), ("WELL-0005", 2026), ("WELL-0164", 2024)]:
    add(f"How many days was {w} down in {yr}?", [f"{down([w], f'{yr}-01-01', f'{yr}-12-31')[w]} days"])
d = down(sel("SW-24"), "2026-06-01", "2026-08-31"); top = sorted(d.items(), key=lambda x: (-x[1], x[0]))[:3]
add("Which 3 wells in Southwest Block 24 were down the longest this summer, and why?", [f"{k}: {v} days" for k, v in top], "bar")
d = down(list(W), "2026-06-01", "2026-08-31"); by = defaultdict(int)
for k, v in d.items(): by[AN[W[k]["m"]["area_id"]]] += v
add("Show downtime by area this summer as a bar chart.", [f"{a}: {v} days" for a, v in by.items()], "bar")
d = down(sel(wt="T200"), "2025-01-01", "2025-12-31"); add("What was the total downtime of T200 wells in 2025?", [f"{sum(d.values()):,}".replace(",", "") + " days"])
s = T = None
s0 = (Y.replace(month=Y.month - 3)); d = down(sel(team="TEAM-NE"), str(s0), str(Y)); add("How much downtime did the Northeast Production team have in the last 3 months?", [f"{sum(d.values())} days"])
d = down(sel("NE-08"), "2026-01-01", str(Y)); top = sorted(d.items(), key=lambda x: (-x[1], x[0]))[:5]
add("Top 5 wells in Northeast Block 8 by downtime this year", [f"{k}: {v} days" for k, v in top])
d = down(["WELL-0001", "WELL-0005", "WELL-0121"], "2026-01-01", str(Y)); add("Compare downtime of WELL-0001, WELL-0005 and WELL-0121 in 2026 as a bar chart.", [f"{k}: {v} days" for k, v in d.items()], "bar")
# --- spills
for w in ["WELL-0082", "WELL-0151"]:
    sp = spills([w]); add(f"How many oil spills has {w} had in total, and how much oil?", [f"{len(sp)} real spills", g(round(sum(i['spill_est_volume_bbl'] for _, i in sp), 1))], "table")
sp = spills(sel("NE-07"), "2026-03-01", "2026-03-31"); add("How many spills were there in Northeast Block 7 in March 2026?", [f"{len(sp)} real spills"])
sp = spills(sel(wt="T350"), "2026-03-01", "2026-03-31"); add("How many spills did T350 wells have in March 2026?", [f"{len(sp)} in total"])
sp = spills(sel(team="TEAM-SW"), "2025-01-01", "2025-12-31"); add("How much oil did the Southwest Production team spill in 2025?", [g(round(sum(i['spill_est_volume_bbl'] for _, i in sp), 1)) + " bbl"])
sp = spills(list(W), "2026-01-01", str(Y)); bm = defaultdict(int)
for _, i in sp: bm[i["d"][:7]] += 1
add("Show spills by month in 2026", [f"{k}: {v}" for k, v in sorted(bm.items())], "line")
for wt in ["T200", "T350"]: pass
sp = spills(list(W), "2025-01-01", "2025-12-31"); bt = defaultdict(int)
for k, _ in sp: bt[W[k]["m"]["well_type"]] += 1
add("Compare spills by well type in 2025", [f"{k}: {v}" for k, v in sorted(bt.items())], "bar")
sp = spills(sel("SW-23"), "2026-05-01", "2026-07-31"); add("How many spills were there in Southwest Block 23 between 1 May 2026 and 31 Jul 2026?", [f"{len(sp)} real spills"])
sp = spills(sel("SW-24"), str(TODAY - dt.timedelta(days=60)), str(Y)); add("Show on a map the wells in Southwest Block 24 with a real spill in the last 60 days.", sorted({k for k, _ in sp}), "map")
# --- repairs & cost
for w, yr in [("WELL-0001", 2025), ("WELL-0170", 2026)]:
    add(f"What did repairs on {w} cost in {yr}?", [usd(cost([w], f"{yr}-01-01", f"{yr}-12-31"))])
by = {AN[a]: cost(sel(a), "2025-01-01", "2025-12-31") for a in AN}; add("Compare repair cost by area in 2025", [f"{a}: {usd(v)}" for a, v in by.items()], "bar")
s12 = str(Y.replace(year=Y.year - 1))
add("How many corrective flowline repairs were there in Northeast Block 8 in the last 12 months?", [str(nrep(sel("NE-08"), s12, str(Y), maintenance_type="corrective", equipment_kind="flowline")) + " in total"])
add("What did T350 wells spend on repairs in 2026?", [usd(cost(sel(wt="T350"), "2026-01-01", str(Y)))])
add("What was the total repair cost for the Northeast Production team between 1 Jan 2026 and 30 Jun 2026?", [usd(cost(sel(team="TEAM-NE"), "2026-01-01", "2026-06-30"))])
# --- regulator events / fines
fin = sum(e["fine_usd"] or 0 for k in W for e in W[k]["reg"]); add("How much have we been fined in total across the field?", [usd(fin)])
op = sorted({k for k in W for e in W[k]["reg"] if e["status"] == "open" and e["fine_usd"]}); add("Which wells have open fines?", op)
nov = sum(1 for k in W for e in W[k]["reg"] if e["event_type"] == "notice_of_violation" and e["date"].startswith("2025")); add("How many notices of violation did we receive in 2025?", [f"{nov} in total"])
f26 = sum(e["fine_usd"] or 0 for k in sel(team="TEAM-SW") for e in W[k]["reg"] if e["date"] >= "2026-01-01"); add("What fines did the Southwest Production team get in 2026?", [usd(f26)])
# --- SOP compliance: containment & reporting in other areas/windows
for a, days in [("NE-07", 90), ("SW-23", 365)]:
    a0 = str(TODAY - dt.timedelta(days=days)); hits = []
    for k in sel(a):
        ins = {i["inspection_id"]: i for i in W[k]["ins"]}
        for x in W[k]["mnt"]:
            t = x.get("triggered_by_inspection_id")
            if t in ins and ins[t]["spill"] and ins[t]["d"] >= a0 and x["contained"] and x["contained"] > 4: hits.append(k)
    add(f"In {AN[a]}, which spills in the last {days} days were not contained within the SOP time limit?", [f"{len(hits)} spills"] + sorted(set(hits)), "table")
for a in ["SW-23", "NE-07"]:
    rp = [k for k, i in spills(sel(a), str(TODAY - dt.timedelta(days=90)), str(Y)) if i["spill_est_volume_bbl"] >= 5]
    add(f"Which spills in {AN[a]} in the last 90 days needed a report to the regulator?", ([f"{len(rp)} spill(s)"] + rp) if rp else ["No spill"])
# --- notes and planned shutdowns
for w in ["WELL-0101", "WELL-0013"]:
    ns = W[w]["notes"]; add(f"What notes do we have on {w}?", [n["note_id"] for n in ns] or ["0 in total"])
add("Is any downtime planned for WELL-0001?", ["Yes", "CTX-0001-003", "20 Oct"])
# --- compliance one well
add("Which rules has WELL-0082 broken in the last 12 months?", ["SR-02", "MNT-0082-028"])
print(json.dumps(Q, indent=1))
