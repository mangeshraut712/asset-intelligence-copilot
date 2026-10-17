# Asset Intelligence Copilot: Results on the Final Questions
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · page 2*

Test data: sample-data, test-data loaded in one step. **7 questions answered in 0.3 s** (whole pipeline 1.8 s). 7 were answered by deterministic tools with high or medium confidence; 0 needed the Gemma 4 planner; 0 flagged a data conflict instead of silently picking a side. Visuals: bar × 2, card × 1, heatmap × 1, map × 1, table × 2.

## Answers
| # | Question | Answer (headline) | Visual | Confidence | Sources |
|---|---|---|---|---|---|
| F1 | Is WELL-0201 producing oil right now? When was it last inspected, and by whom? | WELL-0201 is not producing oil (as of its latest inspection). | card | high | 3 |
| F2 | Which 3 wells in Southeast Block 41 had the most downtime in the last 4 months? Show a bar char | Top 3 wells in Southeast Block 41 by downtime (16 Jun 2026 to 16 Oct 2026): WELL-0321: 49 days (T200), WELL-0307: 42 days (T350), WELL-0338: 42 days (T350). Next is WELL- | bar | high | 20 |
| F3 | Show a heatmap of 2026 spills by geographic area and month. | Real spills in 2026 by area and month (corrected detections removed). Totals: Southwest Block 23: 35, Southwest Block 24: 43, Northeast Block 7: 37, Northeast Block 8: 26 | heatmap | high | 2 |
| F4 | Which rules has WELL-0201 broken in the last 12 months, and what is still open? | WELL-0201: 4 rule breach(es) in the last 12 months, USD 5,000 in fines still open. | table | high | 12 |
| F5 | In Northwest Block 32, which spills in the last 90 days were not contained within the SOP time  | 2 spills in Northwest Block 32 were not contained within the 4-hour SOP limit (SR-02): WELL-0282 after about 7.1 h (report MNT-0282-028, inspection INS-0282-0198); WELL-0 | table | high | 5 |
| F6 | Show on a map every well in Southeast Block 42 with a real spill in the last 90 days. | 4 real spills for Southeast Block 42 (19 Jul 2026 to 16 Oct 2026), 10.2 barrels in total. 6 detections; excluded as corrected: INS-0394-0192 (23 Jul 2026, CTX-0394-002),  | map | high | 7 |
| F7 | Which 3 wells in Northeast Block 7 had the most downtime in the last 4 months? Show a bar chart | Top 3 wells in Northeast Block 7 by downtime (16 Jun 2026 to 16 Oct 2026): WELL-0121: 49 days (T200), WELL-0107: 42 days (T350), WELL-0138: 42 days (T350). Next is WELL-0 | bar | high | 20 |

Full answers, with every citation and the visual data, are in `results/final.md` and `results/final.json` in the repository.

## What worked
- 7/7 answers came from a confident deterministic route, with record and document citations.
- Rules (production thresholds, the spill reporting, containment and verification limits, RCA counts) were applied from the parsed documents, so the new wells and areas needed no code change.
- Corrections, shared facts and private memory were applied at their scopes across the question sequence.

## What didn't, and why
- No low-confidence answers. Remaining risk: answers whose wording differed from the expected phrasing, which I'm checking manually against the results page.



## How these were produced
One command (`python scripts/final_run.py --data <test-data> --questions <final.txt>`) loaded the sample and test datasets into SQLite, reset runtime memory, and ran every question in order through the copilot (memory and corrections carry across questions as in the scenarios). Numbers come from deterministic tools. Thresholds and deadlines were parsed from the manuals and SOPs. Gemma 4 (open-weight) plans only the questions the rule router isn't confident about.
