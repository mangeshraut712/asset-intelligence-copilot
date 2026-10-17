# Asset Intelligence Copilot: System Design
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · MIT · github.com/mangeshraut712/asset-intelligence-copilot*

**Repo:** https://github.com/mangeshraut712/asset-intelligence-copilot · **Video:** https://vimeo.com/1236779581

**Principle: the model never does arithmetic.** Every number comes from a deterministic, unit-tested tool over SQLite. Every threshold and deadline is extracted from the manuals and SOPs. Every answer cites record IDs and document passages. The open-weight **Gemma 4** model plans tool calls, phrases answers and reads photos, and is checked at each step.

**Storage and indexing.** A re-runnable loader ingests any number of dataset folders: wells, equipment, inspections (indexed by well and date), maintenance, regulator events, notes and documents. It follows each `report_file` and extracts facts that exist only in prose (*"contained about 7 hours after the inspection flight"*, also "after/within", minutes). It also builds a `rules` table from the documents: producing at Δ ≥ 15 °C (T200) and 20 °C (T350); reportable at ≥ 5 bbl; notice within 24 h; containment within 4 h; verification within 60 d; NOV response within 30 d; RCA at 3 repairs. New wells, areas or manuals need no code change; 400 wells load in about 1 s.

**Tools.** `effective_inspections` is the single source of truth: raw readings + correction notes + runtime corrections, with the originals kept. Specialised tools cover status, temperature series, spills, downtime (7 days per non-producing inspection, causes from overlapping repairs and notes), compliance (SR-01/02/03, RC-02, RC-04, RCA), containment, reportable spills and repair history. A **composable query** covers the long tail: metric (downtime, spills, volume, repairs, cost, fines, regulator events, not producing, stale status, notes) × scope (well, area, type, team, field) × window (right now, last N, season, month, quarter, half, between dates) × group-by (well, area, type, team, month, equipment).

**Agent (Gemma 4 by default).** 1) Feedback detection (correction, type-wide rule or well statement). 2) Private-memory recall. 3) A confident rule router. 4) Otherwise **Gemma 4 as planner** fills the structured query (function calling, with a JSON fallback). Its arguments are **validated**; an invalid or empty result triggers **one retry** through the rule router, and the rule router stays authoritative whenever it is confident. Gemma 4 runs via the **Gemini API** (`GEMINI_API_KEY`) or OpenRouter, or locally via Ollama. Gemma 4 also writes a plain-language summary, accepted only if it introduces **no number absent from the tool output**. **Multimodal:** Gemma 4 describes an uploaded inspection photo (equipment, staining, % of pad), shown as advisory next to the records and never overriding them. Picks are cached, and any LLM failure falls back to rules, so a rate limit can't block a run. The visual is the one the user asked for, or else the best fit (card, table, line, bar, map or heatmap).

**Memory with scope and provenance.**
| Level | Scope | Behaviour |
|---|---|---|
| Conversations | one user | "the wells we discussed yesterday" resolves only from that user's own chats |
| Well facts | all users | attributed, timestamped, *confirmed / unconfirmed / planned* |
| Corrections | one inspection field, all users | original + new value, author, reason; rules re-evaluated (4.5 → 5.4 bbl ⇒ SR-01/SR-03) |
| Type rules | every well of one type only | "T350: RCA after 2" changes T350 only; the answer cites the user, not the manual |

**Honesty about conflicts.** Claims are checked against the latest inspection. A contradiction is stored as *unconfirmed*, and the answer names the inspection that disagrees and the user who agrees, then asks for confirmation. A correction that clashes with an inspector note is flagged, and disagreeing notes are shown side by side. Only formal corrections override detections.

**Demo layer.** Proactive field briefing (SOP breaches, unreported spills, open fines, RC-03 downtime, stale status). A clickable evidence drawer with highlighted report and SOP passages. A **"How I got this"** trace (tools, arguments, rules with their source documents). Confidence and conflict badges, follow-up chips, and dark and light themes.

**Quality, cost, next.** 101 pytest tests, including an SR-02 regression test, a Gemma 4 number-guard test, the 18 examples (27/27) and 46 unseen questions whose answers were computed independently from the raw files (46/46). The final-hour command loads, answers and fills the results page in about 2 s. Model cost: $0 (free Gemma 4). Demo video (4:41, my own voice): https://vimeo.com/1236779581. Runs locally; no hosted deployment. Next: embedding retrieval over reports, multi-turn follow-ups, and Gemma 4 spill-area estimation from real drone imagery.


<div style="page-break-before:always"></div>

# Asset Intelligence Copilot: Results on the Final Questions
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · pages 2–3*

Test data: organizers' test dataset (600 wells, commit 009e2b5), today = 15 Jan 2027. Command:
`AIC_TODAY=2027-01-15 python scripts/final_run.py --data <test-data>/dataset --only-test --questions eval/final_questions.json`.
**All 21 turns answered in about 2.5 s end to end** (was 185 s). Every turn is now answered by a deterministic tool, so Gemma 4 isn't called on this set.

## What changed since the first run
My first run on the final questions got nearly every turn wrong, because the router only knew the sample question types (see git history for that page). I then added `copilot/final_tools.py`: deterministic tools that read their rules from the documents (recall lots and the due date from the recall notice; letter scope, threshold and the "Soil samples sent to the lab." test from the regulator letter; MOC well lists, expiry dates and extensions from the MOC memos; OPS-1/2/3/5 from the Operations SOP). I also added router rules for these question types, private per-user preferences, and pump-swap claims that record whether a claim is first-hand or relayed. No answers are hard-coded.

