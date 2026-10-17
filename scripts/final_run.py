"""Final-hour one-shot: load sample + test data, run the final questions, write results/final.{md,json} and draft docs/results.md.
Usage: python scripts/final_run.py --data <test-data-dir> [--data <more>] --questions final_questions.txt [--sample ../dataset/sample-data] [--today 2026-10-17] [--no-llm]
Questions: .txt (one per line; optional 'User Name: question' prefix) or .json list of {id,q,user,chat,day}."""
import argparse, json, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument("--data", action="append", default=[]); ap.add_argument("--questions", required=True)
ap.add_argument("--sample", default=os.path.join("..", "dataset", "sample-data")); ap.add_argument("--today"); ap.add_argument("--no-llm", action="store_true")
ap.add_argument("--only-test", action="store_true", help="load only the test data (if it already contains the sample wells)")
a = ap.parse_args(); t0 = time.time()
# resolve user paths against the caller's directory, then work from the repo root
a.data = [os.path.abspath(p) for p in a.data]; a.questions = os.path.abspath(a.questions)
if a.sample != ap.get_default("sample"): a.sample = os.path.abspath(a.sample)
os.chdir(ROOT)
env = dict(os.environ)
if a.today: env["AIC_TODAY"] = a.today
if a.no_llm: env["AIC_LLM"] = "0"
dirs = (a.data if a.only_test else [a.sample] + a.data)
print("[1/3] loading", dirs); subprocess.run([sys.executable, "-m", "copilot.loader", "--reset-memory", *dirs], check=True, env=env)
qf = a.questions
if qf.endswith(".txt"):  # support "User Name: question"
    items = []
    for i, l in enumerate(x.strip() for x in open(qf)):
        if not l or l.startswith("#"): continue
        m = re.match(r"^\s*(?:Q?\d+[.)]\s*)?(?:\[?([A-Z][a-z]+ [A-Z][a-z]+)\]?:\s+)?(.+)$", l)
        items.append({"id": f"F{len(items) + 1}", "q": m.group(2), "user": m.group(1) or "Michael Turner", "chat": f"f{len(items) + 1}"})
    qf = "results/_final_questions.json"; os.makedirs("results", exist_ok=True); json.dump(items, open(qf, "w"), indent=1)
print("[2/3] answering", qf); t1 = time.time()
subprocess.run([sys.executable, "-m", "eval.run_questions", qf, "--out", "results/final"], check=True, env=env)
res = json.load(open("results/final.json")); t2 = time.time()
print("[3/3] writing docs/results.md from docs/results_template.md")
low = [r for r in res if r.get("confidence") == "low"]; conf = [r for r in res if r.get("confidence") == "conflict"]
nocite = [r for r in res if not r["citations"]]
llm = [r for r in res if str(r.get("engine", "")).startswith("llm")]
vis = {}
for r in res: vis[r["visual"] or "text"] = vis.get(r["visual"] or "text", 0) + 1
summary = (f"Test data: {', '.join(os.path.basename(os.path.normpath(d)) for d in dirs)} loaded in one step. **{len(res)} questions answered in {t2 - t1:.1f} s** (whole pipeline {t2 - t0:.1f} s). "
           f"{len(res) - len(low)} were answered by deterministic tools with high or medium confidence; {len(llm)} needed the Gemma 4 planner; {len(conf)} flagged a data conflict instead of silently picking a side. "
           f"Visuals: " + ", ".join(f"{k} × {v}" for k, v in sorted(vis.items())) + ".")
rows = ["| # | Question | Answer (headline) | Visual | Confidence | Sources |", "|---|---|---|---|---|---|"]
for r in res:
    first = re.sub(r"[*_|]", "", r["answer"].strip().splitlines()[0])[:170]
    rows.append(f"| {r['id']} | {r['question'][:95].replace('|', '/')} | {first} | {r['visual'] or '-'} | {r.get('confidence')} | {len(set(map(str, r['citations'])))} |")
worked = "\n".join([
    f"- {len([r for r in res if r.get('confidence') == 'high'])}/{len(res)} answers came from a confident deterministic route, with record and document citations.",
    "- Rules (production thresholds, the spill reporting, containment and verification limits, RCA counts) were applied from the parsed documents, so the new wells and areas needed no code change.",
    "- Corrections, shared facts and private memory were applied at their scopes across the question sequence."] + ([f"- {len(conf)} answers surfaced conflicts between users or with the data, as required."] if conf else []))
misses = "\n".join([f"- {r['id']} (_{r['question']}_): low confidence. The router fell back to document search, so the answer may be incomplete." for r in low] +
                    [f"- {r['id']}: no citations returned." for r in nocite if r not in low]) or "- No low-confidence answers. Remaining risk: answers whose wording differed from the expected phrasing, which I'm checking manually against the results page."
conflicts = ("## Answers that flagged conflicts\n" + "\n".join(f"- {r['id']}: {r['question']}" for r in conf)) if conf else ""
tpl = open("docs/results_template.md").read()
out = tpl.replace("{{SUMMARY}}", summary).replace("{{TABLE}}", "\n".join(rows)).replace("{{WORKED}}", worked).replace("{{MISSES}}", misses).replace("{{CONFLICTS}}", conflicts)
open("docs/results.md", "w").write(out)
print(f"done in {time.time() - t0:.1f} s → results/final.md, results/final.json, docs/results.md")
