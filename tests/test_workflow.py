import json

import pytest

from app import create_app
from assistant import prompts
from assistant.config import Config
from assistant.dataset import build_examples, load_examples, split_by_conversation
from assistant.llm import MockLLM, extract_json
from assistant.retrieval import Retriever
from assistant.service import Assistant, normalize_history
from assistant.store import PromptStore

EDIT_MARK = "- Keep it under 30 words."


class TestCfg(Config):
    DATABASE_URL = ""
    ADMIN_TOKEN = ""
    VALIDATE_EDITS = False
    FEWSHOT_K = 2


def make(tmp_path, handler=None, **over):
    cfg = type("C", (TestCfg,), {"SQLITE_PATH": str(tmp_path / "t.db"), **over})
    llm = MockLLM(handler)
    examples = load_examples("data/conversations.json")
    a = Assistant(cfg, PromptStore(cfg), llm, examples)
    return cfg, llm, a


def editor_handler(new_prompt_fn=lambda p: p + "\n" + EDIT_MARK):
    """Fake LLM: answers editor calls with an edited prompt, generation calls with a fixed reply."""
    def h(system, user):
        if system.startswith("You are a prompt editor"):
            cur = user.split("CURRENT PROMPT:\n<<<\n", 1)[1].split("\n>>>", 1)[0]
            return json.dumps({"diagnosis": "too long", "changes": ["added brevity rule"], "prompt": new_prompt_fn(cur)})
        return json.dumps({"reply": "Yes, you can apply from there!"})
    return h


# ---- data -------------------------------------------------------------------------------
def test_dataset_examples_and_history_order():
    ex = load_examples("data/conversations.json")
    assert len(ex) >= 100
    first = ex[0]
    assert first["chatHistory"] == []
    second = ex[1]
    assert [h["role"] for h in second["chatHistory"]] == ["client", "consultant"]  # chronological
    assert all(e["consultantReply"] for e in ex)


def test_split_never_mixes_conversations():
    train, test = split_by_conversation(load_examples("data/conversations.json"))
    assert not ({e["contactId"] for e in train} & {e["contactId"] for e in test})
    assert test


def test_consecutive_messages_group_into_sequences():
    convo = [{"contact_id": "X", "scenario": "s", "conversation": [
        {"direction": "in", "text": "a"}, {"direction": "in", "text": "b"},
        {"direction": "out", "text": "c"}, {"direction": "out", "text": "d"}]}]
    ex = build_examples(convo)
    assert ex == [{"contactId": "X", "scenario": "s", "clientSequence": ["a", "b"],
                   "chatHistory": [], "consultantReply": "c\n\nd"}]


def test_history_newest_first_is_reversed_to_chronological():
    h = [{"role": "consultant", "message": "second"}, {"role": "client", "message": "first"}]
    assert [m["message"] for m in normalize_history(h, "newest_first")] == ["first", "second"]
    assert [m["message"] for m in normalize_history(h, "oldest_first")] == ["second", "first"]


def test_retriever_finds_relevant_and_excludes_leak():
    ex = load_examples("data/conversations.json")
    r = Retriever(ex)
    hits = r.top("how much is the service fee price", 3)
    assert hits
    leaked = hits[0]["consultantReply"]
    assert all(h["consultantReply"] != leaked for h in r.top("how much is the service fee price", 3, exclude_reply=leaked))


def test_extract_json_tolerates_fences_and_prose():
    assert extract_json('```json\n{"reply": "hi"}\n```') == {"reply": "hi"}
    assert extract_json('Sure! {"reply": "hi"} hope that helps') == {"reply": "hi"}


# ---- service ----------------------------------------------------------------------------
def test_generate_uses_live_db_prompt_and_contract(tmp_path):
    cfg, llm, a = make(tmp_path, editor_handler())
    a.store.save(a.current_prompt()["content"] + "\nALWAYS USE EMOJIS.", "manual", "t")
    assert a.generate_reply("Can I apply from Bali?", []) == "Yes, you can apply from there!"
    system, user = llm.calls[-1]
    assert "ALWAYS USE EMOJIS." in system
    assert '{"reply":' in system  # output contract appended by code
    assert "NEW CLIENT MESSAGE(S):\nCan I apply from Bali?" in user


def test_improve_saves_new_version_and_returns_spec_fields(tmp_path):
    cfg, llm, a = make(tmp_path, editor_handler())
    before = a.current_prompt()["version"]
    out = a.improve("Can I apply from Bali?", [], "Yes! Apply in Jakarta.")
    assert out["predictedReply"] and out["changed"] is True
    assert EDIT_MARK in out["updatedPrompt"]
    assert out["promptVersion"] == before + 1
    assert a.current_prompt()["content"] == out["updatedPrompt"]


