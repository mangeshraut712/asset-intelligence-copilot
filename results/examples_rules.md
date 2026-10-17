# Copilot answers (examples.json)

**Score: 27/27**

## Q1 — Michael Turner
**Q:** Is WELL-0001 producing oil right now? When was it last inspected, and by whom?

**WELL-0001 is not producing oil** (as of its latest inspection).

Latest inspection INS-0001-0203 on 15 Oct 2026, by drone, by Ryan Brooks. Wellhead 25.6 °C vs air 22.4 °C: 3.2 °C warmer, below the T200 limit of 15 °C.

Inspector note on that inspection: "Pump jack not moving."

Reason: Note CTX-0001-003 by Jake Morales: Well shut in from 7 Oct for planned rod string replacement. Work order not yet in the maintenance system. Expected back online around 20 Oct.

The recorded status still says **active**, which is out of date.

*Visual:* card · *Citations:* INS-0001-0203, T200 manual, CTX-0001-003

*Check:* PASS   

## Q2 — Michael Turner
**Q:** Which wells in Northeast Block 8 are not producing oil right now, and why? Show them in a table.

**4 wells in Northeast Block 8 are not producing oil right now** (latest inspection per well): WELL-0164, WELL-0170, WELL-0172, WELL-0175.

*Visual:* table · *Citations:* INS-0164-0205, INS-0170-0206, INS-0172-0206, INS-0175-0204, T200/T350 manual production rule

*Check:* PASS   

## Q3 — Michael Turner
**Q:** Show a line chart of WELL-0001's wellhead temperature against air temperature for the last 13 weeks, and mark when it was not producing oil.

13 readings for WELL-0001 (23 Jul 2026 to 15 Oct 2026). Not producing oil on: 8 Oct 2026, 15 Oct 2026 (wellhead less than 15 °C above air).

*Visual:* line · *Citations:* INS-0001-0191 … INS-0001-0203

*Check:* PASS   

## Q4 — Michael Turner
**Q:** How many oil spills has WELL-0001 had in the last 4 years, and how much oil in total? List them in a table.

**6 real spills for WELL-0001 (16 Oct 2022 to 16 Oct 2026), 15.1 barrels in total.** 7 detections; excluded as corrected: INS-0001-0070 (7 Mar 2024, CTX-0001-001).

*Visual:* table · *Citations:* INS-0001-0021, INS-0001-0027, INS-0001-0048, INS-0001-0051, INS-0001-0185, INS-0001-0201, CTX-0001-001, Dataset Guide: correction notes override detections

*Check:* PASS   

## Q5 — Michael Turner
**Q:** How many days was WELL-0001 down in 2025?

**WELL-0001 was down 21 days** (1 Jan 2025–31 Dec 2025), from 3 weekly inspections where it was not producing oil:
- 24 Jul 2025 (INS-0001-0140): wellhead 51.6 °C vs air 43.1 °C, only 8.5 °C warmer. Cause: Prime mover tripped on high temperature (MNT-0001-021).
- 16 Oct 2025 (INS-0001-0152): wellhead 26.6 °C vs air 23.2 °C, only 3.4 °C warmer. Cause: Stuffing box packing leak (MNT-0001-023).
- 23 Oct 2025 (INS-0001-0153): wellhead 16.0 °C vs air 16.6 °C, only -0.6 °C warmer. Cause: Stuffing box packing leak (MNT-0001-023); Scheduled lubrication and belt inspection (MNT-0001-024).

Downtime = 7 days per non-producing weekly inspection (Dataset Guide).

*Visual:* None · *Citations:* INS-0001-0140, INS-0001-0152, INS-0001-0153, Dataset Guide (downtime), well-type manual

*Check:* PASS   

## Q6 — Michael Turner
**Q:** Which 3 wells in Northeast Block 7 had the most downtime in the last 4 months? Show a bar chart.

**Top 3 wells in Northeast Block 7 by downtime (16 Jun 2026 to 16 Oct 2026):** WELL-0121: 49 days (T200), WELL-0107: 42 days (T350), WELL-0138: 42 days (T350). Next is WELL-0119 at 28.
- WELL-0121 why: Gearbox oil leak (MNT-0121-031); Scheduled wellhead valve service (MNT-0121-033); Prime mover failure (MNT-0121-034); Prime mover failure (MNT-0121-034)
- WELL-0107 why: Stuffing box packing leak (MNT-0107-028); Stuffing box packing leak (MNT-0107-028); Annual flowline integrity test (MNT-0107-029)
- WELL-0138 why: Prime mover failure (MNT-0138-031); Prime mover failure (MNT-0138-032); Gearbox oil leak (MNT-0138-034)

