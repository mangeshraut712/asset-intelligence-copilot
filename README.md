# Asset Intelligence Copilot

FlytBase challenge · AI Hackers Collective × Hacktoberfest 2026 Hack Day · **open source (MIT) · powered by open-weight Gemma 4**

A chat copilot for oil-field operators. It answers plain-English questions about wells with **numbers computed by deterministic tools, citations to record IDs and SOP passages, and a generated visual** (status card, table, line chart, bar chart, map, heatmap). It remembers shared facts about wells, keeps each user's conversations private, learns from corrections at the right scope (one inspection, or every well of a type) with provenance, and says so when people disagree with the data or with each other.

| Check | Result |
|---|---|
| 18 example scenarios (27 checks) | **27/27** (`results/examples_rules.md`) |
| 46 unseen questions, expected answers computed independently from raw files (`eval/gen_unseen.py`) | **46/46** (`results/unseen_rules.md`) |
| pytest | **135 passed** (101 at submission, 121 on the previous tip of this branch, 14 new pipeline edge tests) |
| Final questions (organizers' test data) | submitted: 16 correct, 2 mostly correct, 3 judgement calls; **post-submission branch: 21/21** by hand check (see `docs/results.md`) |
| Final-hour command on a synthetic 400-well set (sample + test data) | **~2 s** end to end, 7/7 checks |

**Demo video (4:41, narrated in my own voice):** https://drive.google.com/file/d/1OdlK_6-9StQk0gc5ztwZs5MSVCvVVWHz/view (mirror: https://vimeo.com/1236779581)

**Report (PDF):** https://drive.google.com/file/d/1V4ps3w4if5FurkkwLpUvRyxdnbfuCW2f/view · in repo: [docs/report.pdf](docs/report.pdf) ([markdown](docs/report.md))

Docs: [system design (page 1)](docs/writeup.md) · [results (page 2)](docs/results.md) · [video script](docs/video/script.md) · [contributing](CONTRIBUTING.md)

Runs locally (no hosted deployment). Open source under the [MIT License](LICENSE).

## Gemma 4 (open-weight) in the LLM layer
* **Default model:** Gemma 4 31B (`gemma-4-31b-it`), with Gemma 4 26B as fallback. Provider order: **Gemini API** (`GEMINI_API_KEY`), then OpenRouter (`OPENROUTER_API_KEY`, `google/gemma-4-31b-it:free`), then local Ollama (`AIC_LLM_BASE=http://localhost:11434/v1`, `gemma4:*`).
* **Planner:** when the rule router isn't confident, Gemma 4 fills a structured query (metric × scope × window × group-by) through function calling, with a JSON fallback for endpoints without tools. Arguments are validated; an empty or invalid result triggers one retry via the rule router. The rule router stays authoritative when it's confident.
* **Answer phrasing:** Gemma 4 writes a short plain-language summary under each answer. It's rejected automatically if it contains any number not present in the tool output.
* **Multimodal:** upload an inspection photo (📷) and Gemma 4 describes the equipment, any staining and the % of pad, alongside the well's records. This is advisory only and never overrides data. A sample photo is included.
* Numbers never come from the model. Every LLM failure falls back to the deterministic router, and planner picks are cached, so rate limits can't block a run.

## Interface
A product-style chat UI in one HTML file, no build step. The layout follows shadcn (muted sidebar, hairline borders, focus rings, tabular numerals) and Apple HIG spacing (system font, 34 px empty-state title, translucent top bar and composer, light and dark themes). A collapsible sidebar holds new chat, per-user chat history, the field briefing, memory, and the user picker. The conversation column is 760 px, with a sticky auto-growing composer and photo attach.
* Every visual sits in a consistent card with Chart/Table switch, copy-as-CSV and expand. Citations are pills that open the evidence sheet (a right sheet on desktop, a bottom sheet on mobile).
* Each answer has a collapsible "How I got this" trace and follow-up chips.
* Light and dark themes follow the system setting. Keyboard: Enter / Shift+Enter / Esc.
* Checked with Playwright at 1440×900, 1280×800, 768×1024 and 390×844: no console errors, no horizontal overflow, CLS < 0.02.

| Desktop (light) | Desktop (dark) |
|---|---|
| ![](docs/screenshots/desktop-light.png) | ![](docs/screenshots/desktop-dark.png) |
| **Evidence drawer** | **Mobile (390×844)** |
| ![](docs/screenshots/evidence-drawer.png) | <img src="docs/screenshots/mobile.png" width="260"> |

## Architecture

Every number is computed in Python. Gemma 4 may plan a tool call, phrase a summary, or describe a photo, and each of those steps is checked. A bad model reply cannot change a barrel count, a threshold, or a stored correction.

### Modules

| Module | Responsibility |
|---|---|
| `copilot/loader.py` | Rebuilds the raw tables from one or more dataset folders. Parses SOP and manual thresholds into `rules`. Pulls containment hours out of free-text repair reports. Leaves the `memory_*` tables in place across reloads. |
| `copilot/tools.py` | Deterministic calculations: effective inspections (raw readings + correction notes + runtime corrections, originals kept), status, downtime, spills, compliance, containment, root-cause analysis, costs. |
| `copilot/query.py` | Composable query: metric × scope × window × group-by. `validate()` rejects a plan with the wrong shape. `run_query()` runs only after that. |
| `copilot/final_tools.py` | Handlers for organizer questions that do not fit one metric: recall lots, gas-odor response, bypass and MOC, the regulator letter, status conflicts, freeze checks, delays, regional temperature, and the judgement rankings. |
| `copilot/agent.py` | `Copilot.ask()` normalizes the question, routes it, runs tools, and attaches citations, a visual, confidence, a trace, follow-ups, and assumption lines. |
| `copilot/gemma.py` | Optional phrasing and photo description. A summary is dropped when it contains a number that is not in the tool answer or the question. |
| `copilot/insights.py` | Field briefing cards, and the evidence sheet (the raw record plus the highlighted SOP or report passage). |
| `copilot/server.py` | FastAPI: `/api/ask`, memory, briefing, evidence, vision. Serves `web/index.html`. There is no build step. |

### Request path

```
dataset folder(s)
    → copilot/loader.py → SQLite (data/copilot.db)
        raw: wells, equipment, inspections, maintenance (report text + parsed containment hours),
             reg_events, notes, documents, rules
        memory_*: conversations, well facts, corrections, type rules (kept across reloads)
    → Copilot.ask
        1. Normalize: strip invisible characters, collapse whitespace, cap the length.
           A blank or punctuation-only question is refused and is not stored.
        2. final_tools.dispatch for the organizer-shaped questions.
        3. Drop well ids that are not in the loaded dataset. If every named well is missing,
           say so and write nothing. A mix keeps the known wells and names the ones left out.
        4. Feedback, before any data tool: one-inspection correction, type-wide rule, or shared well fact.
           "31 February" is refused, so it is not applied to the latest inspection.
           Sending the same correction or the same type rule again does not insert a second row.
           A bare well id ("WELL-0001", "status of WELL-0001") is a lookup, not a new fact.
        5. Private memory recall ("the wells we discussed yesterday") from this user's other chats only.
        6. Confident rule router. When it is not confident and AIC_LLM is not "0", Gemma 4 fills
           metric × scope × window × group-by. validate() checks the plan. An invalid or empty
           result is retried once through the rule router. A confident rule match stays authoritative.
        7. Answer, citations, and a visual. A visual the user named wins when the series is rectangular.
           A ragged series is left as the tool drew it.
    → JSON: text, visual, citations, wells, user, engine, confidence, trace, followups, assumptions
    → web/index.html (Chart.js, Leaflet, user picker)
```

### Domain rules

These values are parsed from the manuals and SOPs into the `rules` table. They are not hard-coded in the handlers.

* **Producing oil** = wellhead − ambient ≥ the per-type threshold (T200: 15 °C, T350: 20 °C).
* **Downtime** = 7 days per non-producing weekly inspection in the period. Missed inspections add nothing. Causes come from overlapping or triggered repairs and from dated notes.
* **Corrections** (`note_type=correction`, plus runtime `memory_corrections`) void or replace the named inspection field. The original value stays on the row.
* **Spill rules** from the Spill Response SOP: reportable ≥ 5 bbl, written notice ≤ 24 h (2 h for a major spill), containment ≤ 4 h, agency verification ≤ 60 days. RC-04 notice-of-violation response ≤ 30 days. Containment times are parsed from repair reports ("contained about/after/within N hours", or minutes). Each SR-02 line in an answer names the spill it belongs to.
* **Periods.** "Today" is `AIC_TODAY` (default 2026-10-17). "Last N months/days" ends yesterday. A repair belongs to a period by its start date. "Between A and B" uses the earlier date as the start. A dated between/since that is not a real calendar range does not fall through and become the whole year.

### Edge cases the pipeline absorbs

| Input | What happens |
|---|---|
| Blank, whitespace, or no letters or digits | A short prompt, confidence `low`, nothing written to memory |
| Well id with no claim (`WELL-0001`, `status of WELL-0001`) | Status lookup. No shared fact is stored |
| Well id not in the loaded dataset | Named in the answer. No fact and no correction. Mixed ids keep the known wells |
| Well row with zero inspections | "No inspections on record" for status, temperature, and corrections |
| Impossible date on a correction, a fact, or a spill dispute | No write. The reply quotes the bad date |
| The same correction value, or the same type-wide RCA threshold, sent again | Acknowledged. The table is not duplicated |
| Window whose start is after its end | Swapped to a real range inside `run_query` |
| Empty id list (`IN ()`) or a scope that matches zero wells | An empty result, not a SQL error |
| Planner metric, group, well id, or window of the wrong type | `validate()` lists the problems and the router retries |
| "Top N" or a temperature window with a huge N | Capped (50 groups, 520 weeks) |
| A month shift that would land outside year 1..9999 | Clamped, so "last 100000 months" does not raise |
| Summary that invents a number | Gemma phrasing is rejected. The tool answer stands |
| Any other model or network failure | The rule-router answer is used, so a rate limit cannot block a run |

Answer lines that begin with "Assumption:" are also returned on `assumptions[]` and listed in the "How I got this" trace. Memory scopes (private chats, shared facts, per-inspection corrections, per-type rules) are in [Memory and corrections](#memory-and-corrections).

## Composable query, planner and self-check
`copilot/query.py` turns any question into **metric × scope × window × group-by** (metrics: downtime, spills, spill_volume, repairs, repair_cost, fines, reg_events, not_producing, stale_status, notes; scope: well/area/type/team/field; windows: right now, last N days/weeks/months, season, month, quarter, half, between dates, a year; groups: well/area/type/team/month/equipment). The LLM planner (used only when the rule router isn't confident) fills the same structure; args are validated and an empty or invalid result triggers one retry through the rule router.

## Demo features
Field briefing panel (`/api/briefing`), evidence drawer (`/api/evidence?ref=MNT-0001-029` → raw record + highlighted report/SOP passage), "How I got this" trace (tools, args, rules with source docs), confidence/conflict badge, follow-up chips, step progress, dark/light theme.

## Memory and corrections

| Level | Table | Scope | Example |
|---|---|---|---|
| Private conversation memory | `memory_conversations` (user, chat, ts, question, answer, wells) | one user | "the three wells we discussed yesterday" resolves only from *this* user's earlier chats; another user gets "no earlier conversation". |
| Shared well knowledge | `memory_well_facts` (well, author, text, kind, status, conflict) | all users | "WELL-0007 will be shut in from 17 Oct…" is shown to anyone asking about WELL-0007, attributed to the author. |
| Raw-data / AI-analysis corrections | `memory_corrections` (inspection, field, original, corrected, author, reason, conflict) | one inspection, all users | Overlaid on every query via `effective_inspections`; the original stays visible with who/why. |
| Type-wide rules | `memory_type_rules` (well_type, rule_key, value, author) | every well of that type only | "Note for all T350 wells: RCA after 2 repairs" changes T350 only; answers say it follows the user's rule, not the manual. |

**Conflicts**: a statement about a well is compared with its latest inspection; if it contradicts the data it is stored as *unconfirmed*, the copilot says which inspection disagrees, which other user's note agrees, and asks for confirmation. A correction that contradicts an inspector note (e.g. "Pump jack not moving.") is applied but flagged. Disagreeing notes on the same inspection are shown side by side; only a formal correction overrides a detection.

## Run

```bash
git clone https://github.com/FlytBaseAILabs/flytbase-ahc-swe-asset-intelligence-dataset ../dataset
pip install -r requirements.txt
cp .env.example .env   # optional: add OPENROUTER_API_KEY, then `set -a; . ./.env; set +a`
python -m copilot.loader ../dataset/sample-data           # builds data/copilot.db
python3 -m uvicorn copilot.server:app --port 8000         # open http://localhost:8000
python -m pytest -q tests                                  # 135 tests
python -m eval.run_questions eval/examples.json --fresh    # 18 examples (27 checks) → results/examples.{md,json} + score
python -m eval.run_questions eval/unseen.json --fresh      # 46 unseen questions
```

LLM (Gemma 4 by default; numbers always come from the tools): set `GEMINI_API_KEY` (Gemma 4 via the Gemini API) or `OPENROUTER_API_KEY`, or point `AIC_LLM_BASE` at Ollama. Optional: `AIC_LLM_MODEL`, `AIC_LLM_PROVIDER`, `AIC_LLM_FALLBACKS`. Routing policy (`AIC_LLM`): `auto` (default) means the rule router is authoritative when it matches confidently and the LLM is only asked when it is unsure; `force` sends every question through the LLM; `0` means rules only. LLM picks are cached in `data/llm_cache.json`, a free-model fallback chain is tried (`AIC_LLM_FALLBACKS`), the timeout is `AIC_LLM_TIMEOUT` (20 s), and any error falls back to the rule router, so rate limits cannot block a run.

## Tests

```bash
pip install -r requirements-dev.txt
AIC_DATA=/path/to/sample-data python -m pytest -q tests   # 135 tests: tools, raw-data recomputation, memory scopes, corrections, 18 examples, 46 unseen, SR-02 regression, Gemma 4 guard, API, pipeline edge cases
```
`tests/test_raw_recompute.py` recomputes key expected answers straight from the raw JSON (no copilot code), so the example checker is not just matching strings. Tests use a temporary DB and never touch the running server's memory.

## Docker (optional, local)
`docker build -t aic . && docker run -p 8000:8000 -e GEMINI_API_KEY=... aic`. The image bakes in the public sample dataset; to add the test set, mount it and set `DATA_DIRS="/data/sample-data /data/extra"`. The container listens on `$PORT` (default 8000). There is no hosted deployment.

## Final hour (one command)
```bash
# exact command used for the submitted results (organizers' dataset repo, commit 009e2b5, cloned next to this repo as ../dataset):
AIC_TODAY=2027-01-15 python scripts/final_run.py --data ../dataset/test-data/dataset --only-test --questions eval/final_questions.json
# general form: --data <test-data> --questions final.txt; --today YYYY-MM-DD; --no-llm for rules only
```
Reproduces `results/final.md` and `results/final.json` byte-for-byte in about 2.5 s. Note: it also regenerates `docs/results.md` from the template; the submitted page 2 adds hand-checked per-turn verdicts, so restore it with `git checkout docs/results.md` afterwards. Final result: 16 of 21 turns correct, 2 mostly correct, 3 judgement calls (see `docs/results.md`).
It loads sample + test data (memory reset), answers every question (`.txt` lines may start with `User Name:`) and writes `results/final.md`, `results/final.json` and `docs/results.md`, filled from `docs/results_template.md` (summary, answer table, what worked, what didn't). A rehearsal output is in `docs/rehearsal-synthetic.md`. Rehearsed on the synthetic 400-well set (`synth/test-data`, built by `scripts/make_synthetic_dataset.py`): **1.8 s end to end**.

## Loading the test dataset

The loader is idempotent and accepts several folders (same layout as `sample-data/`):

```bash
python -m copilot.loader /path/to/sample-data /path/to/test-data   # or just the test folder
AIC_TODAY=2026-10-17 python3 -m uvicorn copilot.server:app --port 8000   # set "today" if the test data says otherwise
# final questions: one per line in a .txt, or a JSON list of {id, q, user, chat, day}
python -m eval.run_questions final.txt --out results/final
```
To dry-run this step: `python scripts/make_synthetic_dataset.py <sample-data> /tmp/test-data` builds a 200-well copy (renumbered wells, new areas). `eval/synthetic.json` checks answers on sample + synthetic loaded together (7/7, 400 wells load in about 1 s).
`--reset-memory` on the loader wipes runtime memory; otherwise it is preserved across reloads.

## Models and cost
Deterministic core: no model, $0. Optional LLM routing uses one small tool-call per question (free Gemma 4 on OpenRouter/AI Studio by default).

## Demo video
**https://vimeo.com/1236779581** (4:41), narrated in my own voice over the real UI. The timed script is in `docs/video/script.md` and the narration in `docs/video/narration.txt`. `python scripts/record_demo.py <out-dir>` re-records the screen capture by driving the UI with Playwright (1280×720) against `http://localhost:8000` (override with `AIC_URL`).

## Next steps
Embedding retrieval over reports, LLM-written prose on top of tool JSON, richer statement parsing for arbitrary feedback, per-chat context for follow-ups.

## Future scope
What is still open after the post-submission work (details in `docs/results.md`):
- **Validated failure model.** The "most likely to need a repair in 90 days" ranking (Q7) and "which well first" (Q9.6) use documented precursors (T500 early-warning fall, repeated drive trips, "unit running, wellhead cold") with hand-set points. With a longer note history, the points should be fitted and back-tested against later repairs.
- **Phrasing coverage.** Gas-odor, shut-in/restart, bypass and abnormal-sound notes are matched with patterns that cover this dataset's wording. New wording should fall back to the Gemma 4 planner or an embedding classifier, with the pattern match kept as the audit trail.
- **Ambiguity as a first-class output.** Some answers already state an assumption and give the other reading (drive trips under OPS-3, "today", repair since the first or the latest note). This should become a structured `assumptions` field in the API and UI, not just prose.
- **Statistics.** Q10 uses a chi-square test and permutation tests without a multiple-comparison correction. Trends over time per area and contractor would make "stands out" more useful.
- **Recall and swap reconciliation.** User-reported pump swaps are stored as shared facts. When the work order lands, the system should close them out automatically and flag mismatches.
- **Per-chat context** for follow-ups beyond the patterns handled now ("back to the pumps…", "wells we've talked about").

## Contributing and license
See [CONTRIBUTING.md](CONTRIBUTING.md); issue and PR templates are in `.github/`. Released under the [MIT License](LICENSE) © 2026 Mangesh Raut.

**CI:** the workflow is in `docs/ci-workflow.yml`. Copy it to `.github/workflows/ci.yml`; pushing it needs a token with the `workflow` scope.
