# Contributing

Thanks for helping. Issues and pull requests are welcome.

## Setup
```bash
git clone https://github.com/FlytBaseAILabs/flytbase-ahc-swe-asset-intelligence-dataset ../dataset
pip install -r requirements.txt -r requirements-dev.txt
python -m copilot.loader ../dataset/sample-data
python -m uvicorn copilot.server:app --port 8000
```

## Ground rules
1. **The model never does arithmetic.** Every number comes from a deterministic tool in `copilot/tools.py` or `copilot/query.py`. Gemma 4 may plan, phrase or describe photos, and its output is checked.
2. **Every answer cites its sources** (record IDs and document passages).
3. **Thresholds and deadlines come from the manuals and SOPs** (`rules` table built by `copilot/loader.py`), not from constants in code.
4. **Corrections keep the original** and record who changed what and why; they apply only at their scope (one inspection or one well type).

## Before you open a PR
```bash
python -m pytest -q tests
python -m eval.run_questions eval/examples.json --fresh   # must stay 27/27
python -m eval.run_questions eval/unseen.json --fresh     # must stay 46/46
```
Add a test for any bug fix (see `tests/test_containment.py` for an example regression test).

## Layout
| Path | What |
|---|---|
| `copilot/` | loader, tools, query engine, agent (router + Gemma 4 planner), Gemma 4 helpers, FastAPI server |
| `web/` | single-file chat UI (no build step) |
| `eval/` | question sets and the checker; `gen_unseen.py` computes expected answers from raw files |
| `scripts/` | `final_run.py` (final-hour one-shot), `record_demo.py`, synthetic dataset generator, container entrypoint |
| `tests/` | pytest suite |
| `docs/` | write-up, results, video script, CI workflow template |

CI: `docs/ci-workflow.yml` is a GitHub Actions workflow; copy it to `.github/workflows/ci.yml` (needs a token with the `workflow` scope).

By contributing you agree your work is released under the MIT License.
