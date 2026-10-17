# Copilot answers (final_questions.json)

## Q1 — Michael Turner
**Q:** All our wells feed one reservoir. Map the reservoir pressure across the field from the pressure data.

Real spills in 2027 by area and month (corrected detections removed). Totals: Southwest Block 23: 4, Southwest Block 24: 3, Northeast Block 7: 2, Northeast Block 8: 3, Southeast Block 31: 1, Northwest Block 12: 7, Southeast Block 32: 4

*Visual:* heatmap · *Citations:* inspections (spill_detected, corrections applied), context.jsonl correction notes

## Q2 — Robert Hayes
**Q:** Which well produced the most oil in 2026?

I couldn't map this to a data tool. Relevant passages from the manuals/SOPs:

**fleet/sops/regulator-letter-2026-11-20.md**: # Letter from the State Oil & Gas Commission

> Fictional letter for the FlytBase Asset Copilot hackathon.

**From:** State Oil & Gas Commission, District Office
**To:** Northeast Production (TEAM-NE), attention Michael Turner, production supervisor
**Date:** 20 Nov 2026
**Subject:** Soil sampling after reportable spills in Northeast Block 7 and Northeast Block 8

Our review of recent spill reports from your Northeast Block 7 and Northeast Block 8 leases found
clean-up files without laboratory soil results.

For every reportable spill in Northeast Block 7 or Northeast Block 8 since 1 Jun 2026,

**fleet/sops/moc-2026-044.md**: ## Change

This memo extends MOC-2026-031. The replacement check valves are still on back-order, so the
temporary flowline bypass stays authorized on every well named in MOC-2026-031:
WELL-0013, WELL-0062, WELL-0118, WELL-0248, WELL-0476.

The new expiry date below replaces the expiry date in MOC-2026-031. All other conditions of
MOC-2026-031 stay the same. MOC-2026-036 is not changed by this memo.

This approval expires on 28 Feb 2027.

**fleet/sops/operations-sop-rev2.md**: ## OPS-3 Status evidence precedence

A well's current status comes from the most recent of these two:
- its latest inspection reading (producing oil or not producing oil, by the well-type manual,
  after any `data_correction` note), or
- its latest operator note saying the well was shut in or restarted.

If a shut-in note is more recent than the latest inspection, the well is **not producing (shut
in)**, even if that inspection reads as producing. If a restart note is more recent than the latest
inspection, the well is **producing (unconfirmed)** until an inspection confirms it. Other operator

*Visual:* None · *Citations:* fleet/sops/regulator-letter-2026-11-20.md, fleet/sops/moc-2026-044.md, fleet/sops/operations-sop-rev2.md

## Q3 — Laura Simmons
**Q:** Since 1 Nov 2026, every time an operator note reports gas at a well, did we get someone out to that well in time under our operating procedures? List every report and whether the response met the deadline.

**Human notes — the whole field, 1 Nov 2026 to 14 Jan 2027 (event type=notice_of_violation): 1277 in total**

- WELL-0135: 9
- WELL-0217: 8
- WELL-0010: 7
- WELL-0039: 7
- WELL-0149: 7
- WELL-0175: 7
- WELL-0181: 7
- WELL-0182: 7
- WELL-0240: 7
- WELL-0270: 7
- WELL-0425: 7
- WELL-0013: 6
- WELL-0020: 6
- WELL-0058: 6
- WELL-0076: 6
- … 475 more

- CTX-0001-005 (WELL-0001, Ryan Brooks, operator_note): Checked WELL-0001 after the rain, pad dry and clean.
- CTX-0001-006 (WELL-0001, Ryan Brooks, operator_note): WELL-0001 tank gauged, level normal.
- CTX-0002-002 (WELL-0002, Ryan Brooks, operator_note): Walked the flowline at WELL-0002, nothing to report.
- CTX-0002-003 (WELL-0002, Sarah Mitchell, operator_note): WELL-0002 pumping normally.
- CTX-0003-003 (WELL-0003, Sarah Mitchell, operator_note): WELL-0003 tank gauged, level normal.
- CTX-0003-004 (WELL-0003, Sarah Mitchell, operator_note): Checked WELL-0003 after the rain, pad dry and clean.
- CTX-0003-005 (WELL-0003, Jake Morales, operator_note): Walked the flowline at WELL-0003, nothing to report.
- CTX-0004-003 (WELL-0004, Ryan Brooks, operator_note): Rod squeal at WELL-0004 stuffing box, greased the polished rod.
- CTX-0005-003 (WELL-0005, Jake Morales, operator_note): WELL-0005 tank gauged, level normal.
- CTX-0005-004 (WELL-0005, Ryan Brooks, operator_note): Heard fluid pound on WELL-0005, unit still running.
- CTX-0005-005 (WELL-0005, Ryan Brooks, operator_note): WELL-0005 tagging bottom on the downstroke, adjust spacing next visit.
- CTX-0005-006 (WELL-0005, Ryan Brooks, operator_note): Rod squeal at WELL-0005 stuffing box, greased the polished rod.
- CTX-0006-003 (WELL-0006, Ryan Brooks, operator_note): WELL-0006 tank gauged, level normal.
- CTX-0006-004 (WELL-0006, Jake Morales, operator_note): Heard fluid pound on WELL-0006, unit still running.
- CTX-0006-005 (WELL-0006, Jake Morales, operator_note): WELL-0006 pumping normally.
- CTX-0007-002 (WELL-0007, Ryan Brooks, operator_note): Checked WELL-0007 after the rain, pad dry and clean.
- CTX-0007-003 (WELL-0007, Ryan Brooks, operator_note): Checked WELL-0007 after the rain, pad dry and clean.
- CTX-0007-004 (WELL-0007, Sarah Mitchell, operator_note): Shut-in WELL-0007 so the maintenance crew can start work.
- CTX-0007-005 (WELL-0007, Ryan Brooks, operator_note): Restarted WELL-0007, unit running smooth.
- CTX-0009-001 (WELL-0009, Ryan Brooks, operator_note): Checked WELL-0009 after the rain, pad dry and clean.