*Visual:* bar · *Citations:* INS-0121-0189, INS-0121-0200, INS-0121-0201, INS-0121-0202, INS-0121-0203, INS-0121-0205, INS-0121-0206, INS-0107-0194, INS-0107-0195, INS-0107-0196, INS-0107-0197, INS-0107-0198, INS-0107-0199, INS-0138-0195, INS-0138-0196, INS-0138-0200, INS-0138-0201, INS-0138-0206, INS-0138-0207, Dataset Guide (downtime = 7 d per non-producing inspection)

*Check:* PASS   

## Q7 — Michael Turner
**Q:** Show on a map every well in Northeast Block 8 with a real spill in the last 90 days.

**4 real spills for Northeast Block 8 (19 Jul 2026 to 16 Oct 2026), 10.2 barrels in total.** 6 detections; excluded as corrected: INS-0194-0192 (23 Jul 2026, CTX-0194-002), INS-0199-0200 (10 Sep 2026, CTX-0199-002). 4 wells: WELL-0151 (24 Sep 2026, 4.5 bbl, 32.12246, -102.18445); WELL-0165 (30 Jul 2026, 1.2 bbl, 32.15665, -102.14522); WELL-0175 (30 Jul 2026, 3.9 bbl, 32.1802, -102.1479); WELL-0186 (23 Jul 2026, 0.6 bbl, 32.17552, -102.17775)

*Visual:* map · *Citations:* INS-0151-0201, INS-0165-0194, INS-0175-0193, INS-0186-0097, CTX-0194-002, CTX-0199-002, Dataset Guide: correction notes override detections

*Check:* PASS   

## Q8 — Michael Turner
**Q:** Show a heatmap of 2026 spills by geographic area and month.

Real spills in 2026 by area and month (corrected detections removed). Totals: Southwest Block 23: 35, Southwest Block 24: 43, Northeast Block 7: 37, Northeast Block 8: 26

*Visual:* heatmap · *Citations:* inspections (spill_detected, corrections applied), context.jsonl correction notes

*Check:* PASS   

## Q9 — Michael Turner
**Q:** Which rules has WELL-0001 broken in the last 12 months, and what is still open?

**WELL-0001: 4 rule breach(es) in the last 12 months**, USD 5,000 in fines still open.
- **SR-01** (11 Jun 2026 (6.8 bbl, INS-0001-0185)): written notice after 41 h vs 24 h limit (REG-0001-001)
- **SR-03** (11 Jun 2026 (6.8 bbl, INS-0001-0185)): agency clean-up verification due by 10 Aug 2026, still open (REG-0001-003)
- **RC-04** (11 Jun 2026 (6.8 bbl, INS-0001-0185)): response to REG-0001-002 was due by 30 Jul 2026; none recorded
- **SR-02** (11 Jun 2026 (6.8 bbl, INS-0001-0185)): contained after about 7 h vs 4 h limit (report MNT-0001-029)

**Still open / pending:**
- SR-01: notice of violation REG-0001-002, fine USD 5,000, still open
- RCA: root-cause analysis due on flowline: 3 corrective repairs in 12 months (MNT-0001-028, MNT-0001-029, MNT-0001-032)
- Manual §4: planned shut-in not yet recorded in the maintenance system, which the manual requires before work starts (CTX-0001-003)

**Met:**
- SR-02: contained after about 1.7 h vs 4 h limit (report MNT-0001-032)
- RC-02: annual flowline integrity test done 7 Mar 2026 (MNT-0001-026)

*Visual:* table · *Citations:* INS-0001-0185, REG-0001-001, REG-0001-002, REG-0001-003, MNT-0001-029, INS-0001-0201, MNT-0001-032, MNT-0001-028, MNT-0001-026, CTX-0001-003, Spill Response SOP, Regulatory Compliance SOP

*Check:* PASS   

## Q10 — Michael Turner
**Q:** In Southwest Block 24, which spills in the last 90 days were not contained within the SOP time limit?

**2 spills in Southwest Block 24 were not contained within the 4-hour SOP limit (SR-02):** WELL-0082 after about 7.1 h (report MNT-0082-028, inspection INS-0082-0198); WELL-0100 after about 8.1 h (report MNT-0100-034, inspection INS-0100-0196). Containment times come from the free-text repair reports.

