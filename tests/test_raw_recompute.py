"""Independent recomputation straight from the raw JSON files (no SQLite, no copilot code) to validate expected answers."""
import json, glob, os, re, datetime as dt
from collections import Counter
from conftest import DATA

def wells():
    for d in sorted(glob.glob(os.path.join(DATA, "assets", "*"))):
        m = json.load(open(os.path.join(d, "metadata.json")))
        ins = [json.loads(l) for l in open(os.path.join(d, "inspections.jsonl")) if l.strip()]
        notes = [json.loads(l) for l in open(os.path.join(d, "context.jsonl")) if l.strip()] if os.path.exists(os.path.join(d, "context.jsonl")) else []
        yield m, ins, notes

THR = {"T200": 15, "T350": 20}

def test_q4_q8_spills_raw():
    area = {a["area_id"]: a["name"] for a in json.load(open(os.path.join(DATA, "fleet", "areas.json")))["areas"]}
    heat = Counter(); w1 = None
    for m, ins, notes in wells():
        voided = {n["inspection_id"] for n in notes if n["note_type"] == "correction"}
        real = [i for i in ins if i["spill_detected"] and i["inspection_id"] not in voided]
        if m["asset_id"] == "WELL-0001": w1 = real
        for i in real:
            if i["inspected_at"].startswith("2026"): heat[area[m["area_id"]]] += 1
    assert len(w1) == 6 and round(sum(i["spill_est_volume_bbl"] for i in w1), 1) == 15.1
    assert heat == {"Southwest Block 23": 35, "Southwest Block 24": 43, "Northeast Block 7": 37, "Northeast Block 8": 26}

def test_q5_q6_downtime_raw():
    res = {}
    for m, ins, _ in wells():
        down = lambda a, b: 7 * sum(1 for i in ins if a <= i["inspected_at"][:10] <= b and i["wellhead_temp_c"] - i["ambient_temp_c"] < THR[m["well_type"]])
        if m["asset_id"] == "WELL-0001": assert down("2025-01-01", "2025-12-31") == 21
        if m["area_id"] == "NE-07": res[m["asset_id"]] = down("2026-06-16", "2026-10-16")
    top = sorted(res.items(), key=lambda x: -x[1])[:4]
    assert dict(top[:3]) == {"WELL-0121": 49, "WELL-0138": 42, "WELL-0107": 42} and top[3] == ("WELL-0119", 28)

def test_q10_containment_raw():
    hits = []
    for d in glob.glob(os.path.join(DATA, "assets", "*")):
        m = json.load(open(os.path.join(d, "metadata.json")))
        if m["area_id"] != "SW-24": continue
        ins = {json.loads(l)["inspection_id"]: json.loads(l) for l in open(os.path.join(d, "inspections.jsonl"))}
        for l in open(os.path.join(d, "maintenance.jsonl")):
            x = json.loads(l); t = x.get("triggered_by_inspection_id")
            if x.get("report_file") and t in ins and ins[t]["spill_detected"] and ins[t]["inspected_at"][:10] >= "2026-07-19":
                mm = re.search(r"contained (?:about )?([\d.]+) hours", open(os.path.join(d, x["report_file"])).read(), re.I)
                if mm and float(mm.group(1)) > 4: hits.append((m["asset_id"], float(mm.group(1))))
    assert sorted(hits) == [("WELL-0082", 7.1), ("WELL-0100", 8.1)]
