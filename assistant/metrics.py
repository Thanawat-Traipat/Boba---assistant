"""Cheap, deterministic quality signals. Not a substitute for human review (see README limitations).

token_f1      - word overlap with the real consultant reply (content/phrasing proxy).
length_ratio  - predicted words / real words; ~1.0 means the bot is as terse as the humans.
ai_isms       - count of assistant boilerplate / markdown / emoji, the "sounds like an AI" tells.
"""
import re

_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
_AI_PHRASES = ["i hope this helps", "certainly", "great question", "as an ai", "i understand your",
               "feel free to reach out", "i'd be happy to", "absolutely!", "don't hesitate"]


def _words(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def token_f1(pred, ref):
    p, r = _words(pred), _words(ref)
    if not p or not r:
        return 0.0
    common = 0
    pool = list(r)
    for w in p:
        if w in pool:
            pool.remove(w)
            common += 1
    if not common:
        return 0.0
    prec, rec = common / len(p), common / len(r)
    return 2 * prec * rec / (prec + rec)


def length_ratio(pred, ref):
    return len(_words(pred)) / max(1, len(_words(ref)))


def ai_isms(text):
    low = text.lower()
    n = sum(low.count(p) for p in _AI_PHRASES)
    n += len(_EMOJI.findall(text))
    n += len(re.findall(r"\*\*|^#{1,6} ", text, re.M))
    return n


def score(pred, ref):
    return {"f1": round(token_f1(pred, ref), 3), "lenRatio": round(length_ratio(pred, ref), 2),
            "aiIsms": ai_isms(pred), "words": len(_words(pred))}
