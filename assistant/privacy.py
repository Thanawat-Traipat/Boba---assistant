"""Best-effort PII redaction for anything we PERSIST or forward to the prompt editor.

Why: client chats can contain emails, phone numbers and passport/card numbers. Improvement edits
store a note about what triggered them (DB) and show real exchanges to the editor LLM; neither
should be able to bake a customer's personal details into the prompt history. Regexes are a
safety net, not a guarantee (names and addresses are NOT detected) - see README limitations.
"""
import re

_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[EMAIL]"),
    (re.compile(r"https?://\S+"), "[URL]"),
    (re.compile(r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)"), "[NUMBER]"),  # phones, long ids, card-like runs
    (re.compile(r"\b[A-Z]{1,2}\d{6,9}\b"), "[ID]"),                    # passport-style ids, e.g. AB1234567
]


def redact(text):
    if not isinstance(text, str):
        return text
    for pat, repl in _PATTERNS:
        text = pat.sub(repl, text)
    return text


def redact_history(history):
    return [{"role": h["role"], "message": redact(h["message"])} for h in history]