*Visual:* table · *Citations:* CTX-0135-003, CTX-0135-004, CTX-0135-005, CTX-0135-006, CTX-0135-007, CTX-0135-008, CTX-0135-009, CTX-0135-010, CTX-0135-011, CTX-0217-004, CTX-0217-005, CTX-0217-006, CTX-0217-007, CTX-0217-008, CTX-0217-009, CTX-0217-010, CTX-0217-011, CTX-0010-001, CTX-0010-002, CTX-0010-003, CTX-0010-004, CTX-0010-005, CTX-0010-006, CTX-0010-007, CTX-0039-003

## Q4 — Chris Dalton
**Q:** Across all areas, which temporary flowline bypasses are in place right now, and is each one allowed? Also list any bypass, past or present, that stayed in after its approval ran out or was never approved at all.

I couldn't map this to a data tool. Relevant passages from the manuals/SOPs:

**fleet/sops/operations-sop-rev2.md**: ## OPS-2 Temporary bypass

A temporary flowline bypass is allowed only on a well named in a management-of-change memo
(the `moc-*.md` files in `fleet/sops/`) that has not expired. A memo that extends an earlier memo
replaces its expiry date.

A bypass is in place from the operator note that puts it in until the operator note that takes it
out.
It is a violation if:
- the well is not named in any MOC, or
- the bypass is still in place after the expiry date (the end of that day), including a bypass that
  is still in place today.

**fleet/sops/field-work-sop.md**: ## 2. Background (industry references)

| Topic | What industry practice says | How this SOP uses it |
|---|---|---|
| Crew safety on well servicing | API RP 54 (*Occupational Safety and Health for Oil and Gas Well Drilling and Servicing Operations*) covers well servicing rigs and special services. Pre-job safety meetings (job safety analysis briefings) are standard practice in OSHA's oil and gas safety guidance. | WS-01 |
| Energy isolation | The federal lockout/tagout standard (OSHA 29 CFR 1910.147) lists oil and gas well drilling and servicing as outside its scope; the US Chemical Safety Bo

**fleet/well-types/T500.md**: ## 5. Early warning signs

An ESP runs at a steady speed, so a healthy T500 wellhead stays within a degree or two of
its usual difference above air. ESP motors usually fail after running hot with too little
fluid over the pump. In the weeks before a failure, the wellhead-to-air difference typically
**falls steadily** while the well is still producing.

- If the wellhead-to-air difference is **lower than at the inspection before, three
  inspections in a row** (four readings, each lower than the last) **and has fallen by
  3 °C or more in total** over those four readings, schedule an ESP drive 

*Visual:* None · *Citations:* fleet/sops/operations-sop-rev2.md, fleet/sops/field-work-sop.md, fleet/well-types/T500.md

## Q5 — Michael Turner
**Q:** The State Oil & Gas Commission wrote to us in November 2026 about spills. Which of our spills does the letter cover, and on which ones are we not compliant? Show me a table.

**Real spills — the whole field, November 2026: 48 in total**

**Highest: WELL-0035 (1)**

- WELL-0035: 1
- WELL-0062: 1
- WELL-0077: 1
- WELL-0113: 1
- WELL-0114: 1
- WELL-0117: 1
- WELL-0119: 1
- WELL-0134: 1
- WELL-0138: 1
- WELL-0143: 1
- WELL-0151: 1
- WELL-0169: 1
- WELL-0181: 1
- WELL-0189: 1
- WELL-0194: 1
- … 33 more

_Rules applied: Detections voided by correction notes are excluded; runtime corrections applied._

