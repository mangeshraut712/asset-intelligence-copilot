"""46 unseen-style questions whose expected answers are computed independently from raw files (eval/gen_unseen.py)."""
import json, os, subprocess, sys, pytest
from copilot import agent
from conftest import ROOT, DATA, wipe

def _qs():
    out = subprocess.run([sys.executable, os.path.join(ROOT, "eval", "gen_unseen.py"), DATA], capture_output=True, text=True, check=True).stdout
    return json.loads(out)
QS = _qs()

@pytest.fixture(scope="module")
def results():
    wipe(); cp = agent.Copilot(); agent.SIM_DAY = 0
    out = {x["id"]: cp.ask(x["q"], x["user"], x["chat"]) for x in QS}; wipe(); return out

@pytest.mark.parametrize("x", QS, ids=[x["id"] for x in QS])
def test_unseen(results, x):
    r = results[x["id"]]; blob = (r["text"] + json.dumps(r.get("visual"), default=str)).lower()
    assert [e for e in x["expect"] if e.lower() not in blob] == [], r["text"][:400]
    if x.get("visual"): assert (r.get("visual") or {}).get("type") == x["visual"]
