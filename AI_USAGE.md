# AI usage log

## Tools used
- **Claude Code** (Anthropic; model Claude Sonnet 5.5) in the Claude desktop app. It read the assignment and sample data and wrote the code, tests and docs in this repo, running commands and tests itself.
- **Not used:** Cursor / Antigravity / the "browser prompt → Cursor prompt" relay in the assignment. The assignment lets applicants choose tools ("Cursor/Antigravity and LLMs of your choice"); I used Claude Code instead, so the generated prompts were written directly in the repo, not copied between tools.
- **LLM inside the app:** `anthropic/claude-haiku-5.5` via OpenRouter (provider is swappable: Gemini, Groq, Anthropic, OpenRouter).
- **Final application prompts** (as requested): `assistant/prompts.py` - `SEED_PROMPT` (chatbot), `EDITOR_PROMPT` (auto-improve), `MANUAL_EDITOR_PROMPT`. The evolving live prompt is in the database (`GET /prompt`, `/prompt/history`).

## Key prompts (to Claude Code)
1. The assessment email (pasted verbatim) with the assignment link, as the task.
2. "Look at the lab and improve the work", with the lab's recruitment page pasted. This led to the eval rework (repeats + bootstrap CIs, hypothesis arms), PII redaction, and the privacy/credits/method sections in the README.
3. Smaller steering messages: provide an OpenRouter key; use Supabase Postgres; report honestly rather than polish.

## What the AI did, and what changed because of testing
| AI proposal / output | What testing showed | Resulting change |
|---|---|---|
| Output-format contract appended by code, not stored in the prompt | (design choice, covered by tests) | kept |
| Edit guards (empty/short/long, protected `## HARD RULES`, ±40% size) | caught destructive edits in tests | kept |
| Auto-learning loop, first round (20 edits, 3 conversations) | prompt grew 94% and memorised scenarios; held-out F1 0.253→0.259 (noise) | interleaved training order, 5,200-char size cap, "no scenario scripts" editor rule |
| Second round after fixes | held-out F1 0.251→0.232; length still ~1.5x human | stated as *no demonstrated gain*; built a repeat/CI eval to test hypotheses properly |
| Token-F1 as the quality metric | too noisy for one reference reply | added length ratio, AI-isms, repeats, paired bootstrap CI |
| Stored/forwarded raw chats to the editor | PII risk (emails, phones, IDs) | added redaction + tests |

Full numbers and outputs: `docs/BEFORE_AFTER.md`, `docs/EVAL_ROUND1.md`, `EVAL_ROUND2.md`, `EVAL_ROUND3.md`.

## How results were checked
- 19 offline tests with a scripted fake LLM (workflow, guards, rollback, HTTP validation, auth, history order, retrieval leakage, privacy).
- Live runs of all three endpoints against the real LLM and a real Postgres (Supabase), plus the assignment's "send lots of emojis" manual-update test and a rollback.
- Held-out evaluation by whole conversation (never single turns).

## Honest limits of this log
Everything above was produced by the AI under my prompts. The section below is the part only I can write, and it must describe things I actually did.

## TODO - my personal contribution (write in your own words, truthfully)
Examples of what belongs here: which decisions you reviewed and kept/changed/rejected and why; what you ran yourself and what you saw; the problems you noticed (e.g. the replies being too long, the data inconsistency in Laos pricing, no ghosting in the data); what you would try next; how you deployed it. Do not claim work you did not do.
