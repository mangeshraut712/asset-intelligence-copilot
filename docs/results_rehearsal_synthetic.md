# Asset Intelligence Copilot: Results on the Final Questions
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · page 2*

Test data: sample-data, test-data loaded in one step. **15 questions answered in 0.6 s** (whole pipeline 1.7 s). 15 were answered by deterministic tools with high or medium confidence; 0 needed the Gemma 4 planner; 2 flagged a data conflict instead of silently picking a side. Visuals: bar × 2, card × 3, heatmap × 1, line × 1, map × 1, table × 5, text × 2.

## Answers
| # | Question | Answer (headline) | Visual | Confidence | Sources |
|---|---|---|---|---|---|
| F1 | Is WELL-0201 producing oil right now? When was it last inspected, and by whom? | WELL-0201 is not producing oil (as of its latest inspection). | card | high | 3 |
| F2 | Which wells in Southeast Block 42 are not producing oil right now, and why? Show them in a tabl | 4 wells in Southeast Block 42 are not producing oil right now (latest inspection per well): WELL-0364, WELL-0370, WELL-0372, WELL-0375. | table | high | 5 |
| F3 | Show a line chart of WELL-0321's wellhead temperature against air temperature for the last 13 w | 13 readings for WELL-0321 (23 Jul 2026 to 15 Oct 2026). Not producing oil on: 3 Sep 2026, 10 Sep 2026, 17 Sep 2026, 24 Sep 2026, 8 Oct 2026, 15 Oct 2026 (wellhead less th | line | high | 1 |
| F4 | How many oil spills has WELL-0282 had in the last 4 years, and how much oil in total? List them | 3 real spills for WELL-0282 (16 Oct 2022 to 16 Oct 2026), 2.9 barrels in total. | table | high | 4 |
| F5 | How many days was WELL-0205 down in 2025? | WELL-0205 was down 42 days (1 Jan 2025–31 Dec 2025), from 6 weekly inspections where it was not producing oil: | - | high | 8 |
| F6 | Which 3 wells in Northwest Block 32 had the most downtime in the last 4 months? Show a bar char | Top 3 wells in Northwest Block 32 by downtime (16 Jun 2026 to 16 Oct 2026): WELL-0284: 42 days (T200), WELL-0269: 35 days (T200), WELL-0261: 28 days (T200). Next is WELL- | bar | high | 16 |
| F7 | Show on a map every well in Southeast Block 41 with a real spill in the last 90 days. | 10 real spills for Southeast Block 41 (19 Jul 2026 to 16 Oct 2026), 14.6 barrels in total. 13 detections; excluded as corrected: INS-0307-0201 (20 Aug 2026, CTX-0307-002) | map | high | 14 |
| F8 | Show a heatmap of 2026 spills by geographic area and month. | Real spills in 2026 by area and month (corrected detections removed). Totals: Southwest Block 23: 35, Southwest Block 24: 43, Northeast Block 7: 37, Northeast Block 8: 26 | heatmap | high | 2 |
| F9 | Which rules has WELL-0213 broken in the last 12 months, and what is still open? | WELL-0213: 4 rule breach(es) in the last 12 months. | table | high | 17 |
| F10 | In Northwest Block 31, which spills in the last 90 days were not contained within the SOP time  | 4 spills in Northwest Block 31 were not contained within the 4-hour SOP limit (SR-02): WELL-0217 after about 4.9 h (report MNT-0217-029, inspection INS-0217-0198); WELL-0 | table | high | 9 |
| F11 | Which area lost the most production days in 2025? | Downtime — the whole field, 2025: 8120 days in total | bar | high | 200 |
| F12 | What fines are still open across the field? | Regulator fines — the whole field (open=True): USD 15,000 in total | table | high | 4 |
| F13 | Is WELL-0364 producing oil right now? | WELL-0364 is not producing oil (as of its latest inspection). | card | high | 2 |
| F14 | The 15 Oct reading for WELL-0364 is wrong. The field crew re-measured the wellhead at 41.0 °C. | Recorded: INS-0364-0205 (15 Oct 2026) wellheadtempc corrected from 24.0 to 41.0 by Michael Turner. The original value is kept; the correction applies to every later answe | - | conflict | 1 |
| F15 | Is WELL-0364 producing oil right now? | WELL-0364 is producing oil (as of its latest inspection). | card | conflict | 3 |

Full answers, with every citation and the visual data, are in `results/final.md` and `results/final.json` in the repository.

## What worked
- 13/15 answers came from a confident deterministic route, with record and document citations.
- Rules (production thresholds, the spill reporting, containment and verification limits, RCA counts) were applied from the parsed documents, so the new wells and areas needed no code change.
- Corrections, shared facts and private memory were applied at their scopes across the question sequence.
- 2 answers surfaced conflicts between users or with the data, as required.

## What didn't, and why
- No low-confidence answers. Remaining risk: answers whose wording differed from the expected phrasing, which I'm checking manually against the results page.

## Answers that flagged conflicts
- F14: The 15 Oct reading for WELL-0364 is wrong. The field crew re-measured the wellhead at 41.0 °C.
- F15: Is WELL-0364 producing oil right now?

## How these were produced
One command (`python scripts/final_run.py --data <test-data> --questions <final.txt>`) loaded the sample and test datasets into SQLite, reset runtime memory, and ran every question in order through the copilot (memory and corrections carry across questions as in the scenarios). Numbers come from deterministic tools. Thresholds and deadlines were parsed from the manuals and SOPs. Gemma 4 (open-weight) plans only the questions the rule router isn't confident about.
