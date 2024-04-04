import sqlite3
from pathlib import Path

import aiosql

from fuzzimport import lazy_import
from fuzzterms import Collection, Config, SQLDatabase


class SQLiteDatabase(SQLDatabase):
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

    def initialize(self):
        with self.acquire() as conn:
            self.sql.initialize(conn)
            conn.execute(
                f"CREATE VIRTUAL TABLE IF NOT EXISTS vss_terms USING "
                f"vss0(vector({self.vss_dimensions}))"
            )
