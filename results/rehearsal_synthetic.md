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
**Q:** Which wells in Southeast Block 42 are not producing oil right now, and why? Show them in a table.

**4 wells in Southeast Block 42 are not producing oil right now** (latest inspection per well): WELL-0364, WELL-0370, WELL-0372, WELL-0375.

*Visual:* table · *Citations:* INS-0364-0205, INS-0370-0206, INS-0372-0206, INS-0375-0204, T200/T350 manual production rule

## F3 — Michael Turner
**Q:** Show a line chart of WELL-0321's wellhead temperature against air temperature for the last 13 weeks.

13 readings for WELL-0321 (23 Jul 2026 to 15 Oct 2026). Not producing oil on: 3 Sep 2026, 10 Sep 2026, 17 Sep 2026, 24 Sep 2026, 8 Oct 2026, 15 Oct 2026 (wellhead less than 15 °C above air).

*Visual:* line · *Citations:* INS-0321-0194 … INS-0321-0206

## F4 — Michael Turner
**Q:** How many oil spills has WELL-0282 had in the last 4 years, and how much oil in total? List them in a table.

**3 real spills for WELL-0282 (16 Oct 2022 to 16 Oct 2026), 2.9 barrels in total.**

*Visual:* table · *Citations:* INS-0282-0083, INS-0282-0167, INS-0282-0198, Dataset Guide: correction notes override detections

## F5 — Michael Turner
**Q:** How many days was WELL-0205 down in 2025?

**WELL-0205 was down 42 days** (1 Jan 2025–31 Dec 2025), from 6 weekly inspections where it was not producing oil:
- 27 Mar 2025 (INS-0205-0126): wellhead 17.0 °C vs air 13.7 °C, only 3.3 °C warmer. Cause: Flowline corrosion pinhole leak (MNT-0205-020).
- 3 Apr 2025 (INS-0205-0127): wellhead 25.4 °C vs air 15.2 °C, only 10.2 °C warmer. Cause: Flowline corrosion pinhole leak (MNT-0205-020).
- 10 Apr 2025 (INS-0205-0128): wellhead 32.3 °C vs air 22.2 °C, only 10.1 °C warmer. Cause: Flowline corrosion pinhole leak (MNT-0205-020).
- 17 Apr 2025 (INS-0205-0129): wellhead 26.5 °C vs air 18.6 °C, only 7.9 °C warmer. Cause: Flowline corrosion pinhole leak (MNT-0205-020).
- 24 Apr 2025 (INS-0205-0130): wellhead 28.5 °C vs air 26.2 °C, only 2.3 °C warmer. Cause: Flowline corrosion pinhole leak (MNT-0205-020); Walking beam bearing wear (MNT-0205-021).
- 1 May 2025 (INS-0205-0131): wellhead 30.8 °C vs air 28.0 °C, only 2.8 °C warmer. Cause: Walking beam bearing wear (MNT-0205-021).

Downtime = 7 days per non-producing weekly inspection (Dataset Guide).

*Visual:* None · *Citations:* INS-0205-0126, INS-0205-0127, INS-0205-0128, INS-0205-0129, INS-0205-0130, INS-0205-0131, Dataset Guide (downtime), well-type manual

## F6 — Michael Turner
**Q:** Which 3 wells in Northwest Block 32 had the most downtime in the last 4 months? Show a bar chart.

**Top 3 wells in Northwest Block 32 by downtime (16 Jun 2026 to 16 Oct 2026):** WELL-0284: 42 days (T200), WELL-0269: 35 days (T200), WELL-0261: 28 days (T200). Next is WELL-0271 at 28.
- WELL-0284 why: Separator level controller fault (MNT-0284-031); Gearbox oil leak (MNT-0284-032)
- WELL-0269 why: Prime mover failure (MNT-0269-034); Prime mover failure (MNT-0269-034); Downhole pump stuck (MNT-0269-035); Downhole pump stuck (MNT-0269-035)
- WELL-0261 why: Sucker rod parted (MNT-0261-028); Sucker rod parted (MNT-0261-028); Scheduled lubrication and belt inspection (MNT-0261-029)

*Visual:* bar · *Citations:* INS-0284-0199, INS-0284-0200, INS-0284-0201, INS-0284-0203, INS-0284-0204, INS-0284-0205, INS-0269-0187, INS-0269-0188, INS-0269-0189, INS-0269-0190, INS-0269-0191, INS-0261-0202, INS-0261-0203, INS-0261-0204, INS-0261-0205, Dataset Guide (downtime = 7 d per non-producing inspection)

