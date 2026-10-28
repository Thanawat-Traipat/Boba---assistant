"""Turn conversations.json into (history, client sequence, consultant reply) examples.

A "client sequence" is a run of consecutive inbound messages; the consultant reply is the run
of outbound messages that follows it. Chat history is everything before the client sequence,
in chronological order (oldest first).
"""
import json


def _runs(messages):
    run, direction = [], None
    for m in messages:
        if m["direction"] != direction and run:
            yield direction, run
            run = []
        direction = m["direction"]
        run.append(m["text"].strip())
    if run:
        yield direction, run


def build_examples(conversations):
    examples = []
    for conv in conversations:
        history = []  # chronological [{"role","message"}]
        runs = list(_runs(conv["conversation"]))
        for i, (direction, texts) in enumerate(runs):
            if direction == "in" and i + 1 < len(runs) and runs[i + 1][0] == "out":
                examples.append({
                    "contactId": conv["contact_id"],
                    "scenario": conv["scenario"],
                    "clientSequence": texts,
                    "chatHistory": list(history),
                    "consultantReply": "\n\n".join(runs[i + 1][1]),
                })
            role = "client" if direction == "in" else "consultant"
            history.extend({"role": role, "message": t} for t in texts)
    return examples


def load_examples(path):
    with open(path, encoding="utf-8") as f:
        return build_examples(json.load(f))


def split_by_conversation(examples, holdout_every=4):
    """Hold out whole conversations (never single turns) so eval never sees training chats."""
    ids = sorted({e["contactId"] for e in examples})
    test_ids = set(ids[holdout_every - 1::holdout_every])
    train = [e for e in examples if e["contactId"] not in test_ids]
    test = [e for e in examples if e["contactId"] in test_ids]
    return train, test