*Visual:* table · *Citations:* INS-0035-0210, INS-0062-0207, INS-0077-0204, INS-0113-0213, INS-0114-0210, INS-0117-0196, INS-0119-0209, INS-0134-0208, INS-0138-0211, INS-0143-0179, INS-0151-0209, INS-0169-0211, INS-0181-0212, INS-0189-0212, INS-0194-0209, INS-0200-0210, INS-0203-0213, INS-0225-0208, INS-0235-0212, INS-0240-0211, INS-0246-0126, INS-0253-0209, INS-0281-0207, INS-0287-0208, INS-0299-0210

## Q6 — Nathan Pierce
**Q:** Across the whole field, not just my area, for which wells do the latest inspection and the operator notes disagree about whether the well is producing oil? For each one, what is its real status right now, and why?

**46 wells not producing oil right now — the whole field.**

- WELL-0010: 17.5 °C above air at INS-0010-0219 (14 Jan 2027), recorded status active
- WELL-0026: 5.4 °C above air at INS-0026-0216 (14 Jan 2027), recorded status down
- WELL-0032: 7.4 °C above air at INS-0032-0219 (14 Jan 2027), recorded status active
- WELL-0033: 10.0 °C above air at INS-0033-0222 (14 Jan 2027), recorded status active
- WELL-0046: 2.1 °C above air at INS-0046-0220 (14 Jan 2027), recorded status down
- WELL-0053: 2.3 °C above air at INS-0053-0220 (14 Jan 2027), recorded status active
- WELL-0069: 4.8 °C above air at INS-0069-0217 (14 Jan 2027), recorded status active
- WELL-0093: 4.5 °C above air at INS-0093-0216 (14 Jan 2027), recorded status active
- WELL-0097: 6.5 °C above air at INS-0097-0215 (14 Jan 2027), recorded status active
- WELL-0105: 3.9 °C above air at INS-0105-0216 (14 Jan 2027), recorded status active
- WELL-0133: 4.0 °C above air at INS-0133-0219 (14 Jan 2027), recorded status active
- WELL-0134: 3.2 °C above air at INS-0134-0216 (14 Jan 2027), recorded status active
- WELL-0160: 3.8 °C above air at INS-0160-0217 (14 Jan 2027), recorded status active
- WELL-0167: 1.5 °C above air at INS-0167-0119 (14 Jan 2027), recorded status active
- WELL-0169: 5.2 °C above air at INS-0169-0219 (14 Jan 2027), recorded status active
- WELL-0175: 5.5 °C above air at INS-0175-0216 (14 Jan 2027), recorded status active
- WELL-0197: 1.2 °C above air at INS-0197-0214 (14 Jan 2027), recorded status down
- WELL-0199: 4.1 °C above air at INS-0199-0216 (31 Dec 2026), recorded status plugged
- WELL-0203: 22.4 °C above air at INS-0203-0221 (14 Jan 2027), recorded status active
- WELL-0213: 1.5 °C above air at INS-0213-0221 (14 Jan 2027), recorded status active
- WELL-0219: 4.5 °C above air at INS-0219-0171 (14 Jan 2027), recorded status active
- WELL-0249: 5.9 °C above air at INS-0249-0120 (14 Jan 2027), recorded status active
- WELL-0251: -0.4 °C above air at INS-0251-0215 (14 Jan 2027), recorded status active
- WELL-0263: 4.0 °C above air at INS-0263-0219 (14 Jan 2027), recorded status active
- WELL-0281: 10.2 °C above air at INS-0281-0214 (14 Jan 2027), recorded status down
- WELL-0309: 2.5 °C above air at INS-0309-0215 (14 Jan 2027), recorded status active
- WELL-0316: 1.0 °C above air at INS-0316-0217 (14 Jan 2027), recorded status active
- WELL-0330: 4.4 °C above air at INS-0330-0213 (14 Jan 2027), recorded status down
- WELL-0332: 0.5 °C above air at INS-0332-0217 (14 Jan 2027), recorded status active
- WELL-0373: 1.1 °C above air at INS-0373-0219 (14 Jan 2027), recorded status active
- WELL-0377: 0.4 °C above air at INS-0377-0220 (14 Jan 2027), recorded status active
- WELL-0397: 5.2 °C above air at INS-0397-0219 (14 Jan 2027), recorded status active
- WELL-0404: 1.8 °C above air at INS-0404-0214 (14 Jan 2027), recorded status down
- WELL-0408: 7.1 °C above air at INS-0408-0218 (14 Jan 2027), recorded status active
- WELL-0418: 8.2 °C above air at INS-0418-0219 (14 Jan 2027), recorded status active
- WELL-0429: 6.2 °C above air at INS-0429-0219 (14 Jan 2027), recorded status active
- WELL-0442: 2.5 °C above air at INS-0442-0220 (14 Jan 2027), recorded status active
- WELL-0452: 3.1 °C above air at INS-0452-0219 (14 Jan 2027), recorded status down
- WELL-0471: 1.8 °C above air at INS-0471-0219 (14 Jan 2027), recorded status active
- WELL-0490: 5.1 °C above air at INS-0490-0170 (14 Jan 2027), recorded status active

