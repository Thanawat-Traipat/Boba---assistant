"""Batch tools for the self-learning loop.

  python -m scripts.lab train --limit 30 --sleep 1        # run /improve-ai logic over TRAIN conversations
  python -m scripts.lab eval --versions 1 latest --repeats 3 --report docs/EVAL_REPORT.md
  python -m scripts.lab eval --versions 1 --rule "Hard cap: 40 words." --repeats 3   # test a candidate rule

Why a split: every 4th conversation is held out (whole conversations, never single turns) so the
reported numbers come from chats the prompt-editor never saw. The few-shot retriever used here is
also built from train conversations only, otherwise eval would leak the answers.

Why repeats + CIs: replies are sampled at temperature 0.7 and each turn has ONE reference reply,
so a single run's F1 moves by ~0.02 for no reason. Each arm is generated `--repeats` times, scores
are averaged per turn, and the difference to the first arm is reported with a paired bootstrap
95% CI over turns. If the CI contains 0, treat the change as "not demonstrated".
"""
import argparse
import random
import statistics
import time
from itertools import zip_longest

from assistant import metrics
from assistant.config import Config
from assistant.dataset import load_examples, split_by_conversation
from assistant.llm import get_llm
from assistant.service import Assistant
from assistant.store import PromptStore


def build(cfg):
    train, test = split_by_conversation(load_examples(cfg.DATA_PATH))
    return Assistant(cfg, PromptStore(cfg), get_llm(cfg), train), train, test


def cmd_train(a, train, args):
    # Round-robin across conversations: round 1 trained on 3 chats in a row and overfit to them.
    by_conv = {}
    for e in train:
        by_conv.setdefault(e["contactId"], []).append(e)
    ex = [e for tup in zip_longest(*by_conv.values()) for e in tup if e]
    ex = ex[: args.limit] if args.limit else ex
    for epoch in range(args.epochs):
        for i, e in enumerate(ex, 1):
            try:
                out = a.improve(e["clientSequence"], e["chatHistory"], e["consultantReply"], order="oldest_first")
            except Exception as err:  # keep going: one bad LLM call shouldn't end a long run
                print(f"[{epoch}:{i}/{len(ex)}] {e['contactId']} ERROR {err}")
                continue
            status = f"v{out['promptVersion']} changed" if out["changed"] else f"skip ({out.get('rejectedReason')})"
            print(f"[{epoch}:{i}/{len(ex)}] {e['contactId']} {status}")
            time.sleep(args.sleep)


def _version(store, v):
    return store.latest() if v == "latest" else store.get(int(v))


def _generate_retry(a, prompt, e, tries=4):
    for t in range(tries):
        try:
            return a._generate(prompt, e["chatHistory"], e["clientSequence"])
        except Exception as err:  # transient LLM/network error: back off, don't abort a long eval
            if t == tries - 1:
                print("  gave up on one call:", str(err)[:120])
                return None
            time.sleep(3 * (t + 1))


def paired_bootstrap(diffs, n=4000, seed=0):
    """Mean of per-turn differences and its 95% percentile CI."""
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choices(diffs, k=len(diffs))) for _ in range(n))
    return statistics.mean(diffs), means[int(0.025 * n)], means[int(0.975 * n)]


def cmd_eval(a, test, args):
    ex = test[: args.limit] if args.limit else test
    arms = []  # (name, prompt text)
    for v in args.versions:
        p = _version(a.store, v)
        arms.append((f"v{p['version']}", p["content"]))
    if args.rule:
        arms.append((f"{arms[0][0]}+rule", arms[0][1].rstrip() + "\n- " + args.rule))

    # results[arm][turn] = list of score dicts, one per repeat
    results = {name: [[] for _ in ex] for name, _ in arms}
    replies = {name: [None] * len(ex) for name, _ in arms}
    for r in range(args.repeats):
        for name, prompt in arms:
            for i, e in enumerate(ex):
                reply = _generate_retry(a, prompt, e)
                if reply is None:
                    continue
                results[name][i].append(metrics.score(reply, e["consultantReply"]))
                if replies[name][i] is None:
                    replies[name][i] = reply
                time.sleep(args.sleep)
        print(f"repeat {r + 1}/{args.repeats} done")

    def per_turn(name, key):  # mean over repeats for each turn (turns with no successful call dropped)
        return [statistics.mean(s[key] for s in turn) if turn else None for turn in results[name]]

    base = arms[0][0]
    lines = ["| prompt | turns | token-F1 | Δ F1 vs " + base + " (95% CI) | length ratio (1.0 = as terse as humans) | AI-isms / reply |",
             "|---|---|---|---|---|---|"]
    for name, _ in arms:
        f1 = per_turn(name, "f1")
        ok = [i for i, v in enumerate(f1) if v is not None and per_turn(base, "f1")[i] is not None]
        delta = "-"
        if name != base and ok:
            m, lo, hi = paired_bootstrap([f1[i] - per_turn(base, "f1")[i] for i in ok])
            verdict = "" if lo <= 0 <= hi else (" ▲" if m > 0 else " ▼")
            delta = f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]{verdict}"
        good = [v for v in f1 if v is not None]
        lines.append(f"| {name} | {len(good)} | {statistics.mean(good):.3f} | {delta} | "
                     f"{statistics.mean(v for v in per_turn(name, 'lenRatio') if v is not None):.2f} | "
                     f"{statistics.mean(v for v in per_turn(name, 'aiIsms') if v is not None):.2f} |")
    out = "\n".join(lines)
    out += (f"\n\n{args.repeats} repeat(s) per turn, temperature 0.7; ▲/▼ = 95% CI excludes 0, no mark = "
            "not distinguishable from noise.\n\n### Side-by-side samples (first repeat)\n")
    for i, e in enumerate(ex[: args.samples]):
        out += f"\n**{e['contactId']} - client:** {' / '.join(e['clientSequence'])}\n\n- **real:** {e['consultantReply']!r}\n"
        for n, _ in arms:
            if replies[n][i] is not None and results[n][i]:
                out += f"- **{n}:** {replies[n][i]!r}  _(F1 {results[n][i][0]['f1']})_\n"
    print(out)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write("# Held-out evaluation\n\n" + out)
        print("wrote", args.report)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("--limit", type=int, default=0)
    t.add_argument("--epochs", type=int, default=1)
    t.add_argument("--sleep", type=float, default=2.0, help="seconds between calls (free-tier rate limits)")
    e = sub.add_parser("eval")
    e.add_argument("--versions", nargs="+", default=["1", "latest"])
    e.add_argument("--rule", help="extra prompt line appended to the FIRST version, evaluated as its own arm")
    e.add_argument("--repeats", type=int, default=3)
    e.add_argument("--limit", type=int, default=0)
    e.add_argument("--samples", type=int, default=5)
    e.add_argument("--sleep", type=float, default=0.2)
    e.add_argument("--report")
    args = ap.parse_args()
    a, train, test = build(Config)
    print(f"{len(train)} train examples, {len(test)} held-out examples")
    cmd_train(a, train, args) if args.cmd == "train" else cmd_eval(a, test, args)


if __name__ == "__main__":
    main()
