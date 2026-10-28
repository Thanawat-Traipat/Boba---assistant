"""Thin LLM layer: one `generate(system, user, temperature)` method, several providers.

Plain HTTP via `requests` so there is no vendor SDK to keep in sync. Every provider is asked
for JSON; `extract_json` still tolerates code fences / chatter because models do that anyway.
"""
import json
import re
import time

import requests

DEFAULT_MODELS = {
    "gemini": "gemini-2.0-flash",
    "groq": "llama-3.3-70b-versatile",
    "anthropic": "claude-haiku-5-5",
}


class LLMError(RuntimeError):
    pass


def extract_json(text):
    """Parse a JSON object from model output, tolerating ```json fences and leading/trailing prose."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
    raise LLMError("model did not return valid JSON: " + text[:200])


def _post(url, headers, payload, timeout=60, retries=2):
    for attempt in range(retries + 1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.RequestException as e:
            if attempt == retries:
                raise LLMError(f"network error: {e}")
            time.sleep(1.5 * (attempt + 1))
            continue
        if r.status_code in (429, 500, 502, 503) and attempt < retries:
            time.sleep(2 * (attempt + 1))
            continue
        if r.status_code >= 400:
            raise LLMError(f"LLM HTTP {r.status_code}: {r.text[:300]}")
        return r.json()


class GeminiLLM:
    def __init__(self, key, model):
        self.key, self.model = key, model

    def generate(self, system, user, temperature=0.7):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        data = _post(url, {"x-goog-api-key": self.key}, {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"},
        })
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise LLMError(f"unexpected Gemini response: {str(data)[:300]}")


class GroqLLM:
    def __init__(self, key, model):
        self.key, self.model = key, model

    def generate(self, system, user, temperature=0.7):
        data = _post("https://api.groq.com/openai/v1/chat/completions",
                     {"Authorization": f"Bearer {self.key}"}, {
                         "model": self.model, "temperature": temperature,
                         "response_format": {"type": "json_object"},
                         "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                     })
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise LLMError(f"unexpected Groq response: {str(data)[:300]}")


class AnthropicLLM:
    def __init__(self, key, model):
        self.key, self.model = key, model

    def generate(self, system, user, temperature=0.7):
        data = _post("https://api.anthropic.com/v1/messages",
                     {"x-api-key": self.key, "anthropic-version": "2023-06-01"}, {
                         "model": self.model, "max_tokens": 4096, "temperature": temperature,
                         "system": system, "messages": [{"role": "user", "content": user}],
                     }, timeout=120)
        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError):
            raise LLMError(f"unexpected Anthropic response: {str(data)[:300]}")


class MockLLM:
    """Offline stub. Pass `handler(system, user) -> str` to script behaviour in tests."""

    def __init__(self, handler=None):
        self.handler = handler
        self.calls = []

    def generate(self, system, user, temperature=0.7):
        self.calls.append((system, user))
        if self.handler:
            return self.handler(system, user)
        return json.dumps({"reply": "Hi there! Thanks for reaching out. Which country are you applying from?"})


def get_llm(cfg):
    p = cfg.LLM_PROVIDER
    model = cfg.LLM_MODEL or DEFAULT_MODELS.get(p, "")
    keys = {"gemini": cfg.GEMINI_API_KEY, "groq": cfg.GROQ_API_KEY, "anthropic": cfg.ANTHROPIC_API_KEY}
    if p == "mock":
        return MockLLM()
    if p not in keys:
        raise LLMError(f"unknown LLM_PROVIDER '{p}'")
    if not keys[p]:
        raise LLMError(f"LLM_PROVIDER={p} but its API key is not set")
    return {"gemini": GeminiLLM, "groq": GroqLLM, "anthropic": AnthropicLLM}[p](keys[p], model)