_Rules applied: T200: producing when wellhead − air ≥ 15 °C (T200 manual); T350: producing when wellhead − air ≥ 20 °C (T350 manual); T500: producing when wellhead − air ≥ 25 °C (T500 manual)._

*Visual:* table · *Citations:* INS-0010-0219, INS-0026-0216, INS-0032-0219, INS-0033-0222, INS-0046-0220, INS-0053-0220, INS-0069-0217, INS-0093-0216, INS-0097-0215, INS-0105-0216, INS-0133-0219, INS-0134-0216, INS-0160-0217, INS-0167-0119, INS-0169-0219, INS-0175-0216, INS-0197-0214, INS-0199-0216, INS-0203-0221, INS-0213-0221, INS-0219-0171, INS-0249-0120, INS-0251-0215, INS-0263-0219, INS-0281-0214

## Q7.1 — Robert Hayes
**Q:** Over the last month the operators have written notes about wells that sound or behave wrong. Which of those wells haven't had a repair since? Rank the 10 most likely to need a repair in the next 90 days, other than a spill clean-up, and quote the notes as evidence.

**Repair jobs — the whole field, last month (14 Dec 2026 to 14 Jan 2027): 386 in total**

**Highest: WELL-0031 (3)**

- WELL-0031: 3
- WELL-0046: 3
- WELL-0169: 3
- WELL-0235: 3
- WELL-0340: 3
- WELL-0379: 3
- WELL-0006: 2
- WELL-0026: 2
- WELL-0033: 2
- WELL-0036: 2
- WELL-0045: 2
- WELL-0047: 2
- WELL-0060: 2
- WELL-0062: 2
- WELL-0073: 2
- … 311 more

_Rules applied: A repair belongs to a period by its start date._

*Visual:* table · *Citations:* MNT-0031-031, MNT-0031-032, MNT-0031-033, MNT-0046-026, MNT-0046-027, MNT-0046-028, MNT-0169-026, MNT-0169-027, MNT-0169-028, MNT-0235-030, MNT-0235-031, MNT-0235-032, MNT-0340-037, MNT-0340-038, MNT-0340-039, MNT-0379-026, MNT-0379-027, MNT-0379-028, MNT-0006-030, MNT-0006-031, MNT-0026-033, MNT-0026-034, MNT-0033-032, MNT-0033-033, MNT-0036-027

## Q7.2 — Robert Hayes
**Q:** Which three would you send a crew to first this week, and why?

**46 wells not producing oil right now — the whole field.**

- WELL-0010: 17.5 °C above air at INS-0010-0219 (14 Jan 2027), recorded status active
- WELL-0026: 5.4 °C above air at INS-0026-0216 (14 Jan 2027), recorded status down
- WELL-0032: 7.4 °C above air at INS-0032-0219 (14 Jan 2027), recorded status active
- WELL-0033: 10.0 °C above air at INS-0033-0222 (14 Jan 2027), recorded status active
- WELL-0046: 2.1 °C above air at INS-0046-0220 (14 Jan 2027), recorded status down
- WELL-0053: 2.3 °C above air at INS-0053-0220 (14 Jan 2027), recorded status active
- WELL-0069: 4.8 °C above air at INS-0069-0217 (14 Jan 2027), recorded status active
- WELL-0093: 4.5 °C above air at INS-0093-0216 (14 Jan 2027), recorded status active
- WELL-0097: 6.5 °C above air at INS-0097-0215 (14 Jan 2027), recorded status active
- WELL-0105: 3.9 °C above air at INS-0105-0216 (14 Jan 2027), recorded status active
- WELL-0133: 4.0 °C above air at INS-0133-0219 (14 Jan 2027), recorded status active
- WELL-0134: 3.2 °C above air at INS-0134-0216 (14 Jan 2027), recorded status active
- WELL-0160: 3.8 °C above air at INS-0160-0217 (14 Jan 2027), recorded status active
- WELL-0167: 1.5 °C above air at INS-0167-0119 (14 Jan 2027), recorded status active
- WELL-0169: 5.2 °C above air at INS-0169-0219 (14 Jan 2027), recorded status active
- WELL-0175: 5.5 °C above air at INS-0175-0216 (14 Jan 2027), recorded status active
- WELL-0197: 1.2 °C above air at INS-0197-0214 (14 Jan 2027), recorded status down
- WELL-0199: 4.1 °C above air at INS-0199-0216 (31 Dec 2026), recorded status plugged
- WELL-0203: 22.4 °C above air at INS-0203-0221 (14 Jan 2027), recorded status active
- WELL-0213: 1.5 °C above air at INS-0213-0221 (14 Jan 2027), recorded status active
- WELL-0219: 4.5 °C above air at INS-0219-0171 (14 Jan 2027), recorded status active
- WELL-0249: 5.9 °C above air at INS-0249-0120 (14 Jan 2027), recorded status active
- WELL-0251: -0.4 °C above air at INS-0251-0215 (14 Jan 2027), recorded status active
- WELL-0263: 4.0 °C above air at INS-0263-0219 (14 Jan 2027), recorded status active
- WELL-0281: 10.2 °C above air at INS-0281-0214 (14 Jan 2027), recorded status down
- WELL-0309: 2.5 °C above air at INS-0309-0215 (14 Jan 2027), recorded status active
- WELL-0316: 1.0 °C above air at INS-0316-0217 (14 Jan 2027), recorded status active
- WELL-0330: 4.4 °C above air at INS-0330-0213 (14 Jan 2027), recorded status down
- WELL-0332: 0.5 °C above air at INS-0332-0217 (14 Jan 2027), recorded status active
- WELL-0373: 1.1 °C above air at INS-0373-0219 (14 Jan 2027), recorded status active
- WELL-0377: 0.4 °C above air at INS-0377-0220 (14 Jan 2027), recorded status active
- WELL-0397: 5.2 °C above air at INS-0397-0219 (14 Jan 2027), recorded status active
- WELL-0404: 1.8 °C above air at INS-0404-0214 (14 Jan 2027), recorded status down
- WELL-0408: 7.1 °C above air at INS-0408-0218 (14 Jan 2027), recorded status active
- WELL-0418: 8.2 °C above air at INS-0418-0219 (14 Jan 2027), recorded status active
- WELL-0429: 6.2 °C above air at INS-0429-0219 (14 Jan 2027), recorded status active
- WELL-0442: 2.5 °C above air at INS-0442-0220 (14 Jan 2027), recorded status active
- WELL-0452: 3.1 °C above air at INS-0452-0219 (14 Jan 2027), recorded status down
- WELL-0471: 1.8 °C above air at INS-0471-0219 (14 Jan 2027), recorded status active
- WELL-0490: 5.1 °C above air at INS-0490-0170 (14 Jan 2027), recorded status active

