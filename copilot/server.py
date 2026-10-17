"""FastAPI server: chat API + static UI."""
import os, json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from .agent import Copilot, llm_available, llm_config
from .tools import db

app = FastAPI(title="Asset Intelligence Copilot")
cp = Copilot()
WEB = os.path.join(os.path.dirname(__file__), "..", "web")

class Ask(BaseModel):
    question: str
    user: str = "U-201"
    chat: str = "default"

@app.get("/")
def index(): return FileResponse(os.path.join(WEB, "index.html"))

@app.get("/samples/{name}")
def sample(name: str):
    p = os.path.join(WEB, "samples", os.path.basename(name))
    return FileResponse(p)

@app.get("/api/users")
def users(): return [dict(r) for r in db().execute("SELECT * FROM users ORDER BY user_id")]

@app.get("/api/briefing")
def get_briefing():
    from .insights import briefing
    return briefing()

@app.get("/api/evidence")
def get_evidence(ref: str):
    from .insights import evidence
    return json.loads(json.dumps(evidence(ref), default=str))

class Phrase(BaseModel):
    question: str
    text: str

@app.post("/api/phrase")
def api_phrase(p: Phrase):
    from .gemma import phrase
    try: return phrase(p.question, p.text)
    except Exception as e: return {"ok": False, "reason": str(e)[:200]}

@app.post("/api/vision")
async def api_vision(file: UploadFile = File(...), well: str = Form(""), user: str = Form("U-201")):
    from .gemma import describe_image
    data = await file.read()
    if len(data) > 6_000_000: return {"ok": False, "reason": "image too large (max 6 MB)"}
    ctx = ""
    if well:
        from .tools import well_status
        s = well_status(well.upper())
        if "error" not in s: ctx = f"Context from records: {well.upper()} latest inspection {s['last_inspection_id']} shows {'producing' if s['producing'] else 'not producing'}."
    try:
        r = describe_image(data, file.content_type or "image/jpeg", ctx); r["context"] = ctx; return r
    except Exception as e: return {"ok": False, "reason": str(e)[:200]}

@app.get("/api/healthz")
def healthz(): return {"ok": True}

@app.get("/api/status")
def status():
    cfg = llm_config()
    return {"llm": bool(llm_available()), "model": cfg[2] if cfg else None, "wells": db().execute("SELECT count(*) FROM wells").fetchone()[0]}

@app.get("/api/memory")
def memory(user: str = "U-201"):
    c = db()
    return {"conversations": [dict(r) for r in c.execute("SELECT id,chat_id,ts,question,wells FROM memory_conversations WHERE user_id=? ORDER BY id DESC LIMIT 30", (user,))],
            "shared_facts": [dict(r) for r in c.execute("SELECT * FROM memory_well_facts ORDER BY id DESC")],
            "corrections": [dict(r) for r in c.execute("SELECT * FROM memory_corrections ORDER BY id DESC")],
            "type_rules": [dict(r) for r in c.execute("SELECT * FROM memory_type_rules ORDER BY id DESC")]}

@app.post("/api/ask")
def ask(a: Ask): return json.loads(json.dumps(cp.ask(a.question, a.user, a.chat), default=str))
