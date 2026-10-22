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

**15 wells** where the latest inspection and the latest operator note saying the well was shut in or restarted disagree. Real status now: **4 producing**, **11 not producing** (table, one line per well with the reason).

Rule (Operations SOP OPS-3): the more recent of the two wins. A shut-in note newer than the inspection means not producing (shut in); a restart note newer than the inspection means producing (unconfirmed) until an inspection confirms it; an inspection newer than the note stands. Inspections are read after any data_correction note. Gas, bypass and equipment notes don't change status.

Not producing because the note is newer: WELL-0044, WELL-0323, WELL-0355, WELL-0422, WELL-0479, WELL-0481. Producing (unconfirmed) because a restart note is newer: WELL-0026, WELL-0032, WELL-0033, WELL-0046. Inspection is newer, so it stands: WELL-0010 (not producing oil), WELL-0330 (not producing oil), WELL-0332 (not producing oil), WELL-0429 (not producing oil), WELL-0452 (not producing oil).

**Assumption, stated:** I read "drive tripping …, restarted/reset from the panel" as an equipment remark (the well was never shut in), so it doesn't count under OPS-3. If you count it as a restart note, 2 more well(s) disagree: WELL-0219 (WELL-0219 drive tripping on underload, restarted from the panel.) → still **not producing oil**, because inspection is more recent than the note (OPS-3); WELL-0249 (WELL-0249 drive tripping on underload, restarted from the panel.) → still **not producing oil**, because inspection is more recent than the note (OPS-3). The status answer is the same under both readings.

*Visual:* table · *Citations:* Operations SOP OPS-3, INS-0010-0219, CTX-0010-004, INS-0026-0216, CTX-0026-001, INS-0032-0219, CTX-0032-006, INS-0033-0222, CTX-0033-003, INS-0044-0218, CTX-0044-008, INS-0046-0220, CTX-0046-004, INS-0219-0171, CTX-0219-006, INS-0249-0120, CTX-0249-004, INS-0323-0219, CTX-0323-002, INS-0330-0213, CTX-0330-002, INS-0332-0217, CTX-0332-003, INS-0355-0213, CTX-0355-004

## Q7.1 — Robert Hayes
**Q:** Over the last month the operators have written notes about wells that sound or behave wrong. Which of those wells haven't had a repair since? Rank the 10 most likely to need a repair in the next 90 days, other than a spill clean-up, and quote the notes as evidence.