*Visual:* table · *Citations:* MNT-0082-028, MNT-0100-034, INS-0082-0198, INS-0100-0196, Spill Response SOP SR-02

*Check:* PASS   

## Q11a — Michael Turner
**Q:** Which 3 wells in Northeast Block 7 had the most downtime in the last 4 months? Show a bar chart.

**Top 3 wells in Northeast Block 7 by downtime (16 Jun 2026 to 16 Oct 2026):** WELL-0121: 49 days (T200), WELL-0107: 42 days (T350), WELL-0138: 42 days (T350). Next is WELL-0119 at 28.
- WELL-0121 why: Gearbox oil leak (MNT-0121-031); Scheduled wellhead valve service (MNT-0121-033); Prime mover failure (MNT-0121-034); Prime mover failure (MNT-0121-034)
- WELL-0107 why: Stuffing box packing leak (MNT-0107-028); Stuffing box packing leak (MNT-0107-028); Annual flowline integrity test (MNT-0107-029)
- WELL-0138 why: Prime mover failure (MNT-0138-031); Prime mover failure (MNT-0138-032); Gearbox oil leak (MNT-0138-034)

*Visual:* bar · *Citations:* INS-0121-0189, INS-0121-0200, INS-0121-0201, INS-0121-0202, INS-0121-0203, INS-0121-0205, INS-0121-0206, INS-0107-0194, INS-0107-0195, INS-0107-0196, INS-0107-0197, INS-0107-0198, INS-0107-0199, INS-0138-0195, INS-0138-0196, INS-0138-0200, INS-0138-0201, INS-0138-0206, INS-0138-0207, Dataset Guide (downtime = 7 d per non-producing inspection)

*Check:* PASS   

## Q11 — Michael Turner
**Q:** For the three wells we discussed yesterday, what have repairs cost this year?

From your earlier conversation (2026-10-18T06:23: "Which 3 wells in Northeast Block 7 had the most downtime in the last 4 months? Show a bar chart.") the wells were WELL-0121, WELL-0107, WELL-0138. **Repair costs in 2026:** WELL-0121: USD 25,794 (7 jobs) · WELL-0107: USD 5,176 (6 jobs) · WELL-0138: USD 46,942 (10 jobs)

*Visual:* bar · *Citations:* MNT-0121-029, MNT-0121-030, MNT-0121-031, MNT-0121-032, MNT-0121-033, MNT-0121-034, MNT-0121-035, MNT-0107-025, MNT-0107-026, MNT-0107-027, MNT-0107-028, MNT-0107-029, MNT-0107-030, MNT-0138-026, MNT-0138-027, MNT-0138-028, MNT-0138-029, MNT-0138-030, MNT-0138-031, MNT-0138-032, MNT-0138-033, MNT-0138-034, MNT-0138-035

*Check:* PASS   

## Q12 — Michael Turner
**Q:** The 15 Oct reading for WELL-0164 is wrong. The handheld thermal gun used in that inspection was faulty; the field crew re-measured the wellhead at 41.0 °C.

Recorded: **INS-0164-0205** (15 Oct 2026) wellhead_temp_c corrected from 24.0 to 41.0 by Michael Turner. The original value is kept; the correction applies to every later answer for every user.

With 41.0 °C against 19.9 °C air (21.1 °C warmer, above the T200 limit of 15 °C), WELL-0164 is **producing oil**.

⚠ Conflict: the same inspection has the note "Pump jack not moving." by Tyler Hughes, which disagrees with the corrected reading. Michael Turner, can you confirm?

*Visual:* None · *Citations:* INS-0164-0205

*Check:* PASS   

## Q12b — Michael Turner
**Q:** Which wells in Northeast Block 8 are not producing oil right now, and why? Show them in a table.

**3 wells in Northeast Block 8 are not producing oil right now** (latest inspection per well): WELL-0170, WELL-0172, WELL-0175.

WELL-0164 is no longer listed: its INS-0164-0205 wellhead reading was corrected by Michael Turner from 24.0 to 41.0 °C (The 15 Oct reading for WELL-0164 is wrong. The handheld thermal gun used in that inspection was faulty; the field crew re-measured the wellhead at 41.0 °C.), so it now counts as producing.

*Visual:* table · *Citations:* INS-0170-0206, INS-0172-0206, INS-0175-0204, T200/T350 manual production rule

