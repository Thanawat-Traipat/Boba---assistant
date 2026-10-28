"""Tiny dependency-free retriever: pick real consultant replies for similar client questions.

Used for few-shot examples at generation time, so the model copies the real tone and the real
facts instead of inventing them. Plain bag-of-words cosine is enough for ~130 exchanges.
"""
import math
import re
from collections import Counter

_STOP = set("the a an and or to of in on for is are i you it my me we do does can be have has with that this at as if so "
            "what how when where which your our will would there their they but not no yes just about from".split())


def _tokens(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOP and len(t) > 1]


class Retriever:
    def __init__(self, examples):
        self.examples = examples
        self.docs = [Counter(_tokens(" ".join(e["clientSequence"]))) for e in examples]
        df = Counter(t for d in self.docs for t in d)
        n = len(self.docs) or 1
        self.idf = {t: math.log((n + 1) / (c + 0.5)) for t, c in df.items()}

    def _vec(self, counter):
        return {t: c * self.idf.get(t, 1.0) for t, c in counter.items()}

    def top(self, query, k=3, exclude_reply=None):
        """exclude_reply: skip examples whose real reply equals this text, so improving on a known
        example can't leak the ground-truth answer into the prediction through few-shot."""
        if k <= 0 or not self.examples:
            return []
        q = self._vec(Counter(_tokens(query)))
        qn = math.sqrt(sum(v * v for v in q.values())) or 1.0
        scored = []
        for ex, doc in zip(self.examples, self.docs):
            if exclude_reply and ex["consultantReply"].strip() == exclude_reply.strip():
                continue
            d = self._vec(doc)
            dn = math.sqrt(sum(v * v for v in d.values())) or 1.0
            score = sum(v * d.get(t, 0.0) for t, v in q.items()) / (qn * dn)
            scored.append((score, ex))
        scored.sort(key=lambda s: -s[0])
        return [ex for score, ex in scored[:k] if score > 0.05]