## F7 — Michael Turner
**Q:** Show on a map every well in Southeast Block 41 with a real spill in the last 90 days.

**10 real spills for Southeast Block 41 (19 Jul 2026 to 16 Oct 2026), 14.6 barrels in total.** 13 detections; excluded as corrected: INS-0307-0201 (20 Aug 2026, CTX-0307-002), INS-0320-0202 (10 Sep 2026, CTX-0320-001), INS-0322-0201 (10 Sep 2026, CTX-0322-002). 9 wells: WELL-0301 (20 Aug 2026, 1.0 bbl, 32.62969, -102.22385); WELL-0323 (24 Sep 2026, 6.0 bbl, 32.61597, -102.17947); WELL-0328 (10 Sep 2026, 1.0 bbl, 32.60752, -102.17395); WELL-0332 (6 Aug 2026, 0.8 bbl, 32.59385, -102.17676); WELL-0333 (20 Aug 2026, 1.0 bbl, 32.61644, -102.20567); WELL-0338 (15 Oct 2026, 1.6 bbl, 32.61961, -102.22191); WELL-0341 (3 Sep 2026, 0.9 bbl, 32.61475, -102.20487); WELL-0345 (30 Jul 2026, 0.4 bbl, 32.58642, -102.21354); WELL-0349 (17 Sep 2026, 0.2 bbl, 32.62487, -102.21263)

*Visual:* map · *Citations:* INS-0301-0197, INS-0323-0093, INS-0328-0198, INS-0332-0197, INS-0333-0198, INS-0338-0208, INS-0341-0195, INS-0341-0198, INS-0345-0189, INS-0349-0204, CTX-0307-002, CTX-0320-001, CTX-0322-002, Dataset Guide: correction notes override detections

## F8 — Michael Turner
**Q:** Show a heatmap of 2026 spills by geographic area and month.

Real spills in 2026 by area and month (corrected detections removed). Totals: Southwest Block 23: 35, Southwest Block 24: 43, Northeast Block 7: 37, Northeast Block 8: 26, Northwest Block 31: 35, Northwest Block 32: 43, Southeast Block 41: 37, Southeast Block 42: 26

*Visual:* heatmap · *Citations:* inspections (spill_detected, corrections applied), context.jsonl correction notes

## F9 — Michael Turner
**Q:** Which rules has WELL-0213 broken in the last 12 months, and what is still open?

**WELL-0213: 4 rule breach(es) in the last 12 months**.
- **SR-02** (1 Jan 2026 (3.4 bbl, INS-0213-0165)): contained after about 5.7 h vs 4 h limit (report MNT-0213-026)
- **SR-02** (26 Mar 2026 (2.3 bbl, INS-0213-0177)): contained after about 5 h vs 4 h limit (report MNT-0213-029)
- **SR-01** (11 Jun 2026 (5.2 bbl, INS-0213-0188)): written notice after 48 h vs 24 h limit (REG-0213-001)
- **SR-03** (11 Jun 2026 (5.2 bbl, INS-0213-0188)): agency clean-up verification due by 10 Aug 2026, still open (REG-0213-004)

**Still open / pending:**
- RCA: root-cause analysis due on flowline: 5 corrective repairs in 12 months (MNT-0213-025, MNT-0213-026, MNT-0213-029, MNT-0213-031, MNT-0213-033)

**Met:**
- SR-02: contained after about 2.7 h vs 4 h limit (report MNT-0213-025)
- SR-02: contained after about 1.2 h vs 4 h limit (report MNT-0213-031)
- SR-02: contained after about 1.5 h vs 4 h limit (report MNT-0213-033)
- RC-02: annual flowline integrity test done 7 Mar 2026 (MNT-0213-028)

*Visual:* table · *Citations:* INS-0213-0163, MNT-0213-025, INS-0213-0165, MNT-0213-026, INS-0213-0177, MNT-0213-029, INS-0213-0183, MNT-0213-031, INS-0213-0188, REG-0213-001, REG-0213-002, REG-0213-003, REG-0213-004, MNT-0213-033, MNT-0213-028, Spill Response SOP, Regulatory Compliance SOP

## F10 — Michael Turner
**Q:** In Northwest Block 31, which spills in the last 90 days were not contained within the SOP time limit?

**4 spills in Northwest Block 31 were not contained within the 4-hour SOP limit (SR-02):** WELL-0217 after about 4.9 h (report MNT-0217-029, inspection INS-0217-0198); WELL-0230 after about 7.3 h (report MNT-0230-032, inspection INS-0230-0192); WELL-0242 after about 7.5 h (report MNT-0242-026, inspection INS-0242-0204); WELL-0244 after about 7.9 h (report MNT-0244-036, inspection INS-0244-0197). Containment times come from the free-text repair reports.

