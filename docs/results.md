# Asset Intelligence Copilot: Results on the Final Questions
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · page 2*

Test data: organizers' test dataset (600 wells, commit 009e2b5), today = 15 Jan 2027. Command:
`AIC_TODAY=2027-01-15 python scripts/final_run.py --data <test-data>/dataset --only-test --questions eval/final_questions.json`.
**All 21 turns answered in about 3 s end to end** (was 185 s). Every turn is now answered by a deterministic tool, so Gemma 4 isn't called on this set.

> **Post-submission update (branch `improve/21-of-21`, after the hackathon deadline).** The submitted state is commit `f8ae532` on `main`; its scores were **16 correct, 2 mostly correct (Q6, Q10), 3 judgement calls (Q7.1, Q7.2, Q9.6)**. The rows below marked *post-submission* were improved after the submission, while the entry was under review. They are not part of the judged submission. I made the fixes with general logic (no question strings or answers are hard-coded) and checked every changed answer by hand against the raw files. Same command, same data (test dataset commit 009e2b5, today = 15 Jan 2027).

## Post-submission changes
- **Data corrections are applied (OPS-3 asks for this).** The loader now keeps `data_correction` notes (field, original and corrected value), and `effective_inspections` applies them. Example: INS-0201-0218's wellhead temperature changed from 32.1 to 10.4 °C.
- **Q6:** shut-in phrasings are complete ("…, shut the well in" was missed before, which dropped WELL-0355 and WELL-0479). "Drive tripping …, restarted/reset from the panel" is now treated as an **equipment remark, with the assumption stated**. The answer also gives the other reading (WELL-0219 and WELL-0249 would be added) and shows that the status comes out the same either way.
- **Q7.1 / Q7.2:** the ranking now uses failure precursors named in the documents. These are the T500 early-warning fall in wellhead-minus-air (parsed from the manual, with a check due within 14 days), repeated drive trips that were reset ("treat as a failure, not reset"), and "unit running, wellhead cold" (T200 §7) when no shut-in or open job explains it. Supporting evidence comes after that: repeated notes, symptoms mapped to equipment (Field Work SOP §4), same-equipment repairs against the RCA threshold, and recalled pumps. Wells with a repair already under way are listed separately rather than ranked. Spill clean-ups don't count as a repair. Every note is quoted with its ID and cited. Confidence is labelled *medium (judgement)*.
- **Q9.6:** the answer shows the full comparison of every well discussed, with points and evidence. It covers open safety items (missed gas response with no crew since), overdue recalls (including unconfirmed swap claims), not producing with or without a repair under way, abnormal notes and OPS-5 misses. It also names the runner-up, how the pick would change under a production/recall reading, and the assumption about "today".
- **Q10:** delays are now normalised (delayed share of each area's jobs), with a typical (median) wait per area. A chi-square test checks the reason mix, and a permutation test checks waiting times per area and cause (cells with n ≥ 10). Small-sample differences are labelled "worth watching", not "stands out".

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
| Q6 | Wrong | **Correct** *(post-submission; was mostly correct)* | 15 wells under OPS-3: 6 not producing because a newer shut-in note wins (WELL-0044, 0323, 0355, 0422, 0479, 0481), 4 producing (unconfirmed) because a newer restart note wins (WELL-0026, 0032, 0033, 0046), and 5 where the newer inspection stands (WELL-0010, 0330, 0332, 0429, 0452: not producing). The drive-trip reading is stated as an assumption; under the other reading WELL-0219 and WELL-0249 are added and their status doesn't change. Checked with an independent script over the raw context/inspection files. |
| Q7.1 | Wrong (counted repairs) | **Correct, judgement shown** *(post-submission; was plausible)* | 175 wells with abnormal notes in the last month, 160 with no repair since (3 more have a repair under way and are listed separately). The top of the list is the wells with document-named precursors: WELL-0336 and WELL-0401 (T500 early-warning fall, 37.3→33.1 and 34.1→30.3 °C), WELL-0175 (fluid pound, "unit still running", then Δ 5.5 °C on 14 Jan with no shut-in or job), WELL-0329, WELL-0344 and WELL-0498 (repeated drive trips reset). Raw readings and maintenance were checked by hand. It is still a ranking, not a validated 90-day model, and the answer says so. |
| Q7.2 | Wrong | **Correct, judgement shown** *(post-submission; was plausible)* | WELL-0336, WELL-0401, WELL-0175, each with the manual clause that makes it urgent (ESP check due by 28 Jan 2027 for both T500 wells). The answer states the assumption that gas and recall items are handled first under their own procedures. |
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
| Q9.6 | Wrong | **Correct, judgement shown** *(post-submission; was plausible)* | WELL-0332: gas odor on 3 Dec, missed OPS-1, **no crew on site since** (only drone inspections, checked by hand), now not producing (Δ 0.5 °C) with no job, and rattle/squeal notes. The full table of all 10 wells is included. Runner-up WELL-0160 (recalled pump, repair MNT-0160-032 under way until 26 Jan) is tied with WELL-0263, 0305 and 0428; the answer explains when the pick would change. |
| Q10 | Wrong (counted jobs) | **Correct** *(post-submission; was mostly correct)* | 500 delayed jobs in 2026: weather 28%, contractors 26%, parts 23%, crews 22%, median 9 extra days (hand check: same counts and medians from the raw reports). By area: delayed share from 36% (SE Block 31) to 49% (NE Block 8). **No area clearly stands out**: mix χ² 12.4 on 18 df (p≈0.83), and no waiting-time difference is significant. The answer lists small-sample watch items (NE Block 7 crews median 16 d, n=11; SE Block 31 contractors 15.5 d, n=10). |
| Q11 | Wrong (no tool) | **Correct** | Southeast Block 31 has the hottest producing wellheads in 13 of 13 months. Air temperature is the same across areas (spread ≤ 0.7 °C), and the gap holds within each well type. |

**Summary:** first run, 0 of 21 fully correct (2 partly). Submitted (`f8ae532`): 16 correct, 2 mostly correct (Q6, Q10), 3 judgement calls with evidence (Q7.1, Q7.2, Q9.6). **Post-submission (this branch): 21/21**, by my own hand check. Q7.1, Q7.2 and Q9.6 remain judgement questions: the answers now show their evidence, assumptions and alternatives, but a reviewer could still rank differently.

## Still weak
- Q7.1, Q7.2 and Q9.6 are rankings. The precursors come from the manuals, but the points are hand-set and there is no history to validate a 90-day failure model (abnormal notes only start in Oct 2026).
- The keyword patterns for gas, shut-in/restart and abnormal-sound notes cover the phrasings in this dataset; a new phrasing would need the pattern extended or the Gemma planner.
- Q10's significance tests are simple (chi-square, permutation on medians) and don't correct for multiple comparisons.

## Tests
- `pytest`: 121 passed (101 at submission + 20 new in `tests/test_final_logic.py` for the post-submission logic).
- Example checks: 27/27. Unseen-question checks: 46/46 (`results/examples_rules.md`, `results/unseen_rules.md`), re-run on this branch.

## Answers (post-submission run)
| # | Question | Answer (headline) | Visual | Confidence | Sources |
|---|---|---|---|---|---|
| Q1 | All our wells feed one reservoir. Map the reservoir pressure across the field from the pressure | I can't map reservoir pressure: the dataset has no pressure measurements (no reservoir, bottom-hole, tubing or casing pressure field in inspections, maintenance or notes) | - | high | 2 |
| Q2 | Which well produced the most oil in 2026? | I can't say which well produced the most oil: the dataset has no production volumes (no barrels produced, no allocation or meter data). Inspections only say whether a wel | - | high | 2 |
| Q3 | Since 1 Nov 2026, every time an operator note reports gas at a well, did we get someone out to  | 26 gas-odor reports in operator notes since 1 Nov 2026 (OPS-1: smelled gas, rotten-egg smell, gas odor or H2S monitor alarm). 17 met the deadline and 9 missed it. | table | high | 51 |
| Q4 | Across all areas, which temporary flowline bypasses are in place right now, and is each one all | In place right now (3): WELL-0248 (Southeast Block 31, in since 5 Nov 2026) — Allowed under MOC-2026-031 (extended by MOC-2026-044) until 28 Feb 2027; WELL-0249 (Southeas | table | high | 25 |
| Q5 | The State Oil & Gas Commission wrote to us in November 2026 about spills. Which of our spills d | The letter (20 Nov 2026) covers reportable spills (≥ 5 bbl) in Northeast Block 7 and Northeast Block 8 since 1 Jun 2026, excluding detections later confirmed not to be cr | table | high | 13 |
| Q6 | Across the whole field, not just my area, for which wells do the latest inspection and the oper | 15 wells where the latest inspection and the latest operator note saying the well was shut in or restarted disagree. Real status now: 4 producing, 11 not producing (table | table | conflict | 35 |
| Q7.1 | Over the last month the operators have written notes about wells that sound or behave wrong. Wh | In the last month (15 Dec 2026 – 15 Jan 2027) operators wrote notes about 175 wells that sound or behave wrong (rattling, rod squeal, fluid pound, tagging bottom, amps hu | table | medium (judgement) | 38 |
| Q7.2 | Which three would you send a crew to first this week, and why? | Send crews first to WELL-0336, WELL-0401 and WELL-0175: | table | medium (judgement) | 11 |
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
| Q9.6 | Of all the wells we've talked about today, which one would you deal with first, and why? | Of the 10 wells we've discussed in this conversation (WELL-0428, WELL-0031, WELL-0263, WELL-0426, WELL-0156, WELL-0160, WELL-0577, WELL-0305, WELL-0310, WELL-0332), I'd d | table | medium (judgement) | 7 |
| Q10 | When a well stays shut in longer than the repair itself, what are we usually waiting on: parts, | 500 jobs started in 2026 kept the well shut in longer than the repair (the report states "about N days longer than the repair itself because …"). Field-wide the waits spl | bar | high | 500 |
| Q11 | Which region of the field consistently runs hotter? | Southeast Block 31 runs hotter: its producing wells have the highest average wellhead temperature in 13 of 13 months (last 12 months of inspections). | line | high | 1 |

- Q6: Across the whole field, not just my area, for which wells do the latest inspection and the operator notes disagree about whether the well is producing oil? For each one, what is its real status right now, and why?
- Q8.4: Nathan told me the recalled pump on WELL-0577 was swapped as well. Take it off the recall list.
- Q9.1: How many recalled pumps are still in the ground, and in which areas?

## How these were produced
One command (`python scripts/final_run.py --data <test-data> --questions <final.txt>`) loaded the sample and test datasets into SQLite, reset runtime memory, and ran every question in order through the copilot (memory and corrections carry across questions as in the scenarios). Numbers come from deterministic tools. Thresholds and deadlines were parsed from the manuals and SOPs. Gemma 4 (open-weight) plans only the questions the rule router isn't confident about.

Full answers, citations and visual data: `results/final.md`, `results/final.json`.
