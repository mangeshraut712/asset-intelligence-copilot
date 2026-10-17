# Asset Intelligence Copilot: Results
*Mangesh Raut · FlytBase challenge, AHC × Hacktoberfest 2026 · page 2*

> This page holds the verified pre-final results. In the final hour run
> `AIC_TODAY=2026-10-17 python scripts/final_run.py --data <test-data> --questions final.txt`
> and it overwrites this page from `docs/results_template.md` with the final-question answers.

## Scores (rules-only mode, `AIC_LLM=0`, so they are reproducible without an API key)
| Check | Result | Output |
|---|---|---|
| 18 example scenarios from the problem statement (27 checks, sequential, with memory) | **27/27** | `results/examples_rules.md` |
| 46 unseen questions, expected answers computed straight from the raw files by `eval/gen_unseen.py` | **46/46** | `results/unseen_rules.md` |
| Sample + synthetic 400-well test set loaded together | **7/7** | `eval/synthetic.json` |
| pytest (tools, raw-data recomputation, memory scopes, corrections, examples, unseen, SR-02 regression, Gemma 4 guard, API) | **101 passed** | `tests/` |
| Final-hour command on sample + `synth/test-data` (400 wells, ~79k inspections) | **1.8 s end to end** | `docs/rehearsal-synthetic.md` |

## What worked
- Every number comes from a deterministic tool, and every answer cites record IDs and SOP/manual passages.
- Rules (production thresholds, spill reporting, containment and verification limits, RCA counts) come from the parsed documents, so new wells and areas need no code change.
- Facts that exist only in free-text repair reports are extracted, for example SR-02 containment times: WELL-0001's 11 Jun 2026 spill (6.8 bbl, INS-0001-0185) was contained after about **7 h** (MNT-0001-029, breach of the 4 h limit); its 1 Oct 2026 spill (1.6 bbl, INS-0001-0201) after about **1.7 h** (MNT-0001-032, met). Each SR-02 line names its spill.
- Shared well facts, private per-user memory, corrections and type-wide rules are applied at their scope, with provenance, and conflicts are surfaced instead of silently resolved.

## Known limits
- Gemma 4 is used for planning only when the rule router is not confident, for phrasing (rejected if it adds a number) and for advisory photo descriptions; with no API key the copilot runs on rules alone.
- Free-form feedback outside the supported patterns (correction, type rule, well statement) falls back to document search.
