import threading

from . import metrics, privacy, prompts
from .dataset import load_examples
from .llm import LLMError, extract_json
from .retrieval import Retriever


class BadRequest(ValueError):
    pass


def normalize_history(history, order):
    """Accept [{"role","message"}] in either order; return chronological (oldest first)."""
    if history is None:
        return []
    if not isinstance(history, list):
        raise BadRequest("chatHistory must be a list")
    clean = []
    for h in history:
        if not isinstance(h, dict) or not isinstance(h.get("message"), str):
            raise BadRequest("each chatHistory item needs a string 'message' and a 'role'")
        role = str(h.get("role", "")).lower()
        if role not in ("client", "consultant"):
            raise BadRequest("chatHistory role must be 'client' or 'consultant'")
        clean.append({"role": role, "message": h["message"]})
    if order == "newest_first":
        clean.reverse()
    elif order != "oldest_first":
        raise BadRequest("historyOrder must be 'newest_first' or 'oldest_first'")
    return clean


def normalize_client(client_seq):
    if isinstance(client_seq, str):
        client_seq = [client_seq]
    if (not isinstance(client_seq, list) or not client_seq
            or not all(isinstance(m, str) and m.strip() for m in client_seq)):
        raise BadRequest("clientSequence must be a non-empty string or list of non-empty strings")
    return [m.strip() for m in client_seq]


class Assistant:
    def __init__(self, cfg, store, llm, examples=None):
        self.cfg, self.store, self.llm = cfg, store, llm
        self.retriever = Retriever(examples or [])
        self._edit_lock = threading.Lock()  # serialises read-prompt -> LLM -> save so edits don't clobber
        store.ensure_seed(prompts.SEED_PROMPT)

    @classmethod
    def from_config(cls, cfg, store, llm):
        try:
            examples = load_examples(cfg.DATA_PATH)
        except FileNotFoundError:
            examples = []
        return cls(cfg, store, llm, examples)

    # -- generation -------------------------------------------------------
    def current_prompt(self):
        return self.store.latest()

    def _generate(self, prompt_text, history, client_seq, exclude_reply=None):
        shots = self.retriever.top(" ".join(client_seq), self.cfg.FEWSHOT_K, exclude_reply)
        user = prompts.build_generation_input(history, client_seq, shots)
        raw = self.llm.generate(prompt_text + prompts.OUTPUT_CONTRACT, user, temperature=0.7)
        reply = extract_json(raw).get("reply")
        if isinstance(reply, list):
            reply = "\n\n".join(str(r) for r in reply)
        if not isinstance(reply, str) or not reply.strip():
            raise LLMError("model JSON had no usable 'reply'")
        return reply.strip()

    def generate_reply(self, client_seq, history, order=None):
        client_seq = normalize_client(client_seq)
        history = normalize_history(history, order or self.cfg.HISTORY_ORDER)
        return self._generate(self.current_prompt()["content"], history, client_seq)

    # -- improvement ------------------------------------------------------
    def _edit(self, system, user):
        out = extract_json(self.llm.generate(system, user, temperature=0.2))
        return out.get("prompt"), out

    def improve(self, client_seq, history, consultant_reply, order=None):
        client_seq = normalize_client(client_seq)
        history = normalize_history(history, order or self.cfg.HISTORY_ORDER)
        if not isinstance(consultant_reply, str) or not consultant_reply.strip():
            raise BadRequest("consultantReply must be a non-empty string")
        with self._edit_lock:
            cur = self.current_prompt()
            predicted = self._generate(cur["content"], history, client_seq, exclude_reply=consultant_reply)
            new_prompt, meta = self._edit(
                prompts.EDITOR_PROMPT,
                prompts.build_editor_input(cur["content"], privacy.redact_history(history),
                                           [privacy.redact(m) for m in client_seq],
                                           privacy.redact(consultant_reply), privacy.redact(predicted),
                                           self.cfg.MAX_PROMPT_CHARS))
            result = {"predictedReply": predicted, "diagnosis": meta.get("diagnosis"),
                      "changes": meta.get("changes") or []}

            reason = prompts.validate_new_prompt(cur["content"], new_prompt, self.cfg)
            if not reason and new_prompt.strip() == cur["content"].strip():
                reason = "no change needed (predicted reply already matches the real one)"
                result["noChangeNeeded"] = True
            if not reason and self.cfg.VALIDATE_EDITS:
                before = metrics.token_f1(predicted, consultant_reply)
                after_reply = self._generate(new_prompt, history, client_seq, exclude_reply=consultant_reply)
                after = metrics.token_f1(after_reply, consultant_reply)
                result.update(f1Before=round(before, 3), f1After=round(after, 3))
                if after + 0.02 < before:
                    reason = f"edit made the reply worse (F1 {before:.2f} -> {after:.2f})"
            if reason:
                result.update(updatedPrompt=cur["content"], promptVersion=cur["version"],
                              changed=False, rejectedReason=reason)
                return result

            note = "auto: " + privacy.redact(" | ".join(client_seq))[:200]
            version = self.store.save(new_prompt, "auto", note)
            result.update(updatedPrompt=new_prompt, promptVersion=version, changed=True)
            return result

    def improve_manually(self, instructions):
        if not isinstance(instructions, str) or not instructions.strip():
            raise BadRequest("instructions must be a non-empty string")
        with self._edit_lock:
            cur = self.current_prompt()
            new_prompt, meta = self._edit(prompts.MANUAL_EDITOR_PROMPT,
                                          prompts.build_manual_input(cur["content"], instructions.strip()))
            reason = prompts.validate_new_prompt(cur["content"], new_prompt, self.cfg, allow_big_change=True)
            if reason:
                return {"updatedPrompt": cur["content"], "promptVersion": cur["version"],
                        "changed": False, "rejectedReason": reason}
            version = self.store.save(new_prompt, "manual", "manual: " + instructions.strip()[:200])
            return {"updatedPrompt": new_prompt, "promptVersion": version, "changed": True,
                    "changes": meta.get("changes") or []}

    def restore(self, version):
        with self._edit_lock:
            old = self.store.get(version)
            if not old:
                raise BadRequest(f"no such version {version}")
            new_version = self.store.save(old["content"], "restore", f"restore of v{version}")
            return {"promptVersion": new_version, "restoredFrom": version, "prompt": old["content"]}