_Rules applied: T200: producing when wellhead − air ≥ 15 °C (T200 manual); T350: producing when wellhead − air ≥ 20 °C (T350 manual); T500: producing when wellhead − air ≥ 25 °C (T500 manual)._

*Visual:* bar · *Citations:* INS-0309-0215, INS-0316-0217, INS-0330-0213, INS-0332-0217, INS-0373-0219, INS-0377-0220, INS-0397-0219, INS-0404-0214, INS-0408-0218, INS-0418-0219, INS-0429-0219, INS-0442-0220, INS-0452-0219, INS-0471-0219, INS-0490-0170, INS-0496-0220, INS-0526-0218, INS-0528-0220, INS-0540-0215, INS-0545-0218, INS-0562-0219, INS-0010-0219, INS-0026-0216, INS-0032-0219, INS-0033-0222

## Q8.1 — Nathan Pierce
**Q:** WELL-0333's recalled pump was swapped out yesterday. The work order isn't in the system yet. Please count it as replaced from now on.

Noted for everyone: "WELL-0333's recalled pump was swapped out yesterday. The work order isn't in the system yet. Please count it as replaced from now on." — recorded as shared knowledge about WELL-0333 from Nathan Pierce (confirmed by data).

*Visual:* None · *Citations:* INS-0333-0219

## Q8.2 — Nathan Pierce
**Q:** Also, just for me: whenever you list wells, sort them by area and then by well ID, and show costs in thousands of dollars.

**Repair cost — the whole field, all records: USD 51,024,802 in total**

- Northwest Block 12: USD 13,619,050
- Southeast Block 32: USD 12,122,407
- Southwest Block 24: USD 6,150,758
- Southwest Block 23: USD 5,818,256
- Northeast Block 8: USD 4,907,856
- Northeast Block 7: USD 4,719,478
- Southeast Block 31: USD 3,686,997

_Rules applied: A repair belongs to a period by its start date._

*Visual:* table · *Citations:* MNT-0301-001, MNT-0301-002, MNT-0301-003, MNT-0301-004, MNT-0301-005, MNT-0301-006, MNT-0301-007, MNT-0301-008, MNT-0301-009, MNT-0301-010, MNT-0301-011, MNT-0301-012, MNT-0301-013, MNT-0301-014, MNT-0301-015, MNT-0301-016, MNT-0301-017, MNT-0301-018, MNT-0301-019, MNT-0301-020, MNT-0301-021, MNT-0301-022, MNT-0301-023, MNT-0301-024, MNT-0301-025

## Q8.3 — Robert Hayes
**Q:** Which recalled pumps are still in the ground right now?

I couldn't map this to a data tool. Relevant passages from the manuals/SOPs:

**fleet/sops/supplier-recall-notice-2026-12-01.md**: ## What is recalled

Highline RP-175 downhole rod pumps from these manufacturing lots:

- LOT-2409-A
- LOT-2409-C
- LOT-2410-B

Pumps from all other lots, including LOT-2409-B, LOT-2410-A and LOT-2410-C, are not affected.
Highline Pump Co. does not supply ESP pumps, so ESP wells are not affected by this notice.