## Per-turn verdicts (checked by hand against the raw files)
| Turn | Before | After | Notes on the hand check |
|---|---|---|---|
| Q1 | Wrong (spill heatmap) | **Correct**: declines, explains | No pressure field exists in inspections, maintenance or notes. The only pressures are flowline test pressures in repair reports. |
| Q2 | Wrong (no tool) | **Correct**: declines, explains | No production volumes in the data, only producing/not producing from thermal readings. |
| Q3 | Wrong | **Correct** | 26 gas reports since 1 Nov 2026: 17 met, 9 missed (24 h, or 12 h from 1 Jan 2027; repair or manual inspection only). WELL-0332 checked by hand: only drone inspections followed, so missed. |
| Q4 | Wrong (no tool) | **Correct** | Now: WELL-0248 allowed (MOC-031 extended by MOC-044 to 28 Feb 2027), WELL-0249 expired (MOC-036 ended 15 Dec), WELL-0405 not approved. Past violations: WELL-0087 and WELL-0158 expired; WELL-0561 not approved. |
| Q5 | Wrong (all Nov spills) | **Correct** | 6 reportable spills in NE Block 7/8 since 1 Jun 2026; 3 not compliant (WELL-0123, WELL-0182, WELL-0262: no "Soil samples sent to the lab."). |
| Q6 | Wrong | **Mostly correct** | 15 wells, applying OPS-3. Caveat: "drive tripping on underload, restarted from the panel" notes (WELL-0219, WELL-0249) count as restart notes; the inspection is newer there anyway. |
| Q7.1 | Wrong (counted repairs) | **Plausible, judgement** | Abnormal-sound notes from the last month on wells with no repair since, ranked by a transparent score (repeat notes, non-producing readings, repair frequency, recalled pump). The score isn't a validated failure model. |
| Q7.2 | Wrong | **Plausible, judgement** | Top 3 of that ranking: WELL-0182, WELL-0411, WELL-0297. |
| Q8.1 | Partly (recorded, no recall logic) | **Correct** | First-hand report, so WELL-0333 is counted as replaced, attributed to Nathan, with no work order. |
| Q8.2 | Wrong (cost query) | **Correct** | Saved as Nathan's private preference only. |
| Q8.3 | Wrong (no tool) | **Correct** | 8 recalled pumps in the ground. All 18 recalled-lot installs were checked by hand: 9 were replaced later by other lots, and WELL-0333 is excluded per Nathan. |
| Q8.4 | Wrong ("confirmed by data") | **Correct** | Not removed: a second-hand claim (Nathan → Olivia) with no work order, flagged **unconfirmed**. |
| Q8.5 | Wrong | **Correct** | NW Block 12: WELL-0305, WELL-0426, WELL-0428, sorted by area then ID, costs in $K (install job cost). |
| Q9.1 | Wrong | **Correct** | 8 pumps: NE8 2, NW12 3, SE32 1, SW23 2. WELL-0577 is still listed as unconfirmed. |
| Q9.2 | Wrong | **Correct** | Nathan Pierce leads Northwest Production, which runs 150 wells. |
| Q9.3 | Partly (SOP only) | **Correct** | OPS-5 quoted. Example: WELL-0310 (INS-0310-0213, 17 Dec, −6 °C, producing, no heat trace check within 7 days). |
| Q9.4 | Wrong (status card) | **Correct/partial** | No H2S reading is recorded for that report; the only follow-ups were drone inspections, and OPS-1 was missed. It says so instead of inventing a number. |
| Q9.5 | Wrong | **Correct** | Of the 8 wells, WELL-0263 and WELL-0160 aren't producing; the last repair is shown for each. |
| Q9.6 | Wrong | **Plausible, judgement** | WELL-0332: missed gas response (safety first), not producing. |
| Q10 | Wrong (counted jobs) | **Mostly correct** | 500 delayed jobs in 2026 parsed from "about N days longer than the repair itself because …": weather 28%, contractors 26%, parts 23%, crews 22%; median 9 extra days. No area differs from the field mix by more than 20 points. The "stands out" judgement is weak. |
| Q11 | Wrong (no tool) | **Correct** | Southeast Block 31 has the hottest producing wellheads in 13 of 13 months. Air temperature is the same across areas (spread ≤ 0.7 °C), and the gap holds within each well type. |

**Summary:** before, 0 of 21 turns were fully correct (2 partly). After: 16 correct, 2 mostly correct (Q6, Q10), and 3 judgement calls with evidence (Q7.1, Q7.2, Q9.6).

## Still weak
- Q7 ranking and Q9.6 use a hand-designed score; the reasoning is shown, but it isn't validated.
- The keyword patterns for gas and abnormal-sound notes cover the phrasings in this dataset; a new phrasing would need the pattern extended or the Gemma planner.
- Q10's "stands out" uses a fixed 20-point rule.

## Tests
- `pytest`: 101 passed.
- Example checks: 27/27. Unseen-question checks: 46/46 (`results/examples_rules.md`, `results/unseen_rules.md`).


Full answers, citations and visual data: `results/final.md`, `results/final.json`. Repo: https://github.com/mangeshraut712/asset-intelligence-copilot · Video: https://vimeo.com/1236779581
