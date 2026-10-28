import difflib
import hmac

from flask import Flask, jsonify, request

from assistant.config import Config
from assistant.llm import LLMError, get_llm
from assistant.service import Assistant, BadRequest
from assistant.store import PromptStore


def create_app(assistant=None, cfg=Config):
    app = Flask(__name__)
    state = {"assistant": assistant, "error": None}

    def get_assistant():
        # Lazy so the server (and /health) still boots with a clear error if config is incomplete.
        if state["assistant"] is None:
            try:
                state["assistant"] = Assistant.from_config(cfg, PromptStore(cfg), get_llm(cfg))
                state["error"] = None
            except Exception as e:  # noqa: BLE001
                state["error"] = str(e)
                raise
        return state["assistant"]

    def require_admin():
        if cfg.ADMIN_TOKEN:
            sent = request.headers.get("X-Admin-Token", "")
            if not hmac.compare_digest(sent, cfg.ADMIN_TOKEN):
                return jsonify(error="missing or invalid X-Admin-Token"), 401

    def body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise BadRequest("request body must be a JSON object")
        return data

    @app.errorhandler(BadRequest)
    def _bad(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(LLMError)
    def _llm(e):
        return jsonify(error=f"LLM problem: {e}"), 502

    @app.errorhandler(Exception)
    def _other(e):
        if hasattr(e, "code") and isinstance(e.code, int):  # werkzeug HTTPException (404, 405, ...)
            return jsonify(error=getattr(e, "description", str(e))), e.code
        app.logger.exception("unhandled error")
        return jsonify(error=str(e) if state["error"] else "internal error"), 503 if state["error"] else 500

    @app.get("/")
    def index():
        return jsonify(service="BOBALAB support assistant", status="ok", endpoints={
            "POST /generate-reply": "reply to a client message",
            "POST /improve-ai": "learn from a real consultant reply",
            "POST /improve-ai-manually": "apply reviewer instructions",
            "GET /prompt": "active prompt", "GET /prompt/history": "version list",
            "GET /prompt/diff?from=1&to=2": "unified diff between versions",
            "POST /prompt/restore": "roll back to a version"})

    @app.get("/health")
    def health():
        return jsonify(status="ok", provider=cfg.LLM_PROVIDER, db="postgres" if cfg.DATABASE_URL else "sqlite")

    @app.post("/generate-reply")
    def generate_reply():
        d = body()
        a = get_assistant()
        reply = a.generate_reply(d.get("clientSequence"), d.get("chatHistory"), d.get("historyOrder"))
        return jsonify(aiReply=reply)

    @app.post("/improve-ai")
    def improve_ai():
        denied = require_admin()
        if denied:
            return denied
        d = body()
        return jsonify(get_assistant().improve(d.get("clientSequence"), d.get("chatHistory"),
                                               d.get("consultantReply"), d.get("historyOrder")))

    @app.post("/improve-ai-manually")
    def improve_manually():
        denied = require_admin()
        if denied:
            return denied
        return jsonify(get_assistant().improve_manually(body().get("instructions")))

    @app.get("/prompt")
    def prompt():
        p = get_assistant().current_prompt()
        return jsonify(version=p["version"], source=p["source"], prompt=p["content"])

    @app.get("/prompt/history")
    def history():
        return jsonify(versions=get_assistant().store.history())

    @app.get("/prompt/diff")
    def diff():
        store = get_assistant().store
        latest = store.latest()["version"]
        try:
            to_v = int(request.args.get("to", latest))
            from_v = int(request.args.get("from", to_v - 1))
        except ValueError:
            raise BadRequest("from/to must be integers")
        a, b = store.get(from_v), store.get(to_v)
        if not a or not b:
            raise BadRequest("unknown version")
        lines = difflib.unified_diff(a["content"].splitlines(), b["content"].splitlines(),
                                     f"v{from_v}", f"v{to_v}", lineterm="")
        return jsonify(**{"from": from_v, "to": to_v, "diff": "\n".join(lines)})

    @app.post("/prompt/restore")
    def restore():
        denied = require_admin()
        if denied:
            return denied
        v = body().get("version")
        if not isinstance(v, int):
            raise BadRequest("version must be an integer")
        return jsonify(get_assistant().restore(v))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