*Check:* PASS   

## Q13 — Michael Turner
**Q:** The AI estimated the 24 Sep spill at WELL-0151 as 4.5 bbl. The field crew measured 5.4 bbl.

Recorded: **INS-0151-0201** (24 Sep 2026) spill_est_volume_bbl corrected from 4.5 to 5.4 by Michael Turner. The original value is kept; the correction applies to every later answer for every user.

At 5.4 bbl the spill is **reportable** under the Spill Response SOP.

- SR-01: no written notice on record; was due by 25 Sep 2026 15:30 UTC, 24 h after discovery at the 24 Sep 2026 15:30 inspection — possible breach

- SR-02: contained after about 6.4 h vs 4 h limit (report MNT-0151-025) — possible breach

- SR-03: agency clean-up verification due by 23 Nov 2026, none recorded

- note: report MNT-0151-025 classed the spill as moderate based on the old estimate (4.5 bbl); that no longer holds

*Visual:* None · *Citations:* INS-0151-0201, INS-0151-0201, MNT-0151-025, Spill Response SOP

*Check:* PASS   

## Q14a — Michael Turner
**Q:** Which wells in Northeast Block 7 need a root-cause analysis on their pump jack?

**3 wells need a root-cause analysis on their pump jack:** WELL-0108 (3 repairs, T350), WELL-0121 (3 repairs, T200), WELL-0138 (3 repairs, T350). Rule: T200 manual §10 (≥3 corrective repairs on the same equipment in 12 months; the T350 manual refers to it).

*Visual:* table · *Citations:* MNT-0108-024, MNT-0108-026, MNT-0108-028, MNT-0121-031, MNT-0121-034, MNT-0121-035, MNT-0138-031, MNT-0138-032, MNT-0138-034, T200 manual §10, T350 manual §6

*Check:* PASS   

## Q14b — Michael Turner
**Q:** Note for all T350 wells: our team now wants a pump jack root-cause analysis after 2 repairs, not 3.

Recorded a team rule for **all T350 wells only**: root-cause analysis after 2 corrective repairs (manual: 3, T350 manual (maintenance escalation, RCA)). Set by Michael Turner; it applies to every user's later answers, and not to other well types.

*Visual:* None · *Citations:* T350 manual (maintenance escalation, RCA)

*Check:* PASS   

## Q14 — Michael Turner
**Q:** Which wells in Northeast Block 7 need a root-cause analysis on their pump jack?

**4 wells need a root-cause analysis on their pump jack:** WELL-0108 (3 repairs, T350), WELL-0120 (2 repairs, T350), WELL-0121 (3 repairs, T200), WELL-0138 (3 repairs, T350). Rule: T200 manual §10 (≥3 corrective repairs on the same equipment in 12 months; the T350 manual refers to it).

For T350 wells I applied a rule from Michael Turner (2026-10-19), overrides manual, not the manual.

*Visual:* table · *Citations:* MNT-0108-024, MNT-0108-026, MNT-0108-028, MNT-0120-025, MNT-0120-030, MNT-0121-031, MNT-0121-034, MNT-0121-035, MNT-0138-031, MNT-0138-032, MNT-0138-034, T200 manual §10, T350 manual §6

*Check:* PASS   

## Q15a — Jessica Reed
**Q:** Is WELL-0164 producing oil right now?

**WELL-0164 is producing oil** (as of its latest inspection).

Latest inspection INS-0164-0205 on 15 Oct 2026, by manual, by Tyler Hughes. Wellhead 41.0 °C vs air 19.9 °C: 21.1 °C warmer, at/above the T200 limit of 15 °C.

⚠ This reading was corrected by Michael Turner: wellhead_temp_c 24.0 → 41.0 (The 15 Oct reading for WELL-0164 is wrong. The handheld thermal gun used in that inspection was faulty; the field crew re-measured the wellhead at 41.0 °C.). Original kept for reference.

Inspector note on that inspection: "Pump jack not moving." — this disagrees with the corrected reading; please confirm.

*Visual:* card · *Citations:* INS-0164-0205, T200 manual, memory_corrections#1

*Check:* PASS   

## Q15b — Laura Simmons
**Q:** Which spills in Northeast Block 8 in the last 90 days needed a report to the regulator?

