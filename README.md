# BOBALAB Self-Improving Support Assistant

**Live:** https://boba-assistant.onrender.com (Render free tier: the first request after idle can take ~1 minute to wake up) · **Repo:** https://github.com/Thanawat-Traipat/Boba---assistant

A Flask microservice that answers visa (DTV) customer DMs in a human, casual voice, keeps its
system prompt in a database, and **improves that prompt** from real consultant replies or reviewer
instructions. "Self-learning" here means prompt editing, not model training.

> **Status:** all three endpoints verified on the hosted deployment (Render + Supabase Postgres + OpenRouter); 20 offline tests pass. The auto-learning loop works mechanically but did **not** show a measurable quality gain in my held-out tests - see [`docs/BEFORE_AFTER.md`](docs/BEFORE_AFTER.md) and [Known limitations](#known-limitations-and-honest-status).

## Endpoints (match the assignment spec)

| Method & path | Purpose |
|---|---|
| `POST /generate-reply` | `{clientSequence, chatHistory}` → `{aiReply}` |
| `POST /improve-ai` | `{clientSequence, chatHistory, consultantReply}` → `{predictedReply, updatedPrompt, ...}` |
| `POST /improve-ai-manually` | `{instructions}` → `{updatedPrompt, ...}` |
| `GET /prompt`, `GET /prompt/history`, `GET /prompt/diff?from=1&to=2` | inspect the live prompt, versions, and a unified diff of any edit |
| `POST /prompt/restore` `{version}` | roll back (appends a copy; history is never rewritten) |
| `GET /health` | liveness |

Extra response fields on the improve endpoints (`promptVersion`, `changed`, `diagnosis`, `changes`, `rejectedReason`) are additive; the spec'd fields are always present.

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add ONE LLM key (Gemini/Groq/Anthropic/OpenRouter); leave DATABASE_URL empty for SQLite
python app.py                 # http://localhost:5000
pytest                        # 20 offline tests, no API key needed
```

### Deploy on Vercel (alternative to Render)
1. Import the GitHub repo at vercel.com/new (framework: Flask is auto-detected from `app.py`; `vercel.json` sets a 60 s function limit because `/improve-ai` makes two LLM calls).
2. Add environment variables: `LLM_PROVIDER`, `LLM_MODEL`, the LLM key, `DATABASE_URL` (**Postgres is required**: Vercel's disk is read-only/ephemeral, so SQLite won't work), and `ADMIN_TOKEN`.
3. Deploy, then open `/health`. Caveat: the edit lock is per instance, so two *simultaneous* improve calls on different serverless instances could race (the version primary key makes the loser fail with an error, not corrupt data).

### Deploy (Render + Neon/Supabase)
1. Create a free Postgres (Neon or Supabase) and copy its connection string.
2. Push the repo to GitHub; on Render create a *Blueprint* from `render.yaml` (Docker).
3. Set `GEMINI_API_KEY` (or switch `LLM_PROVIDER`), `DATABASE_URL`, and optionally `ADMIN_TOKEN` in the dashboard.
4. Check `GET /health`, then run the cURL examples below against your URL.

Configuration is all environment variables, documented in `.env.example`.

## cURL examples

```bash
BASE=https://boba-assistant.onrender.com      # or http://localhost:5000
# If ADMIN_TOKEN is set, add:  -H "X-Admin-Token: $ADMIN_TOKEN"  to the two improve calls.

# 1) generate-reply   (chatHistory is NEWEST-first, exactly as in the assignment example)
curl -s $BASE/generate-reply -H 'Content-Type: application/json' -d '{
  "clientSequence": "I'"'"'m American and currently in Bali. Can I apply from Indonesia?",
  "chatHistory": [
    {"role": "consultant", "message": "Hi there! Thank you for reaching out. The DTV is perfect for remote workers like yourself. May I know your nationality and which country you'"'"'d like to apply from?"},
    {"role": "client", "message": "Hello, I'"'"'m interested in the DTV visa for Thailand. I work remotely as a software developer for a US company."}
  ]}'
# -> {"aiReply": "Yes, you can apply from Indonesia! ..."}

# 2) improve-ai
curl -s $BASE/improve-ai -H 'Content-Type: application/json' -d '{
  "clientSequence": "I'"'"'m American and currently in Bali. Can I apply from Indonesia?",
  "chatHistory": [
    {"role": "consultant", "message": "Hi there! Thank you for reaching out. May I know your nationality and which country you'"'"'d like to apply from?"},
    {"role": "client", "message": "Hello, I'"'"'m interested in the DTV visa for Thailand."}
  ],
  "consultantReply": "Yes, you can apply from Indonesia! For remote workers, our service fees are 18,000 THB including all government fees. The processing time in Indonesia is typically around 10 business days."}'
# -> {"predictedReply": "...", "updatedPrompt": "...", "promptVersion": 2, "changed": true, "diagnosis": "...", "changes": ["..."]}

# 3) improve-ai-manually
curl -s $BASE/improve-ai-manually -H 'Content-Type: application/json' \
  -d '{"instructions": "Be more concise. Always mention appointment booking proactively."}'
# -> {"updatedPrompt": "...", "promptVersion": 3, "changed": true, "changes": ["..."]}

# See exactly what an edit changed
curl -s "$BASE/prompt/diff?from=1&to=2"
```

## How it works

```
 client msg + history ──► retrieve 3 similar REAL exchanges (TF-IDF) ─┐
 active prompt (DB, latest version) ───────────────────────────────────┼─► LLM ─► {"reply": ...}
 output-format contract (appended by code, not stored) ────────────────┘

 /improve-ai:   predict reply ─► EDITOR meta-prompt(prompt, history, real reply, predicted reply)
                ─► guard checks ─► (optional) regenerate & compare ─► save as version N+1
 /improve-ai-manually: MANUAL EDITOR meta-prompt(prompt, instructions) ─► guard ─► version N+1
```

Layout: `app.py` (routes) · `assistant/service.py` (workflow) · `prompts.py` (seed prompt, both editor prompts, guards) · `store.py` (versioned prompt table, Postgres/SQLite) · `llm.py` (Gemini/Groq/Anthropic over HTTP + mock) · `retrieval.py` · `dataset.py` · `metrics.py` · `privacy.py` · `scripts/lab.py` (batch train + held-out eval) · `tests/`.

### Decisions that go beyond the provided prompts

1. **Output contract lives in code, not in the prompt.** A self-editing prompt could otherwise edit away `{"reply": ...}` and take the API down. The editor can never touch it.
2. **Guarded edits.** A model-proposed prompt is rejected (and *not saved*) if it is empty, too short/long, loses the protected `## HARD RULES` section, or changes length by >40% (edits must be surgical). `/improve-ai` then returns `changed:false` with `rejectedReason`. Optional `VALIDATE_EDITS=true` re-generates with the new prompt and rejects it if token-F1 against the real reply drops.
3. **Generalise, don't memorise.** The editor prompt forbids customer-specific details, pasting the real reply, and adding a business fact that contradicts an existing one (replace instead of append).
4. **Append-only versions + diff + restore.** Every edit is a row; bad learning is one `POST /prompt/restore` away. `GET /prompt/diff` makes each self-learning edit auditable.
5. **Few-shot from real replies.** Similar past consultant replies are injected at generation time, which anchors tone/length better than instructions alone. In `/improve-ai` the example's own real reply is excluded to avoid leaking the answer.
6. **History order.** The assignment example lists `chatHistory` *newest-first* (consultant "Hi there!" before the client's first "Hello"). That is unusual, so it is the default (`HISTORY_ORDER`) and overridable per request with `historyOrder`.
7. **Held-out evaluation.** `scripts/lab.py` splits whole conversations (every 4th held out), trains on the rest, and compares prompt versions on unseen chats with token-F1, length ratio and an "AI-isms" count.
8. **Serialised edits** with a lock so two concurrent improvements can't overwrite each other.

### What the sample data told me (used to write the seed prompt)
- 15 synthetic chats, 130 consultant messages: median ~36 words, only 5 contain an emoji, 36 use numbered lists (for documents/steps), ~1 in 6 ends with a question. Style rules in the seed prompt (short, plain, one question, rare emoji, lists only for 3+ items) come from this.
- Common intents: eligibility, documents, 500k THB balance, fees, processing time, payment timing, rejection/reapply, embassy interview, post-approval/extension, money-back guarantee.
- High-interest signals: client volunteers nationality/country, asks "how do I start", "when do I pay", uploads documents. The prompt tells the bot to give one clear next step (app + document upload) at these moments.
- **Ghosting / drop-off cannot be learned from this data**: all 15 conversations end with a consultant message and none shows a client going silent. I did not invent drop-off behaviour.
- **Data inconsistency:** Laos is described as "5,000 service + 10,000 government = total 18,000 THB" (that sums to 15,000). The seed prompt states the two components and never a total.

## Evaluation method (and why I don't trust a single number)
- **Held-out by conversation:** every 4th conversation (24 client turns) is never used for training or few-shot retrieval.
- **One reference reply per turn is a weak target:** many different replies are fine. Token-F1 only measures overlap with the one human reply, so I also track length ratio and "AI-isms" (boilerplate/markdown/emoji).
- **Noise control:** replies are sampled, so `python -m scripts.lab eval --repeats 3` generates each turn several times, averages per turn, and reports the difference to the baseline with a **paired bootstrap 95% CI**. A change counts as demonstrated only if the CI excludes 0 (marked ▲/▼ in the report).
- **Hypothesis testing:** `--rule "..."` evaluates "baseline + one candidate prompt line" as its own arm, so a hunch (e.g. "replies are ~50% too long") can be tested before it goes anywhere near the live prompt. Results: `docs/EVAL_ROUND3.md`.
- Still missing: human ratings or an LLM judge for correctness/naturalness, and far more than 24 turns.

## Privacy and responsible use
- **Redaction before persistence:** emails, URLs, phone/long-number runs and passport-style IDs are replaced with placeholders (`assistant/privacy.py`) before a chat is shown to the *editor* LLM or written to the prompt-history notes. Tests prove the editor input and DB never contain the raw values. Names and addresses are **not** detected; the live `/generate-reply` call necessarily sends the raw message to the LLM provider you configure.
- **Prompts hold rules, not people:** the editor is told to generalise and never copy customer details or the real reply into the prompt.
- **Persuasion:** the bot is designed to move interested clients to the next step. That is a behavioural nudge, so the prompt forbids invented facts, promised approval and false urgency, and requires stating the money-back guarantee's limits. Review `GET /prompt/diff` after each learning run to check edits haven't made the bot pushier.
- **Human in the loop:** nothing is sent to customers by this service; it only returns text. A person should review replies before sending, especially on fees, legal rules and refunds.
- **Authorization:** set `ADMIN_TOKEN` in production; the improve endpoints change the behaviour of every future reply.

## Credits
- Task, sample conversations and the prompt-engineering workflow (seed idea, editor-prompt idea, endpoint spec) come from BOBALAB's take-home assessment (github.com/MoriJinzz/Bobalab-Assesment). The 15 chats are synthetic.
- Built with Claude Code (Claude Sonnet 5.5); the LLM used for the results above is `anthropic/claude-haiku-5.5` via OpenRouter. Libraries: Flask, gunicorn, requests, psycopg, python-dotenv, pytest. Full AI-use details in `AI_USAGE.md`.

## Before / after
See [`docs/BEFORE_AFTER.md`](docs/BEFORE_AFTER.md). Reproduce with:
```bash
python -m scripts.lab train --limit 30 --sleep 1
python -m scripts.lab eval --versions 1 latest --report docs/EVAL_REPORT.md
```

## Known limitations and honest status
- **Verified:** all 17 tests pass offline (scripted fake LLM): workflow, guards, rollback, HTTP validation, auth, history ordering, retrieval leakage, data splitting.
- **Verified live:** all three endpoints, prompt versioning/diff/restore, manual instruction, 50+ training edits (OpenRouter + SQLite).
- **Verified on the hosted deployment:** generate, improve-ai (≈14 s), improve-ai-manually, history, restore, and the admin-token 401 on both improve endpoints.
- **Learning gain not demonstrated:** two training rounds gave F1 0.253→0.259 and 0.251→0.232 on one-sample runs; the stronger 3-repeat eval (`docs/EVAL_ROUND3.md`) shows the auto-learned prompt is slightly *worse* than the seed (Δ F1 −0.024, 95% CI [−0.047, −0.005]). A single hand-written length rule did help (reply length 1.67×→1.24× human, F1 not detectably changed) and is now part of the seed prompt. Details in `docs/BEFORE_AFTER.md`.
- **Persistence:** the hosted app stores prompts in Supabase Postgres, so versions survive restarts. Without `DATABASE_URL` the app falls back to SQLite, which Render's free tier wipes on redeploy.
- PII redaction is regex-based: names and street addresses pass through.
- Token-F1 is a crude proxy; it rewards phrasing overlap, not correctness. Use `diagnosis`/diffs and human review for real decisions.
- Single gunicorn worker (edit lock is in-process); scale-out needs a DB-level lock or optimistic versioning.
- Self-editing can still drift or overfit to a few examples; guards reduce but don't remove that. Review `GET /prompt/diff`, and set `ADMIN_TOKEN` on any public deployment because `/improve-ai*` write to the live prompt.
- Business facts come from 15 synthetic chats and may be wrong in production.
- No language detection/handling beyond "reply in the client's language"; no conversation-state storage (the caller sends history).