**fleet/sops/supplier-recall-notice-2026-12-01.md**: ## How to find affected pumps

The lot number is stamped on the pump barrel. Your crews record it when the pump is installed
(in your maintenance reports, on the line "Parts installed"). Only the pump that is in the well
today matters: a recalled pump that has already been pulled and replaced needs no action.

Return pulled pumps to Highline Pump Co. for a full credit.

**fleet/well-types/T500.md**: ## 5. Early warning signs

An ESP runs at a steady speed, so a healthy T500 wellhead stays within a degree or two of
its usual difference above air. ESP motors usually fail after running hot with too little
fluid over the pump. In the weeks before a failure, the wellhead-to-air difference typically
**falls steadily** while the well is still producing.

- If the wellhead-to-air difference is **lower than at the inspection before, three
  inspections in a row** (four readings, each lower than the last) **and has fallen by
  3 °C or more in total** over those four readings, schedule an ESP drive 

*Visual:* None · *Citations:* fleet/sops/supplier-recall-notice-2026-12-01.md, fleet/sops/supplier-recall-notice-2026-12-01.md, fleet/well-types/T500.md

## Q8.4 — Olivia Grant
**Q:** Nathan told me the recalled pump on WELL-0577 was swapped as well. Take it off the recall list.

Noted for everyone: "Nathan told me the recalled pump on WELL-0577 was swapped as well. Take it off the recall list." — recorded as shared knowledge about WELL-0577 from Olivia Grant (confirmed by data).

*Visual:* None · *Citations:* INS-0577-0211

## Q8.5 — Nathan Pierce
**Q:** Show me the recalled pumps that are still in the ground in my area, and what it cost to install each one.

**Repair cost — the whole field (open=True): USD 51,213,351 in total**

_Rules applied: A repair belongs to a period by its start date._

*Visual:* None · *Citations:* MNT-0001-001, MNT-0001-002, MNT-0001-003, MNT-0001-004, MNT-0001-005, MNT-0001-006, MNT-0001-007, MNT-0001-008, MNT-0001-009, MNT-0001-010, MNT-0001-011, MNT-0001-012, MNT-0001-013, MNT-0001-014, MNT-0001-015, MNT-0001-016, MNT-0001-017, MNT-0001-018, MNT-0001-019, MNT-0001-020, MNT-0001-021, MNT-0001-022, MNT-0001-023, MNT-0001-024, MNT-0001-025

## Q9.1 — Robert Hayes
**Q:** How many recalled pumps are still in the ground, and in which areas?

I couldn't map this to a data tool. Relevant passages from the manuals/SOPs:

**fleet/sops/supplier-recall-notice-2026-12-01.md**: ## What is recalled

Highline RP-175 downhole rod pumps from these manufacturing lots:

- LOT-2409-A
- LOT-2409-C
- LOT-2410-B

Pumps from all other lots, including LOT-2409-B, LOT-2410-A and LOT-2410-C, are not affected.
Highline Pump Co. does not supply ESP pumps, so ESP wells are not affected by this notice.

**fleet/sops/supplier-recall-notice-2026-12-01.md**: ## How to find affected pumps

The lot number is stamped on the pump barrel. Your crews record it when the pump is installed
(in your maintenance reports, on the line "Parts installed"). Only the pump that is in the well
today matters: a recalled pump that has already been pulled and replaced needs no action.

Return pulled pumps to Highline Pump Co. for a full credit.

**fleet/well-types/T500.md**: ## 5. Early warning signs

An ESP runs at a steady speed, so a healthy T500 wellhead stays within a degree or two of
its usual difference above air. ESP motors usually fail after running hot with too little
fluid over the pump. In the weeks before a failure, the wellhead-to-air difference typically
**falls steadily** while the well is still producing.

- If the wellhead-to-air difference is **lower than at the inspection before, three
  inspections in a row** (four readings, each lower than the last) **and has fallen by
  3 °C or more in total** over those four readings, schedule an ESP drive 

*Visual:* None · *Citations:* fleet/sops/supplier-recall-notice-2026-12-01.md, fleet/sops/supplier-recall-notice-2026-12-01.md, fleet/well-types/T500.md

## Q9.2 — Robert Hayes
**Q:** Different topic. Who leads Northwest Production, and how many wells does that team run?

I couldn't map this to a data tool. Relevant passages from the manuals/SOPs:

**fleet/sops/regulator-letter-2026-11-20.md**: # Letter from the State Oil & Gas Commission

> Fictional letter for the FlytBase Asset Copilot hackathon.

**From:** State Oil & Gas Commission, District Office
**To:** Northeast Production (TEAM-NE), attention Michael Turner, production supervisor
**Date:** 20 Nov 2026
**Subject:** Soil sampling after reportable spills in Northeast Block 7 and Northeast Block 8

Our review of recent spill reports from your Northeast Block 7 and Northeast Block 8 leases found
clean-up files without laboratory soil results.

