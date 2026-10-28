"""Batch tools for the self-learning loop.

  python -m scripts.lab train --limit 30 --sleep 4     # run /improve-ai logic over TRAIN conversations
  python -m scripts.lab eval --versions 1 latest       # compare prompt versions on HELD-OUT conversations
  python -m scripts.lab eval --versions 1 latest --report docs/EVAL_REPORT.md

Why a split: every 4th conversation is held out (whole conversations, never single turns) so the
reported numbers come from chats the prompt-editor never saw. The few-shot retriever used here is
also built from train conversations only, otherwise eval would leak the answers.
"""
import argparse
from itertools import zip_longest
import statistics
import time

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


def cmd_eval(a, test, args):
    rows = {}
    ex = test[: args.limit] if args.limit else test
    for v in args.versions:
        p = _version(a.store, v)
        results = []
        for e in ex:
            reply = a._generate(p["content"], e["chatHistory"], e["clientSequence"])
            results.append((e, reply, metrics.score(reply, e["consultantReply"])))
            time.sleep(args.sleep)
        rows[f"v{p['version']}"] = results
    names = list(rows)
    lines = ["| prompt | n | token-F1 | length ratio (1.0 = as terse as humans) | AI-isms / reply |", "|---|---|---|---|---|"]
    for name, res in rows.items():
        lines.append(f"| {name} | {len(res)} | {statistics.mean(r[2]['f1'] for r in res):.3f} | "
                     f"{statistics.mean(r[2]['lenRatio'] for r in res):.2f} | "
                     f"{statistics.mean(r[2]['aiIsms'] for r in res):.2f} |")
    out = "\n".join(lines)
    out += "\n\n### Side-by-side samples\n"
    for i, e in enumerate(ex[: args.samples]):
        out += f"\n**{e['contactId']} - client:** {' / '.join(e['clientSequence'])}\n\n- **real:** {e['consultantReply']!r}\n"
        for n in names:
            out += f"- **{n}:** {rows[n][i][1]!r}  _(F1 {rows[n][i][2]['f1']})_\n"
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
    e.add_argument("--limit", type=int, default=0)
    e.add_argument("--samples", type=int, default=5)
    e.add_argument("--sleep", type=float, default=1.0)
    e.add_argument("--report")
    args = ap.parse_args()
    a, train, test = build(Config)
    print(f"{len(train)} train examples, {len(test)} held-out examples")
    cmd_train(a, train, args) if args.cmd == "train" else cmd_eval(a, test, args)


if __name__ == "__main__":
    main()
