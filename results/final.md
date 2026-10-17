# Copilot answers (final_questions.json)

## Q1 — Michael Turner
**Q:** All our wells feed one reservoir. Map the reservoir pressure across the field from the pressure data.

I can't map reservoir pressure: **the dataset has no pressure measurements** (no reservoir, bottom-hole, tubing or casing pressure field in inspections, maintenance or notes). The only pressures in the data are flowline pressure-test values in repair reports, which are test pressures, not reservoir pressure. I won't draw a map from proxies such as wellhead temperature, because that would be misleading. If you can supply pressure surveys, I can map them.

*Visual:* None · *Citations:* inspections.jsonl schema, maintenance reports (pressure tests)

## Q2 — Robert Hayes
**Q:** Which well produced the most oil in 2026?

I can't say which well produced the most oil: **the dataset has no production volumes** (no barrels produced, no allocation or meter data). Inspections only say whether a well was producing oil at the time of the reading (wellhead minus air temperature against the well-type threshold). I could rank wells by the share of 2026 inspections that read as producing, but that measures uptime, not volume, so I won't present it as the top producer.

*Visual:* None · *Citations:* inspections.jsonl schema, well-type manuals

## Q3 — Laura Simmons
**Q:** Since 1 Nov 2026, every time an operator note reports gas at a well, did we get someone out to that well in time under our operating procedures? List every report and whether the response met the deadline.

**26 gas-odor reports** in operator notes since 1 Nov 2026 (OPS-1: smelled gas, rotten-egg smell, gas odor or H2S monitor alarm). **17 met** the deadline and **9 missed** it.

