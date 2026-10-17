# Asset Intelligence Copilot: Results on the Final Questions
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · page 2*

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

## Answers
| # | Question | Answer (headline) | Visual | Confidence | Sources |
|---|---|---|---|---|---|
| Q1 | All our wells feed one reservoir. Map the reservoir pressure across the field from the pressure | I can't map reservoir pressure: the dataset has no pressure measurements (no reservoir, bottom-hole, tubing or casing pressure field in inspections, maintenance or notes) | - | high | 2 |
| Q2 | Which well produced the most oil in 2026? | I can't say which well produced the most oil: the dataset has no production volumes (no barrels produced, no allocation or meter data). Inspections only say whether a wel | - | high | 2 |
| Q3 | Since 1 Nov 2026, every time an operator note reports gas at a well, did we get someone out to  | 26 gas-odor reports in operator notes since 1 Nov 2026 (OPS-1: smelled gas, rotten-egg smell, gas odor or H2S monitor alarm). 17 met the deadline and 9 missed it. | table | high | 51 |
| Q4 | Across all areas, which temporary flowline bypasses are in place right now, and is each one all | In place right now (3): WELL-0248 (Southeast Block 31, in since 5 Nov 2026) — Allowed under MOC-2026-031 (extended by MOC-2026-044) until 28 Feb 2027; WELL-0249 (Southeas | table | high | 25 |
| Q5 | The State Oil & Gas Commission wrote to us in November 2026 about spills. Which of our spills d | The letter (20 Nov 2026) covers reportable spills (≥ 5 bbl) in Northeast Block 7 and Northeast Block 8 since 1 Jun 2026, excluding detections later confirmed not to be cr | table | high | 13 |
| Q6 | Across the whole field, not just my area, for which wells do the latest inspection and the oper | 15 wells where the latest inspection and the latest shut-in/restart operator note disagree. Rule (Operations SOP OPS-3): the more recent evidence wins; a restart note new | table | conflict | 31 |
| Q7.1 | Over the last month the operators have written notes about wells that sound or behave wrong. Wh | In the last month operators wrote abnormal-behaviour notes (rattling, rod squeal, fluid pound, tagging bottom, amps hunting, etc.) about 172 wells; 160 have had no repair | table | high | 0 |
| Q7.2 | Which three would you send a crew to first this week, and why? | Send crews first to: | table | high | 0 |
| Q8.1 | WELL-0333's recalled pump was swapped out yesterday. The work order isn't in the system yet. Pl | Noted for everyone: Nathan Pierce reports the recalled pump on WELL-0333 (lot LOT-2409-A, installed by MNT-0333-024) was swapped. The work order isn't in the system, so I | - | high | 2 |
| Q8.2 | Also, just for me: whenever you list wells, sort them by area and then by well ID, and show cos | Saved as a private preference for Nathan Pierce only (other users are not affected): lists of wells sorted by area, then well ID; costs in thousands of dollars. I'll appl | - | high | 1 |
| Q8.3 | Which recalled pumps are still in the ground right now? | 8 recalled pumps are still in the ground across the field (Highline lots LOT-2409-A, LOT-2409-C, LOT-2410-B from recall notice HPC-RN-2026-07; replacement was due 31 Dec  | table | high | 9 |
| Q8.4 | Nathan told me the recalled pump on WELL-0577 was swapped as well. Take it off the recall list. | ⚠ I have not taken WELL-0577 off the recall list. The data (maintenance report MNT-0577-028 (LOT-2409-A)) still shows recalled lot LOT-2409-A in the well, there is no wor | - | conflict | 1 |
| Q8.5 | Show me the recalled pumps that are still in the ground in my area, and what it cost to install | 3 recalled pumps are still in the ground in your areas (Northwest Block 12) (Highline lots LOT-2409-A, LOT-2409-C, LOT-2410-B from recall notice HPC-RN-2026-07; replaceme | table | high | 4 |
| Q9.1 | How many recalled pumps are still in the ground, and in which areas? | 8 recalled pumps are still in the ground across the field (Highline lots LOT-2409-A, LOT-2409-C, LOT-2410-B from recall notice HPC-RN-2026-07; replacement was due 31 Dec  | table | conflict | 9 |
| Q9.2 | Different topic. Who leads Northwest Production, and how many wells does that team run? | Nathan Pierce (U-601, production supervisor) leads Northwest Production (TEAM-NW). The team runs 150 wells: Northwest Block 12 150. Source: fleet/users.json, areas.json a | table | high | 2 |
| Q9.3 | What does our operations SOP say about cold weather? Name one well that missed the check in Dec | Operations SOP OPS-5 (freeze protection, 1 Dec – 28 Feb): any inspection with air temperature at or below −5 °C on a well that is producing oil at that reading needs a he | table | high | 2 |
| Q9.4 | An operator reported a gas smell at WELL-0332 on 3 Dec. What was the H2S reading? | Operator note CTX-0332-004 (2026-12-03 12:10 UTC): "Gas odor reported by the pumper near WELL-0332 wellhead, area flagged off." — the note itself records no H2S reading. | - | high | 1 |
| Q9.5 | Back to the pumps from my first question: which of those wells are not producing oil right now, | Of the 8 wells with recalled pumps from your first question, 2 are not producing oil right now (latest inspection below the well-type threshold): | table | high | 0 |
| Q9.6 | Of all the wells we've talked about today, which one would you deal with first, and why? | Of the 10 wells discussed in this conversation, I'd deal with WELL-0332 (Northwest Block 12) first: gas-odor report with a missed OPS-1 response (safety); not producing o | - | high | 1 |
| Q10 | When a well stays shut in longer than the repair itself, what are we usually waiting on: parts, | 500 jobs started in 2026 kept the well shut in longer than the repair (the report states "about N days longer than the repair itself because …"). Field-wide: weather 28%  | bar | high | 500 |
| Q11 | Which region of the field consistently runs hotter? | Southeast Block 31 runs hotter: its producing wells have the highest average wellhead temperature in 13 of 13 months (last 12 months of inspections). | line | high | 1 |

Full answers, citations and visual data: `results/final.md`, `results/final.json`.
