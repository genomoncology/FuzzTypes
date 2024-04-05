import sqlite3
from contextlib import contextmanager
from pathlib import Path

import aiosql

from fuzzimport import lazy_import
from fuzzterms import Database


class SQLiteDatabase(Database):
    name = "sqlite"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sql = aiosql.from_path(Path(__file__).parent / "sql", "sqlite3")

    def connect(self):
        conn = sqlite3.connect(self.db_url)
        conn.row_factory = sqlite3.Row  # https://stackoverflow.com/a/3300514

        if self.vss_enabled:
            sqlite_vss = lazy_import("sqlite_vss")
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
                f"vss0(vector({self.vss_dimensions}))"
            )
            self.sql.init_triggers(conn)

    def stats(self) -> int:
        with self.acquire() as conn:
            return self.sql.stats(conn)

    def upsert(self, entity_dicts: list[dict], term_dicts: list[dict]):
        with self.acquire() as conn:
            self.sql.upsert_entities(conn, entity_dicts)
            self.sql.upsert_terms(conn, term_dicts)

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