*Visual:* table · *Citations:* MNT-0217-029, MNT-0230-032, MNT-0242-026, MNT-0244-036, INS-0217-0198, INS-0230-0192, INS-0242-0204, INS-0244-0197, Spill Response SOP SR-02

## F11 — Michael Turner
**Q:** Which area lost the most production days in 2025?

**Downtime — the whole field, 2025: 8120 days in total**

**Highest: Northwest Block 32 (1449 days)**

- Northwest Block 32: 1449 days
- Southwest Block 24: 1449 days
- Northeast Block 7: 966 days
- Southeast Block 41: 966 days
- Northwest Block 31: 889 days
- Southwest Block 23: 889 days
- Northeast Block 8: 756 days
- Southeast Block 42: 756 days

_Rules applied: T200: producing when wellhead − air ≥ 15 °C (T200 manual); T350: producing when wellhead − air ≥ 20 °C (T350 manual); Downtime = 7 days per non-producing weekly inspection (Dataset Guide)._

*Visual:* bar · *Citations:* INS-0251-0117, INS-0251-0118, INS-0251-0119, INS-0251-0123, INS-0251-0128, INS-0251-0129, INS-0252-0145, INS-0252-0146, INS-0252-0147, INS-0252-0150, INS-0252-0151, INS-0253-0127, INS-0253-0128, INS-0253-0129, INS-0253-0130, INS-0253-0131, INS-0253-0132, INS-0253-0139, INS-0253-0140, INS-0253-0152, INS-0253-0153, INS-0255-0146, INS-0255-0147, INS-0255-0157, INS-0255-0158

## F12 — Michael Turner
**Q:** What fines are still open across the field?

**Regulator fines — the whole field (open=True): USD 15,000 in total**

- REG-0001-002 (WELL-0001, 30 Jun 2026): notice of violation, SR-01, fine USD 5,000, open
- REG-0160-002 (WELL-0160, 5 May 2023): notice of violation, SR-01, fine USD 2,500, open
- REG-0201-002 (WELL-0201, 30 Jun 2026): notice of violation, SR-01, fine USD 5,000, open
- REG-0360-002 (WELL-0360, 5 May 2023): notice of violation, SR-01, fine USD 2,500, open

*Visual:* table · *Citations:* REG-0001-002, REG-0160-002, REG-0201-002, REG-0360-002

## F13 — Jessica Reed
**Q:** Is WELL-0364 producing oil right now?

**WELL-0364 is not producing oil** (as of its latest inspection).

Latest inspection INS-0364-0205 on 15 Oct 2026, by manual, by Tyler Hughes. Wellhead 24.0 °C vs air 19.9 °C: 4.1 °C warmer, below the T200 limit of 15 °C.

Inspector note on that inspection: "Pump jack not moving."

Reason: no recorded reason in repairs or notes. Suggest a site check.

The recorded status still says **active**, which is out of date.

*Visual:* card · *Citations:* INS-0364-0205, T200 manual

## F14 — Michael Turner
**Q:** The 15 Oct reading for WELL-0364 is wrong. The field crew re-measured the wellhead at 41.0 °C.

Recorded: **INS-0364-0205** (15 Oct 2026) wellhead_temp_c corrected from 24.0 to 41.0 by Michael Turner. The original value is kept; the correction applies to every later answer for every user.

With 41.0 °C against 19.9 °C air (21.1 °C warmer, above the T200 limit of 15 °C), WELL-0364 is **producing oil**.

⚠ Conflict: the same inspection has the note "Pump jack not moving." by Tyler Hughes, which disagrees with the corrected reading. Michael Turner, can you confirm?

*Visual:* None · *Citations:* INS-0364-0205

## F15 — Jessica Reed
**Q:** Is WELL-0364 producing oil right now?

**WELL-0364 is producing oil** (as of its latest inspection).

Latest inspection INS-0364-0205 on 15 Oct 2026, by manual, by Tyler Hughes. Wellhead 41.0 °C vs air 19.9 °C: 21.1 °C warmer, at/above the T200 limit of 15 °C.

⚠ This reading was corrected by Michael Turner: wellhead_temp_c 24.0 → 41.0 (The 15 Oct reading for WELL-0364 is wrong. The field crew re-measured the wellhead at 41.0 °C.). Original kept for reference.

Inspector note on that inspection: "Pump jack not moving." — this disagrees with the corrected reading; please confirm.

*Visual:* card · *Citations:* INS-0364-0205, T200 manual, memory_corrections#1

