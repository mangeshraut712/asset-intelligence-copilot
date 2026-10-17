## What changed

## How it was checked
- [ ] `python -m pytest -q tests` passes
- [ ] `python -m eval.run_questions eval/examples.json --fresh` still scores 27/27
- [ ] `python -m eval.run_questions eval/unseen.json --fresh` still scores 46/46
- [ ] New behaviour has a test; numbers come from tools, not the LLM