For every reportable spill in Northeast Block 7 or Northeast Block 8 since 1 Jun 2026,

**fleet/well-types/T500.md**: ## 5. Early warning signs

An ESP runs at a steady speed, so a healthy T500 wellhead stays within a degree or two of
its usual difference above air. ESP motors usually fail after running hot with too little
fluid over the pump. In the weeks before a failure, the wellhead-to-air difference typically
**falls steadily** while the well is still producing.

- If the wellhead-to-air difference is **lower than at the inspection before, three
  inspections in a row** (four readings, each lower than the last) **and has fallen by
  3 °C or more in total** over those four readings, schedule an ESP drive 

**fleet/well-types/T500.md**: ## 3. Production temperature rule

ESP wells move more fluid, and the motor adds heat. A T500 well is considered
**producing (active)** only when its wellhead temperature is at least **25 °C above
ambient** air temperature at the time of the reading. Below 25 °C the well is **not
producing** for that reading.

*Visual:* None · *Citations:* fleet/sops/regulator-letter-2026-11-20.md, fleet/well-types/T500.md, fleet/well-types/T500.md

## Q9.3 — Robert Hayes
**Q:** What does our operations SOP say about cold weather? Name one well that missed the check in December.

From the manuals and SOPs:

**fleet/sops/operations-sop-rev2.md**
> ## OPS-1 Gas odor response
> 
> An operator note reporting a gas smell needs a field response on that well. A gas odor report is an
> operator note saying the crew smelled gas, noticed a rotten-egg smell or a gas odor, or that an H2S
> monitor alarmed at a well.
> 
> A field response is either:
> - a maintenance job on that well (its `started_at` in `maintenance.jsonl`), or
> - an inspection of that well with `method` = `manual`. Drone inspections do not count.
> 
> The response must start after the note's `created_at` and within:
> - **24 hours** for reports noted before 1 Jan 2027;
> - **12 hours** for reports note

**fleet/sops/moc-2026-044.md**
> ## Change
> 
> This memo extends MOC-2026-031. The replacement check valves are still on back-order, so the
> temporary flowline bypass stays authorized on every well named in MOC-2026-031:
> WELL-0013, WELL-0062, WELL-0118, WELL-0248, WELL-0476.
> 
> The new expiry date below replaces the expiry date in MOC-2026-031. All other conditions of
> MOC-2026-031 stay the same. MOC-2026-036 is not changed by this memo.
> 
> This approval expires on 28 Feb 2027.

**fleet/sops/moc-2026-036.md**
> ## Change
> 
> A temporary flowline bypass is authorized on these wells: WELL-0087, WELL-0158, WELL-0249, WELL-0284, WELL-0356, WELL-0388, WELL-0461.

*Visual:* table · *Citations:* fleet/sops/operations-sop-rev2.md, fleet/sops/moc-2026-044.md, fleet/sops/moc-2026-036.md

## Q9.4 — Robert Hayes
**Q:** An operator reported a gas smell at WELL-0332 on 3 Dec. What was the H2S reading?

**WELL-0332 is not producing oil** (as of its latest inspection).

Latest inspection INS-0332-0217 on 14 Jan 2027, by drone, by Caleb Whitaker. Wellhead 10.9 °C vs air 10.4 °C: 0.5 °C warmer, below the T200 limit of 15 °C.

Reason: no recorded reason in repairs or notes. Suggest a site check.

The recorded status still says **active**, which is out of date.

*Visual:* card · *Citations:* INS-0332-0217, T200 manual

## Q9.5 — Robert Hayes
**Q:** Back to the pumps from my first question: which of those wells are not producing oil right now, and when was each one last repaired?

**Repair jobs — the whole field: 17415 in total**

**Highest: WELL-0071 (40)**

- WELL-0071: 40
- WELL-0194: 40
- WELL-0345: 40
- WELL-0433: 40
- WELL-0069: 39
- WELL-0074: 39
- WELL-0216: 39
- WELL-0340: 39
- WELL-0013: 38
- WELL-0044: 38
- WELL-0115: 38
- WELL-0138: 38
- WELL-0189: 38
- WELL-0348: 38
- WELL-0015: 37
- … 584 more

_Rules applied: A repair belongs to a period by its start date._

*Visual:* table · *Citations:* MNT-0071-001, MNT-0071-002, MNT-0071-003, MNT-0071-004, MNT-0071-005, MNT-0071-006, MNT-0071-007, MNT-0071-008, MNT-0071-009, MNT-0071-010, MNT-0071-011, MNT-0071-012, MNT-0071-013, MNT-0071-014, MNT-0071-015, MNT-0071-016, MNT-0071-017, MNT-0071-018, MNT-0071-019, MNT-0071-020, MNT-0071-021, MNT-0071-022, MNT-0071-023, MNT-0071-024, MNT-0071-025

## Q9.6 — Robert Hayes
**Q:** Of all the wells we've talked about today, which one would you deal with first, and why?