def test_improve_rejects_destructive_edit(tmp_path):
    cfg, llm, a = make(tmp_path, editor_handler(lambda p: "Be nice. " * 60))  # drops HARD RULES
    before = a.current_prompt()
    out = a.improve("hi", [], "Hello!")
    assert out["changed"] is False and "HARD RULES" in out["rejectedReason"]
    assert a.current_prompt()["version"] == before["version"]  # nothing saved


def test_improve_rejects_non_surgical_rewrite(tmp_path):
    cfg, llm, a = make(tmp_path, editor_handler(lambda p: p + ("\nextra rule " * 200)))
    assert "surgical" in a.improve("hi", [], "Hello!")["rejectedReason"] or "too long" in a.improve("hi", [], "Hello!")["rejectedReason"]


def test_improve_no_change_does_not_create_version(tmp_path):
    cfg, llm, a = make(tmp_path, editor_handler(lambda p: p))
    out = a.improve("hi", [], "Hello!")
    assert out["changed"] is False and out["noChangeNeeded"]
    assert len(a.store.history()) == 1


def test_validate_edits_rejects_regression(tmp_path):
    calls = {"n": 0}

    def h(system, user):
        if system.startswith("You are a prompt editor"):
            cur = user.split("CURRENT PROMPT:\n<<<\n", 1)[1].split("\n>>>", 1)[0]
            return json.dumps({"prompt": cur + "\n- be vague."})
        calls["n"] += 1  # first generation good, regeneration bad
        return json.dumps({"reply": "Yes you can apply from Jakarta" if calls["n"] == 1 else "Maybe."})

    cfg, llm, a = make(tmp_path, h, VALIDATE_EDITS=True)
    out = a.improve("Can I apply from Bali?", [], "Yes you can apply from Jakarta")
    assert out["changed"] is False and "worse" in out["rejectedReason"]


def test_manual_improve_and_restore(tmp_path):
    def h(system, user):
        cur = user.split("CURRENT PROMPT:\n<<<\n", 1)[1].split("\n>>>", 1)[0]
        return json.dumps({"changes": ["emoji rule"], "prompt": cur + "\n- Use lots of emojis."})
    cfg, llm, a = make(tmp_path, h)
    out = a.improve_manually("send lots of emojis")
    assert out["changed"] and "emojis" in out["updatedPrompt"]
    r = a.restore(1)
    assert r["promptVersion"] == 3 and a.current_prompt()["content"] == prompts.SEED_PROMPT


# ---- HTTP -------------------------------------------------------------------------------
@pytest.fixture
def client(tmp_path):
    cfg, llm, a = make(tmp_path, editor_handler(), ADMIN_TOKEN="s3cret")
    return create_app(a, cfg).test_client()


def test_http_generate_reply_matches_spec(client):
    r = client.post("/generate-reply", json={
        "clientSequence": "I'm American and currently in Bali. Can I apply from Indonesia?",
        "chatHistory": [{"role": "consultant", "message": "Hi there!"}, {"role": "client", "message": "Hello"}]})
    assert r.status_code == 200 and set(r.json) == {"aiReply"}


def test_http_validation_errors(client):
    assert client.post("/generate-reply", json={}).status_code == 400
    assert client.post("/generate-reply", data="nope").status_code == 400
    assert client.post("/generate-reply", json={"clientSequence": "x", "chatHistory": [{"role": "bot", "message": "y"}]}).status_code == 400
    assert client.get("/nope").status_code == 404


def test_http_admin_token_guards_mutations(client):
    body = {"instructions": "be concise"}
    assert client.post("/improve-ai-manually", json=body).status_code == 401
    ok = client.post("/improve-ai-manually", json=body, headers={"X-Admin-Token": "s3cret"})
    assert ok.status_code == 200 and "updatedPrompt" in ok.json
    assert client.post("/generate-reply", json={"clientSequence": "hi"}).status_code == 200  # open


def test_http_improve_and_diff(client):
    h = {"X-Admin-Token": "s3cret"}
    r = client.post("/improve-ai", headers=h, json={"clientSequence": "hi", "chatHistory": [], "consultantReply": "Hello!"})
    assert r.status_code == 200 and {"predictedReply", "updatedPrompt"} <= set(r.json)
    d = client.get("/prompt/diff?from=1&to=2").json
    assert "+" + EDIT_MARK in d["diff"]
    assert len(client.get("/prompt/history").json["versions"]) == 2
