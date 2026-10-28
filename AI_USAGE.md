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
| 3-repeat eval with CIs (round 3) | auto-learned prompt significantly worse (ΔF1 −0.024); a hand-written 40-word rule cut length 1.67x→1.24x with no detectable F1 loss | adopted the rule into the seed prompt + live DB (v5); kept the auto loop but documented that it didn't help |
| Stored/forwarded raw chats to the editor | PII risk (emails, phones, IDs) | added redaction + tests |

Full numbers and outputs: `docs/BEFORE_AFTER.md`, `docs/EVAL_ROUND1.md`, `EVAL_ROUND2.md`, `EVAL_ROUND3.md`.

## How results were checked
- 19 offline tests with a scripted fake LLM (workflow, guards, rollback, HTTP validation, auth, history order, retrieval leakage, privacy).
- Live runs of all three endpoints against the real LLM and a real Postgres (Supabase), plus the assignment's "send lots of emojis" manual-update test and a rollback.
- Held-out evaluation by whole conversation (never single turns).

## My contribution
I'll be upfront: Claude Code wrote nearly all of the code, tests and docs. I asked it to draft this section from our session history, and I read it and kept only what is true.

What I did myself:
- Picked the tools and services: Claude Code instead of Cursor (the assignment allows other tools), OpenRouter for the model, Supabase for the database, Render for hosting. I made the accounts and keys, created the GitHub repo and set up the Render service.
- Ran the deployment and fixed the problems it hit. My first Render deploy failed because I had pasted my Supabase dashboard link into `DATABASE_URL` instead of the real connection string. The error message showed it. After fixing that, a stray line break in the value broke it again, so we made the app trim whitespace from all settings.
- Decided to report the results as they came out, including the ones that didn't help, instead of picking numbers that look better.

What I learned from testing (details in `docs/BEFORE_AFTER.md`):
- The automatic prompt learning did not help. On chats it had never seen it scored slightly *worse* than the starting prompt. One hand-written rule (a 40-word limit) did help: replies went from about 1.7x to 1.2x the length of the human replies, with no clear drop in the score. That rule is in the final prompt.
- My first test looked fine but the prompt had nearly doubled in size from just three conversations, so we added a size cap and a better training order, then tested again with repeats and confidence intervals.
- The sample data has no ghosting, and the Laos price (5,000 + 10,000 THB) is described as a total of 18,000, which doesn't add up. I didn't invent anything to cover those gaps.

What is unfinished:
- No quality check beyond a word-overlap score on 24 turns; it needs human ratings.
- The facts the bot knows come from 15 made-up chats, and it still avoids answering things the human consultants answer directly (like translation rules).
- The free Render server sleeps, so the first request can take about a minute.

Next I would batch several examples per prompt edit, add the missing business facts as a proper knowledge section, and have a person rate replies.
