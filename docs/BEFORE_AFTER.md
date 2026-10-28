# Before / after improvement examples

**TODO before submitting:** this file must be filled with REAL outputs from your own LLM key. None are
included on purpose: the code was only run with a scripted fake LLM, so any example text here would be invented.

How to produce them (≈10 min):
1. `python app.py` with a real key, then call `/generate-reply` for a held-out message → copy as **Before**.
2. `/improve-ai` (or `/improve-ai-manually`) → copy `diagnosis`, and `GET /prompt/diff?from=1&to=2` as **Prompt change**.
3. Call `/generate-reply` with the same input → copy as **After**.
4. `python -m scripts.lab eval --versions 1 latest --report docs/EVAL_REPORT.md` for the aggregate numbers.

For each example answer honestly: did it improve? Did it overfit or break another case?

## Example 1 - manual: "send lots of emojis" (assignment intermission), then restore
- Before: _paste_
- Prompt change (diff): _paste_
- After: _paste_
- Verdict: _improved / not, and why_

## Example 2 - auto: _scenario_
## Example 3 - auto: _scenario_ (include one case where the guard rejected an edit, if it happens)
