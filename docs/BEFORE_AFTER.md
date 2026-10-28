# Before / after improvement examples

All outputs below are real runs (LLM: `anthropic/claude-haiku-5.5` via OpenRouter, temperature 0.7 for replies, 0.2 for the editor).
Held-out = 24 client turns from conversations the editor never saw (every 4th conversation). Full tables: `EVAL_ROUND1.md`, `EVAL_ROUND2.md`.
Replies are sampled, so one-off numbers vary by a few thousandths between runs; I re-ran v1 and got 0.253 vs 0.251.

## Example 1 - manual instruction (the assignment's emoji test), then rollback

Instruction: `"Send lots of emojis 😀😃😄😁😆🥹😅😂🤣"` to `POST /improve-ai-manually`. Client: "How long does the DTV process take if I apply from Malaysia?"

- **Before (v1):** "Our legal team reviews your documents within 1-2 business days, and that review is free. The embassy's processing time after submission can vary, so our team will confirm that part for your case. You can start by uploading your documents here: [APP_LINK]"
- **Prompt change (`GET /prompt/diff?from=1&to=2`)** - one line replaced, nothing else touched:
  ```
  -- Emojis: rare. At most one, and only to celebrate good news or after a thank-you.
  +- Emojis: use plenty, sprinkled through your replies, drawing from 😀😃😄😁😆🥹😅😂🤣.
  ```
- **After (v2):** "Happy to help with that 😀 I don't want to guess at the exact timing for Malaysia, so our legal team will confirm it for your case. The document review itself takes 1-2 business days and is free, and you only pay once it's approved 😄 Are you thinking of the remote work route or a soft-power one like Muay Thai or cooking?"
- **After `POST /prompt/restore {"version": 1}` (v3):** emoji-free again.
- **Verdict: works as intended.** The live DB prompt is used on the next call, the edit is surgical (1 line), and rollback works. Side observation: the bot *deflects* on processing time although the sample chats say ~10 business days for Indonesia and 10-14 for Malaysia/Vietnam; that fact is missing from the seed prompt (a real improvement opportunity).

## Example 2 - automatic learning, round 1: it "worked" but overfit (a failure I found and fixed)

Setup: ran `/improve-ai` logic over the first 20 training examples (they came from only 3 conversations), producing v2..v20.

- Prompt grew **3,431 → 6,663 chars (+94%)**, and several additions were scripted answers for those exact chats (e.g. one bullet that scripts the whole "rejected application" conversation).
- Held-out result: token-F1 **0.253 → 0.259** (noise-level), reply length **1.64× → 1.46×** the human reply length, "AI-isms" 0.08 → 0.00.
- **Verdict: not a real improvement.** The only reliable effect was fewer AI-sounding phrases. The prompt was bloating and memorising.

**Fixes I made from this evidence:** (1) training examples are now interleaved across conversations; (2) cumulative size cap of 5,200 chars (~1.5× the seed) that the editor is told about and must respect by merging/deleting lines; (3) the editor prompt now forbids per-scenario scripts.

## Example 3 - automatic learning, round 2 (after the fixes)

Setup: fresh DB, 30 interleaved examples → v2..v23 (7 further edits were rejected for being 4-34 chars over the cap).

- Prompt stayed within budget: 3,431 → 5,198 chars (cap working; no scripted scenarios).
- Held-out: token-F1 **0.251 → 0.232**, length **1.57× → 1.54×**, AI-isms 0 → 0.
- Best case, client: "Hi, I'm a freelance graphic designer. Can I apply for DTV?" Real: asks nationality + where registered.
  - v1: "Yes, freelancers can usually apply under the remote worker route as long as your income comes from clients outside Thailand. Are you currently living outside Thailand, and which country would you apply from?" (F1 0.25)
  - v23: "Hi! Yes, freelance work can fit the remote worker route for the DTV. What's your nationality, and which country are you planning to apply from?" (F1 0.375) - shorter, asks the same question the human did.
- Worst case, client: "I'm German. My business is registered in Germany. I have clients from various countries." (F1 -0.13 vs v1): v23 asks a location question where v1 answered; the real reply states a requirement then asks where to submit.
- **Verdict: no measurable improvement on this metric.** Honest reading: with 24 held-out turns, one reference reply per turn and an overlap metric, I cannot distinguish a −0.02 change from noise, and the learning loop did not clearly move reply length (still ~1.5× too long) or accuracy.

## What I conclude / what I'd do next
- The mechanics (store, edit, diff, guard, rollback, manual instructions) are verified live. The *quality gain from auto-learning on 15 synthetic chats is not demonstrated*.
- Likely limits: facts the human replies state but the prompt lacks (translations, freelancer documents, processing times) can't be inferred from one example; one-example edits are noisy.
- Next: batch several examples per edit instead of one; a length-targeted rule (a deterministic word limit, since the bot is consistently ~50% too long); an LLM judge or human review instead of token-F1; load the missing business facts into a structured knowledge section; more data.