In the last month (15 Dec 2026 – 15 Jan 2027) operators wrote notes about **175 wells** that sound or behave wrong (rattling, rod squeal, fluid pound, tagging bottom, amps hunting, drive trips, stuffing-box leaks). **160** have had no repair since the latest such note (spill clean-ups don't count as a repair; 0 more would drop out if you count from the first note instead).

How I ranked them: wells with a failure precursor that the documents name come first, then by points (table) — the T500 manual's early-warning temperature fall (8), repeated drive trips (6), and a well that reads not producing with no shut-in or job to explain it (6; T200 manual: 'unit running, wellhead cold' = rod parted or pump stuck). Then repeated notes (1.5 each, up to 3), different symptoms (+1 each), corrective repairs on the same equipment in 12 months (+1 each, +2 at the RCA threshold) and a recalled pump (+2). There is no history to validate a 90-day failure model, so this is an evidence-weighted ranking, not a probability.

Left out because a repair is already under way: WELL-0197 (MNT-0197-029 Sucker rod parted, started 1 Jan 2027, due to finish 19 Jan 2027); WELL-0249 (MNT-0249-018 ESP motor burnout, started 9 Jan 2027, due to finish 2 Feb 2027); WELL-0263 (MNT-0263-035 Flowline corrosion pinhole leak, started 9 Jan 2027, due to finish 19 Jan 2027).

Also showing a documented precursor but ranked below #10 on supporting evidence: WELL-0430, WELL-0442, WELL-0202, WELL-0097, WELL-0471, WELL-0478.

Tied with #10 on score: WELL-0430, WELL-0442 (sorted by well ID).

*Visual:* table · *Citations:* CTX-0336-003, CTX-0336-004, CTX-0336-005, INS-0336-0218, CTX-0401-003, CTX-0401-004, INS-0401-0221, CTX-0175-003, CTX-0175-006, CTX-0175-007, INS-0175-0216, CTX-0329-002, CTX-0329-003, INS-0329-0218, CTX-0344-002, CTX-0344-003, CTX-0344-004, INS-0344-0219, CTX-0219-006, CTX-0219-007, INS-0219-0171, CTX-0010-005, CTX-0010-006, CTX-0010-007, INS-0010-0219

## Q7.2 — Robert Hayes
**Q:** Which three would you send a crew to first this week, and why?

Send crews first to WELL-0336, WELL-0401 and WELL-0175:
1. **WELL-0336** (Northwest Block 12, T500, score 16.5) — CTX-0336-005 2027-01-14: "WELL-0336 amps hunting on the drive panel, still running.". Why: T500 early-warning pattern: wellhead-minus-air fell 3 inspections in a row by 4.2 °C (37.3 → 36.9 → 34.9 → 33.1); the manual says ESP motors usually fail after this and calls for a drive and insulation check within 14 days, i.e. by 28 Jan 2027; drive trip reset by the operator; 1 corrective repair(s) on the same equipment (esp_pump) in the last 12 months. Last repair: MNT-0336-026 8 May 2026 (ESP motor burnout).
2. **WELL-0401** (Northwest Block 12, T500, score 15.0) — CTX-0401-004 2027-01-14: "WELL-0401 amps hunting on the drive panel, still running.". Why: T500 early-warning pattern: wellhead-minus-air fell 3 inspections in a row by 3.8 °C (34.1 → 32.9 → 31.6 → 30.3); the manual says ESP motors usually fail after this and calls for a drive and insulation check within 14 days, i.e. by 28 Jan 2027; 2 corrective repair(s) on the same equipment (esp_pump) in the last 12 months — at the RCA threshold (2). Last repair: MNT-0401-032 27 Nov 2026 (ESP motor burnout).
3. **WELL-0175** (Northeast Block 8, T200, score 13.5) — CTX-0175-007 2026-12-26: "WELL-0175 tagging bottom on the downstroke, adjust spacing next visit.". Why: latest inspection INS-0175-0216 (14 Jan 2027) reads not producing (Δ 5.5 °C, below the 15 °C rule) with no shut-in note or open job to explain it — for a rod-lift well the manual lists 'unit running, wellhead cold' as rod parted or pump stuck; 1 corrective repair(s) on the same equipment (wellhead) in the last 12 months. Last repair: MNT-0175-031 30 May 2026 (Stuffing box packing leak).
Why these three: each has a precursor the manuals treat as an imminent or actual failure, not just a noise note; next in line is WELL-0329 (score 13.0). Assumption: this is about the noise/behaviour list from your previous question. Safety items come before all of it: an unanswered gas-odor report (OPS-1) or an overdue recalled pump is handled under its own procedure, so check those lists too before you plan the week.

*Visual:* table · *Citations:* CTX-0336-003, CTX-0336-004, CTX-0336-005, INS-0336-0218, CTX-0401-003, CTX-0401-004, INS-0401-0221, CTX-0175-003, CTX-0175-006, CTX-0175-007, INS-0175-0216

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

Of the **10 wells** we've discussed in this conversation (WELL-0428, WELL-0031, WELL-0263, WELL-0426, WELL-0156, WELL-0160, WELL-0577, WELL-0305, WELL-0310, WELL-0332), I'd deal with **WELL-0332** (Northwest Block 12) first: gas-odor report 2026-12-03 with a missed OPS-1 response and **no crew on site since** (only drone inspections) — an open safety item; not producing now (INS-0332-0217, Δ 0.5 °C) with no repair under way; abnormal operator notes with no repair since (pump-jack rattle/knock, stuffing-box squeal/leak).

How I weighed them: an unanswered safety report beats everything (gas/H2S can hurt people; OPS-1 and WS-03), then an overdue recalled pump (compliance with the supplier recall), then lost production, then abnormal-behaviour notes. Full comparison in the table.

Runner-up: **WELL-0160** (Northeast Block 8): recalled pump (LOT-2409-C) still in the ground, past the 31 Dec 2026 replacement date; not producing now, but repair MNT-0160-032 (Walking beam bearing wear) is already under way until 26 Jan 2027. Tied on points with WELL-0263, WELL-0305, WELL-0428.

If you mean 'first' for production or the recall rather than safety, the answer changes: the recalled-pump wells come first.

Quick win: a repair crew is already on WELL-0160, WELL-0263, which still have recalled pumps; it is worth scheduling the pump swap while the well is already down.

Assumption: 'today' means this conversation (the wells named in my earlier answers here). This is a judgement call based on the evidence shown, not a computed risk.

*Visual:* table · *Citations:* Operations SOP OPS-1, recall notice, INS-0332-0217, INS-0160-0217, MNT-0160-032, INS-0263-0219, MNT-0263-035

## Q10 — Michael Turner
**Q:** When a well stays shut in longer than the repair itself, what are we usually waiting on: parts, crews, contractors or weather? Break it down by area for jobs started in 2026, with the typical number of extra days, and tell me if any area stands out.

**500 jobs started in 2026** kept the well shut in longer than the repair (the report states "about N days longer than the repair itself because …"). Field-wide the waits split weather 28%, contractors 26%, parts 23%, crews 22%: **no single cause dominates**, weather is only slightly ahead, four causes in roughly equal shares. Typical extra time: median **9 days** (mean 11.9), about the same for every cause.

By area (table): Northeast Block 7: 56 jobs (44% of its jobs), mostly parts, median 9 extra days; Northeast Block 8: 67 jobs (49% of its jobs), mostly crews, median 9 extra days; Northwest Block 12: 129 jobs (42% of its jobs), mostly weather, median 9 extra days; Southeast Block 31: 27 jobs (36% of its jobs), mostly contractors, median 10 extra days; Southeast Block 32: 111 jobs (44% of its jobs), mostly contractors, median 9 extra days; Southwest Block 23: 58 jobs (39% of its jobs), mostly parts, median 9 extra days; Southwest Block 24: 52 jobs (39% of its jobs), mostly contractors, median 8.5 extra days.

Does any area stand out? **Not clearly.** The reason mix doesn't differ between areas more than chance would (chi-square 12.4 on 18 df, p≈0.83), and no area's waiting time for any cause differs clearly from the field. Worth watching, but small samples: Northeast Block 7 parts: median 15 extra days vs 9 field-wide (n=15, p≈0.21); Northeast Block 7 crews: median 16 extra days vs 9 field-wide (n=11, p≈0.11); Northeast Block 8 crews: median 14 extra days vs 9 field-wide (n=19, p≈0.23); Southeast Block 31 contractors: median 15.5 extra days vs 9 field-wide (n=10, p≈0.10); Southeast Block 31 contractors share 37% vs 26% field-wide (10 of 27 jobs); Southeast Block 31 crews share 11% vs 22% field-wide (3 of 27 jobs). Delays are most common in Northeast Block 8 (49% of jobs) and least common in Southeast Block 31 (36%); Northwest Block 12 has the most delayed jobs simply because it has the most wells.

Method: the cause is read from the 'because …' clause (back-ordered part → parts, weekday contractor slot → contractors, crew committed elsewhere or rig busy → crews, rain/road → weather); 'typical' = median.

*Visual:* bar · *Citations:* MNT-0001-028, MNT-0001-033, MNT-0002-018, MNT-0004-021, MNT-0004-026, MNT-0005-031, MNT-0006-023, MNT-0006-025, MNT-0006-026, MNT-0007-031, MNT-0009-026, MNT-0010-024, MNT-0010-027, MNT-0013-037, MNT-0013-038, MNT-0014-015, MNT-0015-030, MNT-0015-032, MNT-0015-036, MNT-0018-028, MNT-0019-026, MNT-0020-030, MNT-0020-034, MNT-0021-027, MNT-0021-032

## Q11 — Olivia Grant
**Q:** Which region of the field consistently runs hotter?

**Southeast Block 31** runs hotter: its producing wells have the highest average wellhead temperature in **13 of 13 months** (last 12 months of inspections).

It isn't the weather: air temperature at inspection is the same across all areas (largest monthly spread between areas 0.7 °C). The gap holds within each well type (wellhead minus air, table), so it is not just a different well-type mix.

Readings are drone/manual thermal snapshots, so this is evidence of a consistent pattern, not a root cause.

*Visual:* line · *Citations:* inspections.jsonl wellhead_temp_c / ambient_temp_c

