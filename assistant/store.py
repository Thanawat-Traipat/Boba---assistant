"""Prompt storage with full version history.

Postgres (Neon / Supabase) when DATABASE_URL is set, otherwise a local SQLite file. The active
prompt is simply the highest version number, so every edit is append-only: nothing is ever
overwritten and any version can be restored (restore = append a copy of an old version).
"""
import sqlite3
import threading
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS prompt_versions (
    version     INTEGER PRIMARY KEY,
    kind        TEXT NOT NULL,      -- chatbot prompt name, e.g. "chatbot"
    content     TEXT NOT NULL,
    source      TEXT NOT NULL,      -- seed | auto | manual | restore
    note        TEXT,               -- what triggered the edit (example summary / reviewer instructions)
    created_at  DOUBLE PRECISION NOT NULL
)
"""


class PromptStore:
    def __init__(self, cfg):
        self.pg = bool(cfg.DATABASE_URL)
        self.cfg = cfg
        self._lock = threading.Lock()
        if not self.pg:
            self._sqlite = sqlite3.connect(cfg.SQLITE_PATH, check_same_thread=False)
            self._sqlite.row_factory = sqlite3.Row
        self._exec(SCHEMA.replace("DOUBLE PRECISION", "REAL") if not self.pg else SCHEMA)

    # -- backend plumbing -------------------------------------------------
    def _exec(self, sql, params=(), fetch=False):
        with self._lock:
            if self.pg:
                import psycopg
                from psycopg.rows import dict_row
                with psycopg.connect(self.cfg.DATABASE_URL, row_factory=dict_row) as conn:
                    cur = conn.execute(sql.replace("?", "%s"), params)
                    return cur.fetchall() if fetch else None
            cur = self._sqlite.execute(sql, params)
            self._sqlite.commit()
            return [dict(r) for r in cur.fetchall()] if fetch else None

    # -- API --------------------------------------------------------------
    def latest(self, kind="chatbot"):
        rows = self._exec("SELECT * FROM prompt_versions WHERE kind = ? ORDER BY version DESC LIMIT 1",
                          (kind,), fetch=True)
        return rows[0] if rows else None

    def get(self, version, kind="chatbot"):
        rows = self._exec("SELECT * FROM prompt_versions WHERE kind = ? AND version = ?",
                          (kind, version), fetch=True)
        return rows[0] if rows else None

    def history(self, kind="chatbot", limit=50):
        return self._exec("SELECT version, source, note, created_at, LENGTH(content) AS chars "
                          "FROM prompt_versions WHERE kind = ? ORDER BY version DESC LIMIT ?",
                          (kind, limit), fetch=True)

    def save(self, content, source, note=None, kind="chatbot"):
        """Append a new version and return its number."""
        rows = self._exec("SELECT COALESCE(MAX(version), 0) + 1 AS v FROM prompt_versions", fetch=True)
        version = rows[0]["v"]
        self._exec("INSERT INTO prompt_versions (version, kind, content, source, note, created_at) "
                   "VALUES (?, ?, ?, ?, ?, ?)", (version, kind, content, source, note, time.time()))
        return version

    def ensure_seed(self, seed_prompt, kind="chatbot"):
        if not self.latest(kind):
            self.save(seed_prompt, "seed", "initial prompt", kind)
