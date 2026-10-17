"""All 18 example scenarios (27 checks) run in sequence, rule router only."""
import json, os, pytest
from copilot import agent
from conftest import ROOT, wipe

EX = json.load(open(os.path.join(ROOT, "eval", "examples.json")))

@pytest.fixture(scope="module")
def results():
    wipe(); cp = agent.Copilot(); out = {}
    for x in EX:
        agent.SIM_DAY = x.get("day", 0); out[x["id"]] = cp.ask(x["q"], x["user"], x["chat"])
    wipe(); return out

@pytest.mark.parametrize("x", EX, ids=[x["id"] for x in EX])
def test_example(results, x):
    r = results[x["id"]]; blob = (r["text"] + json.dumps(r.get("visual"), default=str)).lower()
    assert [e for e in x["expect"] if e.lower() not in blob] == []
    assert [e for e in x.get("reject", []) if e.lower() in r["text"].lower()] == []
    if x.get("visual"): assert (r.get("visual") or {}).get("type") == x["visual"]