**1 spill(s) in Northeast Block 8 in the last 90 days reached the 5 bbl reporting threshold (Spill Response SOP SR-01):**
- WELL-0151: 5.4 bbl on 24 Sep 2026 (INS-0151-0201), volume corrected by Michael Turner from 4.5. SR-01: no written notice on record; was due by 25 Sep 2026 15:30 UTC, 24 h after discovery at the 24 Sep 2026 15:30 inspection. SR-03: agency clean-up verification due by 23 Nov 2026, none recorded.
No other spill in that period reached the threshold.

*Visual:* table · *Citations:* INS-0151-0201, Spill Response SOP SR-01, INS-0151-0201, MNT-0151-025

*Check:* PASS   

## Q16a — Jake Morales
**Q:** FYI for everyone: WELL-0007 will be shut in from 17 Oct for a 10-day planned workover.

Noted for everyone: "FYI for everyone: WELL-0007 will be shut in from 17 Oct for a 10-day planned workover." — recorded as shared knowledge about WELL-0007 from Jake Morales (planned (future)).

*Visual:* None · *Citations:* INS-0007-0203

*Check:* PASS   

## Q16b — Michael Turner
**Q:** Is any downtime planned for WELL-0007?

**Yes, downtime is planned for WELL-0007:**
- FYI for everyone: WELL-0007 will be shut in from 17 Oct for a 10-day planned workover. — according to Jake Morales (2026-10-19, shared note)

*Visual:* None · *Citations:* memory_well_facts#1

*Check:* PASS   

## Q16c — Jessica Reed
**Q:** For the three wells we discussed yesterday, what have repairs cost this year?

I have no earlier conversation with Jessica Reed that mentions wells, so I can't tell which wells you mean. (Private memory is per user; I don't use other users' chats.) Which wells do you mean?

*Visual:* None · *Citations:* 

*Check:* PASS   

## Q17a — Michael Turner
**Q:** WELL-0175 has been shut in for planned work since 14 Oct.

Noted for everyone: "WELL-0175 has been shut in for planned work since 14 Oct." — recorded as shared knowledge about WELL-0175 from Michael Turner (confirmed by data).

*Visual:* None · *Citations:* INS-0175-0204

*Check:* PASS   

## Q17b — Tyler Hughes
**Q:** WELL-0175 is running fine.

Noted for everyone: "WELL-0175 is running fine." — recorded as shared knowledge about WELL-0175 from Tyler Hughes (unconfirmed (contradicts data)).

⚠ **This contradicts the data**: the latest inspection INS-0175-0204 (15 Oct 2026, by Jessica Reed) shows the wellhead only 0.4 °C above air, so not producing.

That matches Michael Turner's note ("WELL-0175 has been shut in for planned work since 14 Oct."), not your claim.

I've kept both statements on record and marked yours as **unconfirmed**. Can you confirm, Tyler Hughes?

*Visual:* None · *Citations:* INS-0175-0204

*Check:* PASS   

## Q17c — Jake Morales
**Q:** WELL-0001 is back online since 14 Oct.

Noted for everyone: "WELL-0001 is back online since 14 Oct." — recorded as shared knowledge about WELL-0001 from Jake Morales (unconfirmed (contradicts data)).

⚠ **This contradicts the data**: the latest inspection INS-0001-0203 (15 Oct 2026, by Ryan Brooks) shows the wellhead only 3.2 °C above air, so not producing.

Also on record: Note CTX-0001-003 by Jake Morales: Well shut in from 7 Oct for planned rod string replacement. Work order not yet in the maintenance system. Expected back online around 20 Oct.

I've kept both statements on record and marked yours as **unconfirmed**. Can you confirm, Jake Morales?

*Visual:* None · *Citations:* INS-0001-0203

*Check:* PASS   

## Q18 — Laura Simmons
**Q:** Was the 20 Aug spill at WELL-0101 real oil?

**Yes** — the AI flagged a 1.0 bbl spill at INS-0101-0197 on 20 Aug 2026 ("Oil sheen around cellar."). Notes on it:
- Ryan Brooks (CTX-0101-002, operator_feedback): "Inspection INS-0101-0197: I think this was only produced water, not crude."
- Chris Dalton (CTX-0101-003, operator_feedback): "Inspection INS-0101-0197: sampled the stain, it is crude oil. The detection stands."

These notes **disagree**. Neither is a formal correction, and a spill repair (MNT-0101-029) was done, so the detection stands.

*Visual:* table · *Citations:* INS-0101-0197, CTX-0101-002, CTX-0101-003, MNT-0101-029

*Check:* PASS   

