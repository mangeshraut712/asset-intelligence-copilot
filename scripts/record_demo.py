"""Record the demo screen capture by driving the real UI with Playwright (1280x720), with on-screen cue overlays.
Writes video/demo.mp4, video/demo.srt (cue timings), video/narration.txt (lines to read in your own voice). No synthetic voice."""
import asyncio, json, os, subprocess, sys, time, glob, shutil
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else "/workspace/ahc-hackday/video"
URL = os.environ.get("AIC_URL", "http://localhost:8000/")
os.makedirs(OUT, exist_ok=True); CUES = []; T0 = [0.0]

OVERLAY_JS = """
() => { if (document.getElementById('cap')) return;
 const c=document.createElement('div');c.id='cap';c.style.cssText='position:fixed;left:50%;bottom:118px;transform:translateX(-50%);max-width:1100px;background:rgba(0,0,0,.78);color:#fff;font:600 19px/1.35 Inter,system-ui,sans-serif;padding:10px 18px;border-radius:10px;z-index:99999;text-align:center;pointer-events:none;display:none';document.body.appendChild(c);
 const s=document.createElement('div');s.id='slide';s.style.cssText='position:fixed;inset:0;z-index:99998;display:none;background:radial-gradient(circle at 30% 20%,#1f2937,#0b0f14);color:#e7ebef;font-family:Inter,system-ui,sans-serif;padding:60px 80px;box-sizing:border-box';document.body.appendChild(s);}"""

async def cap(pg, text, secs):
    t = time.monotonic() - T0[0]; CUES.append((t, t + secs, text))
    await pg.evaluate("t=>{const c=document.getElementById('cap');c.textContent=t;c.style.display=t?'block':'none'}", text)
    await pg.wait_for_timeout(int(secs * 1000))

async def slide(pg, html):
    await pg.evaluate("h=>{const s=document.getElementById('slide');s.innerHTML=h;s.style.display=h?'block':'none'}", html)

async def ask(pg, q, wait_gemma=0):
    n = await pg.locator(".turn .a").count()
    await pg.click("#q"); await pg.keyboard.type(q, delay=18); await pg.click("form button.pri")
    await pg.wait_for_function(f"document.querySelectorAll('.turn .a').length>{n} && document.querySelectorAll('.turn .a')[{n}].querySelector('.badge')", timeout=120000)
    if wait_gemma:
        try: await pg.wait_for_function(f"(()=>{{const g=document.querySelectorAll('.turn .a')[{n}].querySelector('.gem');return !g||!/writing/.test(g.textContent)}})()", timeout=wait_gemma * 1000)
        except Exception: pass
    return pg.locator(".turn .a").nth(n)

