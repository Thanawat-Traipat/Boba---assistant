import os

from dotenv import load_dotenv

load_dotenv()


def _bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
    LLM_MODEL = os.getenv("LLM_MODEL", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

    DATABASE_URL = os.getenv("DATABASE_URL", "")
    SQLITE_PATH = os.getenv("SQLITE_PATH", "data/prompts.db")

    HISTORY_ORDER = os.getenv("HISTORY_ORDER", "newest_first")
    FEWSHOT_K = int(os.getenv("FEWSHOT_K", "3"))
    VALIDATE_EDITS = _bool("VALIDATE_EDITS")
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

    DATA_PATH = os.getenv("DATA_PATH", "data/conversations.json")
    MAX_PROMPT_CHARS = 5200  # ~1.5x the seed: cumulative-growth cap (round 1 doubled it)
    MIN_PROMPT_CHARS = 400
