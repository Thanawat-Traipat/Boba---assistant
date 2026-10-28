import os

from dotenv import load_dotenv

load_dotenv()


def _env(name, default=""):
    """Env var with surrounding whitespace removed (a pasted trailing newline once broke DATABASE_URL)."""
    return os.getenv(name, default).strip()


def _bool(name, default=False):
    return _env(name, str(default)).lower() in ("1", "true", "yes", "on")


class Config:
    LLM_PROVIDER = _env("LLM_PROVIDER", "gemini").lower()
    LLM_MODEL = _env("LLM_MODEL", "")
    GEMINI_API_KEY = _env("GEMINI_API_KEY", "")
    GROQ_API_KEY = _env("GROQ_API_KEY", "")
    ANTHROPIC_API_KEY = _env("ANTHROPIC_API_KEY", "")
    OPENROUTER_API_KEY = _env("OPENROUTER_API_KEY", "")

    DATABASE_URL = _env("DATABASE_URL", "")
    SQLITE_PATH = _env("SQLITE_PATH", "data/prompts.db")

    HISTORY_ORDER = _env("HISTORY_ORDER", "newest_first")
    FEWSHOT_K = int(_env("FEWSHOT_K", "3"))
    VALIDATE_EDITS = _bool("VALIDATE_EDITS")
    ADMIN_TOKEN = _env("ADMIN_TOKEN", "")

    DATA_PATH = _env("DATA_PATH", "data/conversations.json")
    MAX_PROMPT_CHARS = 5200  # ~1.5x the seed: cumulative-growth cap (round 1 doubled it)
    MIN_PROMPT_CHARS = 400