INTRO = """<div style="height:100%;display:flex;flex-direction:column;justify-content:center"><div style="font-size:20px;color:#f5a524;font-weight:700;letter-spacing:.08em">FLYTBASE CHALLENGE · AHC × HACKTOBERFEST 2026</div>
<div style="font-size:64px;font-weight:800;margin:14px 0">Asset Intelligence Copilot</div><div style="font-size:26px;color:#aab4be">Ask an oil field anything. Get the answer, the evidence and the right chart.</div>
<div style="margin-top:40px;font-size:20px;color:#8994a0">Mangesh Raut · open source (MIT) · powered by open-weight Gemma 4</div></div>"""
ARCH = """<div style="font-size:34px;font-weight:800;margin-bottom:24px">How it works <span style="color:#f5a524">· the model never does arithmetic</span></div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;font-size:18px;line-height:1.45">
<div style="background:#121820;border:1px solid #2a333d;border-radius:12px;padding:18px"><b style="color:#3fa9f5">1 · Data + rules</b><br>Re-runnable loader → SQLite<br>Rules extracted from manuals &amp; SOPs:<br>T200 Δ≥15 °C · T350 Δ≥20 °C<br>≥5 bbl reportable · 24 h notice · 4 h containment<br>Containment hours parsed from repair reports</div>
<div style="background:#121820;border:1px solid #2a333d;border-radius:12px;padding:18px"><b style="color:#3fa9f5">2 · Deterministic tools</b><br>status · downtime · spills · compliance<br>containment · RCA · repair history<br><b>Composable query</b>: metric × scope × window × group-by<br>94 tests · 27/27 examples · 46/46 unseen</div>
<div style="background:#121820;border:1px solid #2a333d;border-radius:12px;padding:18px"><b style="color:#8b5cf6">3 · Gemma 4 (open-weight)</b><br>Planner when rules aren't confident<br>(validated args, one retry)<br>Plain-language summary with number check<br>Multimodal: reads inspection photos<br>Gemini API · OpenRouter · Ollama</div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;font-size:18px;margin-top:18px">
<div style="background:#121820;border:1px solid #2a333d;border-radius:12px;padding:18px"><b style="color:#22c55e">Scoped memory with provenance</b><br>private chats per user · shared well facts · corrections per inspection · rules per well type</div>
<div style="background:#121820;border:1px solid #2a333d;border-radius:12px;padding:18px"><b style="color:#ef4444">Honest about conflicts</b><br>claims checked against the latest inspection · unconfirmed until verified · both sides shown</div></div>"""
OUTRO = """<div style="height:100%;display:flex;flex-direction:column;justify-content:center"><div style="font-size:52px;font-weight:800">Deterministic tools · rules from documents<br>scoped memory · provenance · honesty</div>
<div style="font-size:24px;color:#aab4be;margin-top:24px">One command for the final hour: load → answer → results page in ~2 s</div>
<div style="font-size:22px;color:#f5a524;margin-top:30px">github.com/mangeshraut712/asset-intelligence-copilot</div></div>"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1280, "height": 720}, record_video_dir="/tmp/vid", record_video_size={"width": 1280, "height": 720})
        pg = await ctx.new_page(); await pg.goto(URL); await pg.wait_for_timeout(2500); await pg.evaluate(OVERLAY_JS)
        T0[0] = time.monotonic() - 2.5
        await slide(pg, INTRO)
        await cap(pg, "Hi, I'm Mangesh. Operators lose hours digging through inspections, repair reports and SOPs.", 6)
        await cap(pg, "I built a copilot that answers in seconds, with the evidence and the right visual.", 6)
        await slide(pg, ARCH)
        await cap(pg, "The core idea: the language model never does arithmetic. A loader puts every dataset into SQLite.", 7)
        await cap(pg, "It extracts the rules from the manuals and SOPs, even containment times hidden in free-text repair reports.", 7)
        await cap(pg, "Deterministic, tested tools compute every number, and one composable query covers unseen questions.", 7)
        await cap(pg, "Open-weight Gemma 4 plans when the rules aren't sure, writes summaries, and reads inspection photos.", 7)
        await cap(pg, "Memory is scoped with provenance, and the copilot is honest when people disagree with the data.", 6)
        await slide(pg, "")
        await cap(pg, "This is the app: a clean chat with suggested questions, chat history and a user picker.", 5)
        await pg.click("#nav-brief"); await pg.wait_for_timeout(600)
        await cap(pg, "The field briefing is computed proactively: breaches, open fines, long downtime, stale status.", 6)
        await pg.locator("#cards details").first.click(); await cap(pg, "Every alert cites the record it came from.", 4)
        await pg.locator("#cards details").first.click(); await pg.click("#nav-chat"); await pg.wait_for_timeout(400)
        await cap(pg, "Let's run one question end to end, as Michael Turner, a production supervisor.", 4)
        m = await ask(pg, "Which rules has WELL-0001 broken in the last 12 months, and what is still open?", wait_gemma=20)
        await cap(pg, "Four breaches, all from the 11 June spill: SR-01 reported after 41 hours, SR-03 and RC-04 overdue.", 7)
        await cap(pg, "SR-02: contained after about 7 hours. That fact only exists in the repair report. Let's open it.", 5)
        await m.evaluate("e=>e.querySelectorAll('.cite[hidden]').forEach(x=>x.hidden=false)"); await m.locator(".cite", has_text="MNT-0001-029").first.click(); await pg.wait_for_timeout(1200)
        await cap(pg, "The evidence drawer shows the raw record and highlights the exact sentence in the report.", 7)
        await pg.click("#drawer button")
        await m.locator("details.trace summary").click(); await m.locator("details.trace").scroll_into_view_if_needed()
        await cap(pg, "'How I got this' shows the tool that ran and each rule with the document it came from.", 7)
        g = m.locator(".gem")
        if await g.count(): await g.scroll_into_view_if_needed(); await cap(pg, "Gemma 4 adds a plain-language summary. It's rejected if it invents any number.", 6)
        await ask(pg, "Which 3 wells in Northeast Block 7 had the most downtime in the last 4 months? Show a bar chart.")
        await cap(pg, "A bar chart when you compare wells: WELL-0121 at 49 days, then WELL-0138 and WELL-0107 at 42.", 6)
        await cap(pg, "Now feedback. The AI estimated a spill at 4.5 barrels; the crew measured 5.4.", 4)
        await ask(pg, "The AI estimated the 24 Sep spill at WELL-0151 as 4.5 bbl. The field crew measured 5.4 bbl.")
        await cap(pg, "It keeps the AI's estimate, records who corrected it and why, and re-checks the SOP rules.", 6)
        await cap(pg, "At 5.4 barrels the spill is reportable, no notice was filed, so it flags a possible SR-01 breach.", 6)
        await pg.select_option("#user", "U-401"); await pg.wait_for_timeout(600)
        await cap(pg, "Switch to Laura Simmons, the HSE officer. The correction reaches her too.", 3)
        await ask(pg, "Which spills in Northeast Block 8 in the last 90 days needed a report to the regulator?")
        await cap(pg, "WELL-0151 is now listed because of Michael's correction, and the missing notice is flagged as overdue.", 6)
        await pg.select_option("#user", "U-202"); await pg.wait_for_timeout(600)
        await ask(pg, "For the three wells we discussed yesterday, what have repairs cost this year?")
        await cap(pg, "Private memory: Jessica has no such conversation, so it never borrows Michael's history.", 6)
        await pg.select_option("#user", "U-204"); await pg.wait_for_timeout(600)
        await ask(pg, "WELL-0175 is running fine.")
        await cap(pg, "Tyler says WELL-0175 is running. The latest inspection says otherwise, so it's flagged as a data conflict.", 7)
        await cap(pg, "Both statements stay on record; his is marked unconfirmed and it asks him to confirm.", 5)
        await pg.click("text=Sample photo")
        try: await pg.wait_for_function("[...document.querySelectorAll('.badge')].some(b=>/vision/i.test(b.textContent))", timeout=60000)
        except Exception: pass
        await pg.locator(".turn .a").last.scroll_into_view_if_needed()
        await cap(pg, "Gemma 4 is multimodal: it reads an inspection photo, and its notes stay advisory next to the records.", 7)
        await slide(pg, OUTRO)
        await cap(pg, "For the final hour, one command loads the test data, answers every question and fills in my results page.", 7)
        await cap(pg, "Deterministic tools, rules from documents, scoped memory with provenance, and honesty. Thanks for watching.", 7)
        dur = time.monotonic() - T0[0]
        await ctx.close(); await b.close()
    webm = max(glob.glob("/tmp/vid/*.webm"), key=os.path.getmtime)
    lead = 0.0
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", webm, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "23", "-r", "30", "-movflags", "+faststart", f"{OUT}/demo.mp4"], check=True)
    f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(t * 1000 % 1000):03d}"
    with open(f"{OUT}/demo.srt", "w") as s:
        for i, (a, z, t) in enumerate(CUES, 1): s.write(f"{i}\n{f(a + lead)} --> {f(z + lead)}\n{t}\n\n")
    with open(f"{OUT}/narration.txt", "w") as s:
        s.write("Read these lines in your own voice; start each at its timestamp (mm:ss).\n\n")
        for a, z, t in CUES: s.write(f"[{int(a // 60):02d}:{int(a % 60):02d}–{int(z // 60):02d}:{int(z % 60):02d}] {t}\n")
    json.dump({"duration_s": dur, "cues": CUES}, open(f"{OUT}/timeline.json", "w"), indent=1)
    print("recorded", round(dur, 1), "s")

asyncio.run(main())
