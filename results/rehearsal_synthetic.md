# Copilot answers (_final_questions.json)

## F1 — Michael Turner
**Q:** Is WELL-0201 producing oil right now? When was it last inspected, and by whom?

**WELL-0201 is not producing oil** (as of its latest inspection).

Latest inspection INS-0201-0203 on 15 Oct 2026, by drone, by Ryan Brooks. Wellhead 25.6 °C vs air 22.4 °C: 3.2 °C warmer, below the T200 limit of 15 °C.

Inspector note on that inspection: "Pump jack not moving."

Reason: Note CTX-0201-003 by Jake Morales: Well shut in from 7 Oct for planned rod string replacement. Work order not yet in the maintenance system. Expected back online around 20 Oct.

The recorded status still says **active**, which is out of date.

*Visual:* card · *Citations:* INS-0201-0203, T200 manual, CTX-0201-003

## F2 — Michael Turner
**Q:** Which 3 wells in Southeast Block 41 had the most downtime in the last 4 months? Show a bar chart.

**Top 3 wells in Southeast Block 41 by downtime (16 Jun 2026 to 16 Oct 2026):** WELL-0321: 49 days (T200), WELL-0307: 42 days (T350), WELL-0338: 42 days (T350). Next is WELL-0319 at 28.
- WELL-0321 why: Gearbox oil leak (MNT-0321-031); Scheduled wellhead valve service (MNT-0321-033); Prime mover failure (MNT-0321-034); Prime mover failure (MNT-0321-034)
- WELL-0307 why: Stuffing box packing leak (MNT-0307-028); Stuffing box packing leak (MNT-0307-028); Annual flowline integrity test (MNT-0307-029)
- WELL-0338 why: Prime mover failure (MNT-0338-031); Prime mover failure (MNT-0338-032); Gearbox oil leak (MNT-0338-034)

*Visual:* bar · *Citations:* INS-0321-0189, INS-0321-0200, INS-0321-0201, INS-0321-0202, INS-0321-0203, INS-0321-0205, INS-0321-0206, INS-0307-0194, INS-0307-0195, INS-0307-0196, INS-0307-0197, INS-0307-0198, INS-0307-0199, INS-0338-0195, INS-0338-0196, INS-0338-0200, INS-0338-0201, INS-0338-0206, INS-0338-0207, Dataset Guide (downtime = 7 d per non-producing inspection)

## F3 — Michael Turner
**Q:** Show a heatmap of 2026 spills by geographic area and month.

Real spills in 2026 by area and month (corrected detections removed). Totals: Southwest Block 23: 35, Southwest Block 24: 43, Northeast Block 7: 37, Northeast Block 8: 26, Northwest Block 31: 35, Northwest Block 32: 43, Southeast Block 41: 37, Southeast Block 42: 26

*Visual:* heatmap · *Citations:* inspections (spill_detected, corrections applied), context.jsonl correction notes

## F4 — Michael Turner
**Q:** Which rules has WELL-0201 broken in the last 12 months, and what is still open?

**WELL-0201: 4 rule breach(es) in the last 12 months**, USD 5,000 in fines still open.
- **SR-01** (11 Jun 2026 (6.8 bbl, INS-0201-0185)): written notice after 41 h vs 24 h limit (REG-0201-001)
- **SR-03** (11 Jun 2026 (6.8 bbl, INS-0201-0185)): agency clean-up verification due by 10 Aug 2026, still open (REG-0201-003)
- **RC-04** (11 Jun 2026 (6.8 bbl, INS-0201-0185)): response to REG-0201-002 was due by 30 Jul 2026; none recorded
- **SR-02** (11 Jun 2026 (6.8 bbl, INS-0201-0185)): contained after about 7 h vs 4 h limit (report MNT-0201-029)

