# Asset Intelligence Copilot by Mangesh
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · MIT*

**Repo:** https://github.com/mangeshraut712/asset-intelligence-copilot · **Video (4:41):** https://vimeo.com/1236779581

> The formatted version of this report is `docs/report.pdf` (page 1: system design; pages 2–3: results).

## System design
**Principle: the model never does arithmetic.** Every number comes from a deterministic, unit-tested tool over SQLite; every threshold and deadline is extracted from the manuals and SOPs; every answer cites record IDs and document passages. Gemma 4 plans tool calls, phrases answers and reads photos, and is checked at each step.

Flow: Datasets → Loader + rules (SQLite, prose facts, rules table) → Deterministic tools (`effective_inspections`, compliance, composable query, `copilot/final_tools.py`) → Agent (feedback → memory → rule router → Gemma 4 planner, number guard) → Answer (citations, visual, confidence, trace).

Memory has scope and provenance (conversations per user; well facts, corrections and type rules shared, attributed and marked confirmed/unconfirmed). 101 pytest tests; examples 27/27; unseen 46/46. Model cost $0. Runs locally.

## Results on the 11 final questions
Organizers' test dataset (600 wells, commit 009e2b5), today = 15 Jan 2027. **16/21 correct · 2 mostly correct · 3 judgement calls · 101 tests · ≈2.5 s full run (was 185 s).**


| Turn | Question | Answer (short) | Verdict |
|---|---|---|---|
| Q1 | Reservoir pressure map | Declines: no pressure field in inspections, maintenance or notes (only flowline test pressures in repair reports). | Correct |
| Q2 | Top oil producer 2026 | Declines: no production volumes, only producing / not producing from thermal readings. | Correct |
| Q3 | Gas reports since 1 Nov | 26 reports: 17 met, 9 missed (24 h, 12 h from 1 Jan 2027). WELL-0332 missed (drone only). | Correct |
| Q4 | Flowline bypasses | WELL-0248 allowed (MOC-031 ext. by MOC-044 to 28 Feb 2027); WELL-0249 expired; WELL-0405 not approved. Past: 0087, 0158 expired; 0561 not approved. | Correct |
| Q5 | Regulator spill letter | 6 reportable spills in NE Block 7/8 since 1 Jun 2026; 3 not compliant (WELL-0123, 0182, 0262: no soil samples). | Correct |
| Q6 | Inspection vs note conflicts | 15 wells, applying OPS-3. Caveat: underload-restart notes (WELL-0219, 0249) counted as restarts. | Mostly correct |
| Q7.1 | Wells that sound wrong | Last-month abnormal notes, no repair since, ranked by a transparent (unvalidated) score. | Judgement call |
| Q7.2 | Top 3 crews this week | WELL-0182, WELL-0411, WELL-0297. | Judgement call |
| Q8.1 | WELL-0333 pump swapped | First-hand: counted as replaced, attributed to Nathan, no work order. | Correct |
| Q8.2 | Private sort preference | Saved as Nathan's private preference only. | Correct |
| Q8.3 | Recalled pumps in ground | 8 pumps. All 18 recalled-lot installs checked: 9 replaced by other lots, WELL-0333 excluded. | Correct |
| Q8.4 | Remove WELL-0577 | Not removed: second-hand claim, no work order, flagged unconfirmed. | Correct |
| Q8.5 | My area + install cost | NW Block 12: WELL-0305, 0426, 0428; sorted by area then ID, costs in $K. | Correct |
| Q9.1 | Recalled pumps by area | 8: NE8 2, NW12 3, SE32 1, SW23 2. WELL-0577 listed as unconfirmed. | Correct |
| Q9.2 | Northwest Production lead | Nathan Pierce; team runs 150 wells. | Correct |
| Q9.3 | OPS-5 cold-weather check | OPS-5 quoted. Example: WELL-0310 (INS-0310-0213, 17 Dec, −6 °C, no heat-trace check in 7 days). | Correct |
| Q9.4 | H2S reading | No H2S reading recorded; only drone follow-ups, OPS-1 missed. Says so, no invented number. | Correct |
| Q9.5 | Producing status of the 8 | WELL-0263 and WELL-0160 not producing; last repair shown for each. | Correct |
| Q9.6 | Most urgent well | WELL-0332: missed gas response (safety first), not producing. | Judgement call |
| Q10 | Delay causes 2026 | 500 delayed jobs: weather 28%, contractors 26%, parts 23%, crews 22%; median 9 extra days. No area >20 pts off field mix. | Mostly correct |
| Q11 | Hottest wellheads | Southeast Block 31 in 13 of 13 months; air temp spread ≤ 0.7 °C; holds within each well type. | Correct |

## Limits and next steps
- Q7 ranking and Q9.6 use a hand-designed score; reasoning shown, not validated.
- Gas and abnormal-sound keyword patterns cover this dataset's phrasings only.
- Q10's "stands out" uses a fixed 20-point rule.
- Next: embedding retrieval, multi-turn follow-ups, Gemma 4 spill-area estimation from drone imagery.

Full answers: `results/final.md`, `results/final.json`.