Rule (Operations SOP rev 2, OPS-1): a field response is a maintenance job (started_at) or a **manual** inspection (drone doesn't count) on that well, starting after the note, within 24 h for notes before 1 Jan 2027 and 12 h from 1 Jan 2027. Times are UTC as recorded.

Missed: WELL-0163 (2026-11-03 20:55 UTC, responded after 251.1 h > 24 h); WELL-0341 (2026-11-19 07:40 UTC, responded after 677.8 h > 24 h); WELL-0332 (2026-12-03 12:10 UTC, no response at all); WELL-0401 (2026-12-05 13:50 UTC, responded after 138.2 h > 24 h); WELL-0052 (2026-12-18 06:45 UTC, no response at all); WELL-0362 (2026-12-24 00:15 UTC, responded after 31.8 h > 24 h); WELL-0161 (2026-12-25 15:45 UTC, responded after 475.2 h > 24 h); WELL-0599 (2027-01-06 17:20 UTC, responded after 16.4 h > 12 h); WELL-0516 (2027-01-06 21:15 UTC, responded after 15.0 h > 12 h).

*Visual:* table · *Citations:* Operations SOP OPS-1, CTX-0163-002, MNT-0163-019, CTX-0149-004, MNT-0149-029, CTX-0165-001, MNT-0165-031, CTX-0341-002, INS-0341-0109, CTX-0091-001, MNT-0091-019, CTX-0423-002, INS-0423-0213, CTX-0059-002, INS-0059-0213, CTX-0332-004, CTX-0401-002, MNT-0401-033, CTX-0189-003, MNT-0189-037, CTX-0403-004, MNT-0403-024, CTX-0244-002, MNT-0244-026, CTX-0040-002

## Q4 — Chris Dalton
**Q:** Across all areas, which temporary flowline bypasses are in place right now, and is each one allowed? Also list any bypass, past or present, that stayed in after its approval ran out or was never approved at all.

**In place right now (3):** WELL-0248 (Southeast Block 31, in since 5 Nov 2026) — Allowed under MOC-2026-031 (extended by MOC-2026-044) until 28 Feb 2027; WELL-0249 (Southeast Block 31, in since 25 Nov 2026) — Expired; WELL-0405 (Northwest Block 12, in since 20 Dec 2026) — Not approved.

**Violations, past or present (5):** WELL-0087 — Expired (approval ended 15 Dec 2026, out 6 Jan 2027); WELL-0158 — Expired (approval ended 15 Dec 2026, out 28 Dec 2026); WELL-0249 — Expired (approval ended 15 Dec 2026, out still in); WELL-0405 — Not approved (no MOC names this well); WELL-0561 — Not approved (no MOC names this well).

Rule (OPS-2): allowed only on a well named in an unexpired MOC; a memo that extends another replaces its expiry date (MOC-2026-044 extends MOC-2026-031 to 28 Feb 2027). In/out times come from operator notes.

*Visual:* table · *Citations:* fleet/sops/moc-2026-031.md, fleet/sops/moc-2026-036.md, fleet/sops/moc-2026-044.md, Operations SOP OPS-2, CTX-0013-002, CTX-0013-005, CTX-0062-002, CTX-0062-005, CTX-0087-001, CTX-0087-004, CTX-0158-003, CTX-0158-005, CTX-0248-002, CTX-0249-002, CTX-0284-002, CTX-0284-003, CTX-0356-002, CTX-0356-003, CTX-0405-003, CTX-0461-002, CTX-0461-003, CTX-0476-002, CTX-0476-003, CTX-0561-004, CTX-0561-005

## Q5 — Michael Turner
**Q:** The State Oil & Gas Commission wrote to us in November 2026 about spills. Which of our spills does the letter cover, and on which ones are we not compliant? Show me a table.

The letter (20 Nov 2026) covers **reportable spills (≥ 5 bbl) in Northeast Block 7 and Northeast Block 8 since 1 Jun 2026**, excluding detections later confirmed not to be crude. That is **6 spills**; **3 are not compliant**: WELL-0123 (INS-0123-0093 (24 Sep 2026)), WELL-0182 (INS-0182-0208 (3 Dec 2026)), WELL-0262 (INS-0262-0218 (7 Jan 2027)).

Compliance test (HSE internal note in the letter, 22 Nov 2026): the clean-up report must contain "Soil samples sent to the lab." Field soil readings don't count. Results were due 15 Jan 2027 (today). Spills outside those two blocks, before 1 Jun 2026, or under 5 bbl are out of the letter's scope.

*Visual:* table · *Citations:* fleet/sops/regulator-letter-2026-11-20.md, INS-0119-0209, MNT-0119-029, INS-0123-0093, MNT-0123-014, INS-0168-0190, MNT-0168-024, INS-0182-0208, MNT-0182-028, INS-0262-0218, MNT-0262-029, INS-0277-0205, MNT-0277-031

## Q6 — Nathan Pierce
**Q:** Across the whole field, not just my area, for which wells do the latest inspection and the operator notes disagree about whether the well is producing oil? For each one, what is its real status right now, and why?

**15 wells** where the latest inspection and the latest shut-in/restart operator note disagree. Rule (Operations SOP OPS-3): the more recent evidence wins; a restart note newer than the inspection means producing (unconfirmed) until an inspection confirms; gas, bypass and equipment notes don't change status.

*Visual:* table · *Citations:* Operations SOP OPS-3, INS-0010-0219, CTX-0010-004, INS-0026-0216, CTX-0026-001, INS-0032-0219, CTX-0032-006, INS-0033-0222, CTX-0033-003, INS-0044-0218, CTX-0044-008, INS-0046-0220, CTX-0046-004, INS-0219-0171, CTX-0219-006, INS-0249-0120, CTX-0249-004, INS-0323-0219, CTX-0323-002, INS-0330-0213, CTX-0330-002, INS-0332-0217, CTX-0332-003, INS-0422-0215, CTX-0422-003

## Q7.1 — Robert Hayes
**Q:** Over the last month the operators have written notes about wells that sound or behave wrong. Which of those wells haven't had a repair since? Rank the 10 most likely to need a repair in the next 90 days, other than a spill clean-up, and quote the notes as evidence.

In the last month operators wrote abnormal-behaviour notes (rattling, rod squeal, fluid pound, tagging bottom, amps hunting, etc.) about **172 wells**; **160** have had no repair since the first such note. Ranked by: number of repeated notes, recent non-producing readings, corrective-repair frequency over 12 months, and recalled pumps. This is a judgement score, not a validated failure model.

*Visual:* table · *Citations:* 

## Q7.2 — Robert Hayes
**Q:** Which three would you send a crew to first this week, and why?

Send crews first to:
1. **WELL-0182** (Northeast Block 8) — 2027-01-05: "Heard fluid pound on WELL-0182, unit still running."; 6 corrective repairs in the last 12 months; 3 recent inspections not producing; last repair MNT-0182-029 26 Dec 2026 (Walking beam bearing wear).
2. **WELL-0411** (Northwest Block 12) — 2026-12-28: "Drive on WELL-0411 showing amps hunting between 38 and 44 A."; 5 corrective repairs in the last 12 months; 6 recent inspections not producing; last repair MNT-0411-023 6 Dec 2026 (Flowline corrosion pinhole leak).
3. **WELL-0297** (Northeast Block 7) — 2027-01-11: "Rod squeal at WELL-0297 stuffing box, greased the polished rod."; 6 corrective repairs in the last 12 months; 4 recent inspections not producing; last repair MNT-0297-036 8 Jan 2027 (Prime mover failure).
Why: these have the most repeated abnormal notes without a repair since, plus the strongest other warning signs. Gas-odor and recalled-pump items are handled under their own procedures.

*Visual:* table · *Citations:* 

## Q8.1 — Nathan Pierce
**Q:** WELL-0333's recalled pump was swapped out yesterday. The work order isn't in the system yet. Please count it as replaced from now on.

Noted for everyone: Nathan Pierce reports the recalled pump on WELL-0333 (lot LOT-2409-A, installed by MNT-0333-024) was swapped. The work order isn't in the system, so I'm counting WELL-0333 as replaced **on Nathan Pierce's first-hand report (shared memory, user-reported)**, not on records. I'll reconcile when the work order appears.

*Visual:* None · *Citations:* MNT-0333-024, shared memory

## Q8.2 — Nathan Pierce
**Q:** Also, just for me: whenever you list wells, sort them by area and then by well ID, and show costs in thousands of dollars.

Saved as a **private preference for Nathan Pierce only** (other users are not affected): lists of wells sorted by area, then well ID; costs in thousands of dollars. I'll apply it whenever I list wells for you.

*Visual:* None · *Citations:* memory_prefs (private)

## Q8.3 — Robert Hayes
**Q:** Which recalled pumps are still in the ground right now?

**8 recalled pumps are still in the ground across the field** (Highline lots LOT-2409-A, LOT-2409-C, LOT-2410-B from recall notice HPC-RN-2026-07; replacement was due 31 Dec 2026, so these are overdue).

By area: Northeast Block 8: 2, Northwest Block 12: 3, Southeast Block 32: 1, Southwest Block 23: 2.

Source: I take the pump currently in each well from the latest 'Parts installed' line in its maintenance reports; a recalled pump later replaced by a pump from another lot is not counted.

Not counted: WELL-0333 — Nathan Pierce reported on 2027-01-15 that the recalled pump was swapped (shared memory, user-reported; no work order in the system yet).

*Visual:* table · *Citations:* fleet/sops/supplier-recall-notice-2026-12-01.md, MNT-0428-022, MNT-0031-027, MNT-0263-033, MNT-0426-030, MNT-0156-027, MNT-0160-028, MNT-0577-028, MNT-0305-032

## Q8.4 — Olivia Grant
**Q:** Nathan told me the recalled pump on WELL-0577 was swapped as well. Take it off the recall list.

⚠ I have **not** taken WELL-0577 off the recall list. The data (maintenance report MNT-0577-028 (LOT-2409-A)) still shows recalled lot LOT-2409-A in the well, there is no work order for a swap, and this is a second-hand report: Nathan told Olivia Grant, not first-hand. I've recorded it in shared memory as **unconfirmed**, attributed to Olivia Grant (relaying Nathan). I'll remove it once Nathan confirms directly or the work order lands.

*Visual:* None · *Citations:* MNT-0577-028

## Q8.5 — Nathan Pierce
**Q:** Show me the recalled pumps that are still in the ground in my area, and what it cost to install each one.

**3 recalled pumps are still in the ground in your areas (Northwest Block 12)** (Highline lots LOT-2409-A, LOT-2409-C, LOT-2410-B from recall notice HPC-RN-2026-07; replacement was due 31 Dec 2026, so these are overdue).

By area: Northwest Block 12: 3.

Source: I take the pump currently in each well from the latest 'Parts installed' line in its maintenance reports; a recalled pump later replaced by a pump from another lot is not counted.

Total install job cost: $75.6K (full cost of the job that installed each pump, from maintenance.jsonl).

Not counted: WELL-0333 — Nathan Pierce reported on 2027-01-15 that the recalled pump was swapped (shared memory, user-reported; no work order in the system yet).

Applied your private preferences (sort_area_well, cost_thousands).

*Visual:* table · *Citations:* fleet/sops/supplier-recall-notice-2026-12-01.md, MNT-0428-022, MNT-0426-030, MNT-0305-032

## Q9.1 — Robert Hayes
**Q:** How many recalled pumps are still in the ground, and in which areas?

**8 recalled pumps are still in the ground across the field** (Highline lots LOT-2409-A, LOT-2409-C, LOT-2410-B from recall notice HPC-RN-2026-07; replacement was due 31 Dec 2026, so these are overdue).

By area: Northeast Block 8: 2, Northwest Block 12: 3, Southeast Block 32: 1, Southwest Block 23: 2.

Source: I take the pump currently in each well from the latest 'Parts installed' line in its maintenance reports; a recalled pump later replaced by a pump from another lot is not counted.

Not counted: WELL-0333 — Nathan Pierce reported on 2027-01-15 that the recalled pump was swapped (shared memory, user-reported; no work order in the system yet).

⚠ Still listed: WELL-0577 — Olivia Grant relayed that it was swapped ("Nathan told me the recalled pump on WELL-0577 was swapped as well. Take it off the recall list."), but that is second-hand and there is no work order; **unconfirmed** until the person who did it or a work order confirms it.

*Visual:* table · *Citations:* fleet/sops/supplier-recall-notice-2026-12-01.md, MNT-0428-022, MNT-0031-027, MNT-0263-033, MNT-0426-030, MNT-0156-027, MNT-0160-028, MNT-0577-028, MNT-0305-032

## Q9.2 — Robert Hayes
**Q:** Different topic. Who leads Northwest Production, and how many wells does that team run?

**Nathan Pierce** (U-601, production supervisor) leads Northwest Production (TEAM-NW). The team runs **150 wells**: Northwest Block 12 150. Source: fleet/users.json, areas.json and well metadata.

*Visual:* table · *Citations:* users.json, areas.json

## Q9.3 — Robert Hayes
**Q:** What does our operations SOP say about cold weather? Name one well that missed the check in December.

Operations SOP OPS-5 (freeze protection, 1 Dec – 28 Feb): any inspection with air temperature at or below −5 °C on a well that is producing oil at that reading needs a heat trace check (a maintenance job whose issue contains "Heat trace check") starting within 7 days after the inspection. A cold reading on a well that isn't producing needs no check.

Example: **WELL-0310** (Northwest Block 12) — inspection INS-0310-0213 on 17 Dec 2026 read -6.0 °C air while producing (Δ 19.3 °C), and no heat trace check started within 7 days. In total 4 December readings missed the check (table).

*Visual:* table · *Citations:* Operations SOP OPS-5, INS-0310-0213

## Q9.4 — Robert Hayes
**Q:** An operator reported a gas smell at WELL-0332 on 3 Dec. What was the H2S reading?

Operator note CTX-0332-004 (2026-12-03 12:10 UTC): "Gas odor reported by the pumper near WELL-0332 wellhead, area flagged off." — the note itself records **no H2S reading**.

OPS-1 response: none, - h after the note, deadline 24 h → **Missed**.

*Visual:* None · *Citations:* CTX-0332-004

## Q9.5 — Robert Hayes
**Q:** Back to the pumps from my first question: which of those wells are not producing oil right now, and when was each one last repaired?

Of the 8 wells with recalled pumps from your first question, **2 are not producing oil right now** (latest inspection below the well-type threshold):

*Visual:* table · *Citations:* 

## Q9.6 — Robert Hayes
**Q:** Of all the wells we've talked about today, which one would you deal with first, and why?

Of the 10 wells discussed in this conversation, I'd deal with **WELL-0332** (Northwest Block 12) first: gas-odor report with a missed OPS-1 response (safety); not producing oil right now. Safety items (gas) outrank production and recall items, then overdue recalls, then lost production. This is a judgement call based on the evidence above.

*Visual:* None · *Citations:* INS-0332-0217

## Q10 — Michael Turner
**Q:** When a well stays shut in longer than the repair itself, what are we usually waiting on: parts, crews, contractors or weather? Break it down by area for jobs started in 2026, with the typical number of extra days, and tell me if any area stands out.

**500 jobs started in 2026** kept the well shut in longer than the repair (the report states "about N days longer than the repair itself because …"). Field-wide: weather 28% (median 9 extra days), contractors 26% (median 9 extra days), parts 23% (median 9 extra days), crews 22% (median 9 extra days).

By area: Northeast Block 7: 56 jobs, mostly parts (parts 27% (median 15 d, mean 14.1 d), contractors 27% (median 8 d, mean 9.3 d), crews 20% (median 16 d, mean 17.5 d), weather 27% (median 9 d, mean 11.5 d)); Northeast Block 8: 67 jobs, mostly crews (parts 19% (median 10 d, mean 13.7 d), contractors 25% (median 9 d, mean 13.3 d), crews 28% (median 14 d, mean 11.9 d), weather 27% (median 8 d, mean 8.7 d)); Northwest Block 12: 129 jobs, mostly weather (parts 22% (median 9 d, mean 10.1 d), contractors 21% (median 9 d, mean 12.4 d), crews 28% (median 8.5 d, mean 11.3 d), weather 29% (median 9 d, mean 11.7 d)); Southeast Block 31: 27 jobs, mostly contractors (parts 22% (median 8.5 d, mean 8.7 d), contractors 37% (median 15.5 d, mean 12.4 d), crews 11% (median 2 d, mean 4.0 d), weather 30% (median 12.5 d, mean 12.1 d)); Southeast Block 32: 111 jobs, mostly contractors (parts 23% (median 9.5 d, mean 11.6 d), contractors 30% (median 9 d, mean 13.7 d), crews 19% (median 10 d, mean 12.2 d), weather 28% (median 8 d, mean 13.7 d)); Southwest Block 23: 58 jobs, mostly parts (parts 28% (median 12.5 d, mean 15.8 d), contractors 21% (median 12.5 d, mean 13.8 d), crews 24% (median 7 d, mean 9.1 d), weather 28% (median 9 d, mean 12.4 d)); Southwest Block 24: 52 jobs, mostly contractors (parts 23% (median 8 d, mean 9.8 d), contractors 33% (median 8 d, mean 7.3 d), crews 15% (median 12 d, mean 10.6 d), weather 29% (median 10 d, mean 11.5 d)).

Stands out: no area's mix differs from the field mix by more than 20 percentage points, and the typical extra wait is about the same everywhere; Northwest Block 12 simply has the most delayed jobs.

*Visual:* bar · *Citations:* MNT-0001-028, MNT-0001-033, MNT-0002-018, MNT-0004-021, MNT-0004-026, MNT-0005-031, MNT-0006-023, MNT-0006-025, MNT-0006-026, MNT-0007-031, MNT-0009-026, MNT-0010-024, MNT-0010-027, MNT-0013-037, MNT-0013-038, MNT-0014-015, MNT-0015-030, MNT-0015-032, MNT-0015-036, MNT-0018-028, MNT-0019-026, MNT-0020-030, MNT-0020-034, MNT-0021-027, MNT-0021-032

## Q11 — Olivia Grant
**Q:** Which region of the field consistently runs hotter?

**Southeast Block 31** runs hotter: its producing wells have the highest average wellhead temperature in **13 of 13 months** (last 12 months of inspections).

It isn't the weather: air temperature at inspection is the same across all areas (largest monthly spread between areas 0.7 °C). The gap holds within each well type (wellhead minus air, table), so it is not just a different well-type mix.

Readings are drone/manual thermal snapshots, so this is evidence of a consistent pattern, not a root cause.

*Visual:* line · *Citations:* inspections.jsonl wellhead_temp_c / ambient_temp_c

