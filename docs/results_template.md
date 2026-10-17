# Asset Intelligence Copilot: Results on the Final Questions
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · page 2*

{{SUMMARY}}

## Answers
{{TABLE}}

Full answers, with every citation and the visual data, are in `results/final.md` and `results/final.json` in the repository.

## What worked
{{WORKED}}

## What didn't, and why
{{MISSES}}

{{CONFLICTS}}

## How these were produced
One command (`python scripts/final_run.py --data <test-data> --questions <final.txt>`) loaded the sample and test datasets into SQLite, reset runtime memory, and ran every question in order through the copilot (memory and corrections carry across questions as in the scenarios). Numbers come from deterministic tools. Thresholds and deadlines were parsed from the manuals and SOPs. Gemma 4 (open-weight) plans only the questions the rule router isn't confident about.
