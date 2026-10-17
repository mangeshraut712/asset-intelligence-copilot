"""Run a list of questions through the copilot and save the answers (JSON + Markdown).
Usage: python -m eval.run_questions eval/examples.json [--out results/examples] [--fresh]
Questions file: list of {id, q, user?, chat?, day?, expect?[], reject?[], visual?}. If 'expect' is present, a score is computed.
--fresh resets runtime memory first (scenarios are sequential, as in the example doc)."""
import json, os, sys, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from copilot import agent
from copilot.loader import DB_PATH

def main():
    args = sys.argv[1:]; path = args[0]; out = args[args.index("--out") + 1] if "--out" in args else "results/" + os.path.splitext(os.path.basename(path))[0]
    if "--fresh" in args:
        c = sqlite3.connect(DB_PATH)
        for t in ["memory_conversations", "memory_well_facts", "memory_corrections", "memory_type_rules"]: c.execute(f"DELETE FROM {t}")
        c.commit(); c.close()
    qs = json.load(open(path)) if path.endswith(".json") else [{"id": f"Q{i+1}", "q": l.strip()} for i, l in enumerate(open(path)) if l.strip()]
    cp = agent.Copilot(); res = []; passed = scored = 0
    for x in qs:
        agent.SIM_DAY = x.get("day", 0)
        r = cp.ask(x["q"], x.get("user", "Michael Turner"), x.get("chat", x["id"]))
        blob = r["text"] + "\n" + json.dumps(r.get("visual"), default=str)
        item = {"id": x["id"], "user": r["user"], "question": x["q"], "answer": r["text"], "visual": (r.get("visual") or {}).get("type"), "citations": r["citations"], "engine": r["engine"], "confidence": r.get("confidence"), "trace": r.get("trace"), "visual_data": r.get("visual")}
        if "expect" in x:
            miss = [e for e in x["expect"] if e.lower() not in blob.lower()]
            bad = [e for e in x.get("reject", []) if e.lower() in r["text"].lower()]
            vis_ok = x.get("visual") is None or item["visual"] == x["visual"]
            item |= {"missing": miss, "unexpected": bad, "visual_ok": vis_ok, "pass": not miss and not bad and vis_ok}
            scored += 1; passed += item["pass"]
        res.append(item)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    json.dump(res, open(out + ".json", "w"), indent=1, default=str)
    with open(out + ".md", "w") as f:
        f.write(f"# Copilot answers ({os.path.basename(path)})\n\n" + (f"**Score: {passed}/{scored}**\n\n" if scored else ""))
        for it in res:
            f.write(f"## {it['id']} — {it['user']}\n**Q:** {it['question']}\n\n{it['answer']}\n\n*Visual:* {it['visual']} · *Citations:* {', '.join(map(str, it['citations'][:25]))}\n\n")
            if "pass" in it: f.write(f"*Check:* {'PASS' if it['pass'] else 'FAIL'} {it['missing'] or ''} {it['unexpected'] or ''} {'' if it['visual_ok'] else 'visual mismatch'}\n\n")
    for it in res:
        if "pass" in it: print(f"{it['id']:6} {'PASS' if it['pass'] else 'FAIL'} vis={it['visual']} {it['missing'] or ''} {it['unexpected'] or ''}")
    if scored: print(f"SCORE {passed}/{scored}")

if __name__ == "__main__": main()
