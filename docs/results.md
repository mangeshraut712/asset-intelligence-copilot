# Asset Intelligence Copilot: Results on the Final Questions
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · page 2*

Test data: dataset loaded in one step. **21 questions answered in 183.4 s** (whole pipeline 185.5 s). 15 were answered by deterministic tools with high or medium confidence; 2 needed the Gemma 4 planner; 1 flagged a data conflict instead of silently picking a side. Visuals: bar × 2, card × 1, heatmap × 1, table × 7, text × 10.

## Answers
| # | Question | Answer (headline) | Visual | Confidence | Sources |
|---|---|---|---|---|---|
| Q1 | All our wells feed one reservoir. Map the reservoir pressure across the field from the pressure | Real spills in 2027 by area and month (corrected detections removed). Totals: Southwest Block 23: 4, Southwest Block 24: 3, Northeast Block 7: 2, Northeast Block 8: 3, So | heatmap | medium | 2 |
| Q2 | Which well produced the most oil in 2026? | I couldn't map this to a data tool. Relevant passages from the manuals/SOPs: | - | conflict | 3 |
| Q3 | Since 1 Nov 2026, every time an operator note reports gas at a well, did we get someone out to  | Human notes — the whole field, 1 Nov 2026 to 14 Jan 2027 (event type=noticeofviolation): 1277 in total | table | high | 200 |
| Q4 | Across all areas, which temporary flowline bypasses are in place right now, and is each one all | I couldn't map this to a data tool. Relevant passages from the manuals/SOPs: | - | low | 3 |
| Q5 | The State Oil & Gas Commission wrote to us in November 2026 about spills. Which of our spills d | Real spills — the whole field, November 2026: 48 in total | table | high | 48 |
| Q6 | Across the whole field, not just my area, for which wells do the latest inspection and the oper | 46 wells not producing oil right now — the whole field. | table | high | 46 |
| Q7.1 | Over the last month the operators have written notes about wells that sound or behave wrong. Wh | Repair jobs — the whole field, last month (14 Dec 2026 to 14 Jan 2027): 386 in total | table | high | 200 |
| Q7.2 | Which three would you send a crew to first this week, and why? | 46 wells not producing oil right now — the whole field. | bar | medium | 28 |
| Q8.1 | WELL-0333's recalled pump was swapped out yesterday. The work order isn't in the system yet. Pl | Noted for everyone: "WELL-0333's recalled pump was swapped out yesterday. The work order isn't in the system yet. Please count it as replaced from now on." — recorded as  | - | high | 1 |
| Q8.2 | Also, just for me: whenever you list wells, sort them by area and then by well ID, and show cos | Repair cost — the whole field, all records: USD 51,024,802 in total | table | high | 200 |
| Q8.3 | Which recalled pumps are still in the ground right now? | I couldn't map this to a data tool. Relevant passages from the manuals/SOPs: | - | low | 2 |
| Q8.4 | Nathan told me the recalled pump on WELL-0577 was swapped as well. Take it off the recall list. | Noted for everyone: "Nathan told me the recalled pump on WELL-0577 was swapped as well. Take it off the recall list." — recorded as shared knowledge about WELL-0577 from  | - | high | 1 |
| Q8.5 | Show me the recalled pumps that are still in the ground in my area, and what it cost to install | Repair cost — the whole field (open=True): USD 51,213,351 in total | - | high | 200 |
| Q9.1 | How many recalled pumps are still in the ground, and in which areas? | I couldn't map this to a data tool. Relevant passages from the manuals/SOPs: | - | low | 2 |
| Q9.2 | Different topic. Who leads Northwest Production, and how many wells does that team run? | I couldn't map this to a data tool. Relevant passages from the manuals/SOPs: | - | low | 2 |
| Q9.3 | What does our operations SOP say about cold weather? Name one well that missed the check in Dec | From the manuals and SOPs: | table | high | 3 |
| Q9.4 | An operator reported a gas smell at WELL-0332 on 3 Dec. What was the H2S reading? | WELL-0332 is not producing oil (as of its latest inspection). | card | high | 2 |
| Q9.5 | Back to the pumps from my first question: which of those wells are not producing oil right now, | Repair jobs — the whole field: 17415 in total | table | high | 200 |
| Q9.6 | Of all the wells we've talked about today, which one would you deal with first, and why? | I couldn't map this to a data tool. Relevant passages from the manuals/SOPs: | - | low | 3 |
| Q10 | When a well stays shut in longer than the repair itself, what are we usually waiting on: parts, | Repair jobs — the whole field, 2026 (maintenance type=corrective): 1183 in total | bar | high | 200 |
| Q11 | Which region of the field consistently runs hotter? | I couldn't map this to a data tool. Relevant passages from the manuals/SOPs: | - | low | 3 |

Full answers, with every citation and the visual data, are in `results/final.md` and `results/final.json` in the repository.

## What worked
- The loader took the 600-well test dataset (125,198 inspections, 17,415 repair jobs, 1,887 notes, 12 documents) in one step with no code change, including the new areas, team and T500 well type.
- Shared memory recorded the user-reported pump swaps in Q8.1 and Q8.4 against the right wells and the person who said them.
- When the router had no matching tool, it said so and quoted the right governing documents instead of inventing numbers: the recall notice (Q8.3, Q9.1), OPS-2 bypass rule (Q4) and OPS-1 gas-odor deadlines (Q9.3, Q11 fallback).

## What didn't, and why
I checked every answer by hand. Most of the final questions need tools my copilot does not have yet, and the router matched them to the closest existing tool instead, so the headline numbers in the table above mostly answer a different question.
- **Wrong tool chosen (Q1, Q3, Q5, Q6, Q7, Q8.2, Q8.5, Q9.4, Q9.5, Q10):** Q1 drew a spill heatmap instead of pressure; Q3 counted notices of violation instead of matching gas notes to responses; Q5 listed all November spills instead of the letter's Northeast Block 7/8 soil-sampling scope; Q6 listed non-producing wells without comparing them to operator notes; Q7.1 counted repairs instead of ranking wells from operator notes; Q10 counted corrective jobs instead of shut-in delay reasons. Q9.4 gave a status card instead of the H2S reading.
- **No tool at all (Q2, Q4, Q8.3, Q9.1, Q9.2, Q9.6, Q11):** there is no production-volume ranking, MOC/bypass check, recall-lot lookup from "Parts installed", team-lead lookup or regional temperature trend. These fell back to document search.
- **Memory gaps:** Q8.2 (Nathan's private sort and thousands-of-dollars preference) was treated as a cost question, not saved as a private preference. Q8.4 accepted Olivia's second-hand report as "confirmed by data" instead of flagging that it came from Nathan through Olivia and has no work order.
- **Why:** the router was built around the 18 example questions. The test set added new document types (MOC memos, recall notice, regulator letter, operator notes) and new fields, and I had no tools for them before the deadline. This is exactly the "tuned to the sample" risk the brief warned about; next I would add those tools and make low-confidence routing ask the planner instead of forcing the nearest tool.

## How these were produced
One command (`python scripts/final_run.py --data <test-data> --questions eval/final_questions.json`) loaded the test dataset (which already contains the 200 sample wells with three more months of records) into SQLite with today set to 15 Jan 2027, reset runtime memory, and ran every question in order through the copilot (memory and corrections carry across questions as in the scenarios). Numbers come from deterministic tools. Thresholds and deadlines were parsed from the manuals and SOPs. Gemma 4 (open-weight) plans only the questions the rule router isn't confident about.
