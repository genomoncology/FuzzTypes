import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import aiosql

from fuzzterms import Database, lazy


class SQLiteDatabase(Database):
    name = "sqlite"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sql = aiosql.from_path(Path(__file__).parent / "sql", "sqlite3")

    def connect(self):
        db_url = self.path / self.config.db_url
        conn = sqlite3.connect(db_url)
        conn.row_factory = sqlite3.Row  # https://stackoverflow.com/a/3300514

        if self.config.vss_enabled:
            sqlite_vss = lazy.lazy_import("sqlite_vss")
            conn.enable_load_extension(True)
            sqlite_vss.load(conn)

        return conn

    @contextmanager
    def acquire(self, existing_connection=None):
        conn = existing_connection

        if conn is None:
            conn = self.connect()

        try:
            yield conn

            if not existing_connection:
                conn.commit()

        except Exception as e:  # pragma: no cover
            conn.rollback()
            raise e

        finally:
            if not existing_connection:
                conn.close()

    def initialize(self):
        with self.acquire() as conn:
            self.sql.init_tables(conn)
            conn.execute(
                f"CREATE VIRTUAL TABLE IF NOT EXISTS vss_terms USING "
                f"vss0(vector({self.config.vss_dimensions}))"
            )
            self.sql.init_triggers(conn)

    def stats(self) -> dict:
        with self.acquire() as conn:
            return dict(self.sql.stats(conn))

    def upsert(self, entity_dicts: list[dict], term_dicts: list[dict]):
        with self.acquire() as conn:
            entity_dicts = list(map(self._serialize_entity, entity_dicts))
            self.sql.upsert_entities(conn, entity_dicts)
            self.sql.upsert_terms(conn, term_dicts)

    def search(self, query: str, vector: list[float], limit: int):
        pass

    def hybrid_search(
        self, query: str, vector: list[float], limit: int
    ) -> list[dict]:
        with self.acquire() as conn:
            results = self.sql.hybrid_search(
                conn,
                query=query,
                vector=vector,
                limit=limit,
            )
            return list(results)

    @classmethod
    def _serialize_entity(cls, entity_dict: dict) -> dict:
        if "meta" in entity_dict and isinstance(entity_dict["meta"], dict):
            entity_dict = entity_dict.copy()
            entity_dict["meta"] = json.dumps(entity_dict["meta"])
        return entity_dict