**Still open / pending:**
- SR-01 (11 Jun 2026 (6.8 bbl, INS-0201-0185)): notice of violation REG-0201-002, fine USD 5,000, still open
- RCA: root-cause analysis due on flowline: 3 corrective repairs in 12 months (MNT-0201-028, MNT-0201-029, MNT-0201-032)
- Manual §4: planned shut-in not yet recorded in the maintenance system, which the manual requires before work starts (CTX-0201-003)

**Met:**
- SR-02 (1 Oct 2026 (1.6 bbl, INS-0201-0201)): contained after about 1.7 h vs 4 h limit (report MNT-0201-032)
- RC-02: annual flowline integrity test done 7 Mar 2026 (MNT-0201-026)

*Visual:* table · *Citations:* INS-0201-0185, REG-0201-001, REG-0201-002, REG-0201-003, MNT-0201-029, INS-0201-0201, MNT-0201-032, MNT-0201-028, MNT-0201-026, CTX-0201-003, Spill Response SOP, Regulatory Compliance SOP

## F5 — Michael Turner
**Q:** In Northwest Block 32, which spills in the last 90 days were not contained within the SOP time limit?

**2 spills in Northwest Block 32 were not contained within the 4-hour SOP limit (SR-02):** WELL-0282 after about 7.1 h (report MNT-0282-028, inspection INS-0282-0198); WELL-0300 after about 8.1 h (report MNT-0300-034, inspection INS-0300-0196). Containment times come from the free-text repair reports.

*Visual:* table · *Citations:* MNT-0282-028, MNT-0300-034, INS-0282-0198, INS-0300-0196, Spill Response SOP SR-02

## F6 — Michael Turner
**Q:** Show on a map every well in Southeast Block 42 with a real spill in the last 90 days.

**4 real spills for Southeast Block 42 (19 Jul 2026 to 16 Oct 2026), 10.2 barrels in total.** 6 detections; excluded as corrected: INS-0394-0192 (23 Jul 2026, CTX-0394-002), INS-0399-0200 (10 Sep 2026, CTX-0399-002). 4 wells: WELL-0351 (24 Sep 2026, 4.5 bbl, 32.62246, -102.18445); WELL-0365 (30 Jul 2026, 1.2 bbl, 32.65665, -102.14522); WELL-0375 (30 Jul 2026, 3.9 bbl, 32.6802, -102.1479); WELL-0386 (23 Jul 2026, 0.6 bbl, 32.67552, -102.17775)

*Visual:* map · *Citations:* INS-0351-0201, INS-0365-0194, INS-0375-0193, INS-0386-0097, CTX-0394-002, CTX-0399-002, Dataset Guide: correction notes override detections

## F7 — Michael Turner
**Q:** Which 3 wells in Northeast Block 7 had the most downtime in the last 4 months? Show a bar chart.

**Top 3 wells in Northeast Block 7 by downtime (16 Jun 2026 to 16 Oct 2026):** WELL-0121: 49 days (T200), WELL-0107: 42 days (T350), WELL-0138: 42 days (T350). Next is WELL-0119 at 28.
- WELL-0121 why: Gearbox oil leak (MNT-0121-031); Scheduled wellhead valve service (MNT-0121-033); Prime mover failure (MNT-0121-034); Prime mover failure (MNT-0121-034)
- WELL-0107 why: Stuffing box packing leak (MNT-0107-028); Stuffing box packing leak (MNT-0107-028); Annual flowline integrity test (MNT-0107-029)
- WELL-0138 why: Prime mover failure (MNT-0138-031); Prime mover failure (MNT-0138-032); Gearbox oil leak (MNT-0138-034)

*Visual:* bar · *Citations:* INS-0121-0189, INS-0121-0200, INS-0121-0201, INS-0121-0202, INS-0121-0203, INS-0121-0205, INS-0121-0206, INS-0107-0194, INS-0107-0195, INS-0107-0196, INS-0107-0197, INS-0107-0198, INS-0107-0199, INS-0138-0195, INS-0138-0196, INS-0138-0200, INS-0138-0201, INS-0138-0206, INS-0138-0207, Dataset Guide (downtime = 7 d per non-producing inspection)