I couldn't map this to a data tool. Relevant passages from the manuals/SOPs:

**fleet/sops/supplier-recall-notice-2026-12-01.md**: ## How to find affected pumps

The lot number is stamped on the pump barrel. Your crews record it when the pump is installed
(in your maintenance reports, on the line "Parts installed"). Only the pump that is in the well
today matters: a recalled pump that has already been pulled and replaced needs no action.

Return pulled pumps to Highline Pump Co. for a full credit.

**fleet/well-types/T500.md**: ## 5. Early warning signs

An ESP runs at a steady speed, so a healthy T500 wellhead stays within a degree or two of
its usual difference above air. ESP motors usually fail after running hot with too little
fluid over the pump. In the weeks before a failure, the wellhead-to-air difference typically
**falls steadily** while the well is still producing.

- If the wellhead-to-air difference is **lower than at the inspection before, three
  inspections in a row** (four readings, each lower than the last) **and has fallen by
  3 °C or more in total** over those four readings, schedule an ESP drive 

**fleet/sops/operations-sop-rev2.md**: ## OPS-4 Failure classification

Classify a corrective job from the "## Root cause" section of its maintenance report. Check the
rows of this table **in order**: the **first** row with a keyword that appears in the root-cause
text (ignoring upper and lower case) gives the category. Order matters: a text that mentions both
sand and wear is Sand, and a text that mentions both corrosion and fatigue is Corrosion.

| Order | Category | Keywords |
|---|---|---|
| 1 | Installation error | installation, installed incorrectly, misaligned, re-terminated, not torqued, cross-threaded |
| 2 | Sand | sand |

*Visual:* None · *Citations:* fleet/sops/supplier-recall-notice-2026-12-01.md, fleet/well-types/T500.md, fleet/sops/operations-sop-rev2.md

## Q10 — Michael Turner
**Q:** When a well stays shut in longer than the repair itself, what are we usually waiting on: parts, crews, contractors or weather? Break it down by area for jobs started in 2026, with the typical number of extra days, and tell me if any area stands out.

**Repair jobs — the whole field, 2026 (maintenance type=corrective): 1183 in total**

- Northwest Block 12: 306
- Southeast Block 32: 253
- Southwest Block 23: 150
- Northeast Block 8: 137
- Southwest Block 24: 133
- Northeast Block 7: 128
- Southeast Block 31: 76

_Rules applied: A repair belongs to a period by its start date._

*Visual:* bar · *Citations:* MNT-0301-025, MNT-0301-027, MNT-0301-028, MNT-0302-027, MNT-0302-030, MNT-0304-023, MNT-0304-026, MNT-0304-027, MNT-0304-030, MNT-0305-030, MNT-0305-032, MNT-0306-029, MNT-0306-031, MNT-0307-023, MNT-0307-025, MNT-0307-028, MNT-0307-029, MNT-0309-022, MNT-0310-024, MNT-0312-033, MNT-0313-025, MNT-0313-027, MNT-0314-027, MNT-0314-032, MNT-0316-020

## Q11 — Olivia Grant
**Q:** Which region of the field consistently runs hotter?

I couldn't map this to a data tool. Relevant passages from the manuals/SOPs:

**fleet/sops/operations-sop-rev2.md**: ## OPS-1 Gas odor response

An operator note reporting a gas smell needs a field response on that well. A gas odor report is an
operator note saying the crew smelled gas, noticed a rotten-egg smell or a gas odor, or that an H2S
monitor alarmed at a well.

A field response is either:
- a maintenance job on that well (its `started_at` in `maintenance.jsonl`), or
- an inspection of that well with `method` = `manual`. Drone inspections do not count.

The response must start after the note's `created_at` and within:
- **24 hours** for reports noted before 1 Jan 2027;
- **12 hours** for reports note

**fleet/sops/field-work-sop.md**: # Field Work Safety and Maintenance SOP

> Fictional SOP for the FlytBase Asset Copilot hackathon. Simplified and modelled on common
> US onshore practice and the public scope of industry documents named below. It is not a
> copy of any standard and is not real safety, legal or regulatory guidance.

Document ID: SOP-WS · Revision 2 · Owner: Field Maintenance (TEAM-MX) with HSE (TEAM-HSE)

**fleet/well-types/T500.md**: ## 5. Early warning signs

An ESP runs at a steady speed, so a healthy T500 wellhead stays within a degree or two of
its usual difference above air. ESP motors usually fail after running hot with too little
fluid over the pump. In the weeks before a failure, the wellhead-to-air difference typically
**falls steadily** while the well is still producing.

- If the wellhead-to-air difference is **lower than at the inspection before, three
  inspections in a row** (four readings, each lower than the last) **and has fallen by
  3 °C or more in total** over those four readings, schedule an ESP drive 

*Visual:* None · *Citations:* fleet/sops/operations-sop-rev2.md, fleet/sops/field-work-sop.md, fleet/well-types/T500.md

