import sqlite3
from pathlib import Path

import aiosql

from fuzzimport import lazy_import
from fuzzterms import Collection, Config, SQLDatabase


class SQLiteDatabase(SQLDatabase):
    name = "sqlite"

    def __init__(self, collection: Collection):
        super().__init__(collection)
        self.db_path: str = str(collection.path / self.config.db_url)
        self.sql = aiosql.from_path(Path(__file__).parent / "sql", "sqlite3")

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # https://stackoverflow.com/a/3300514

        if self.config.vss_enabled:
            sqlite_vss = lazy_import("sqlite_vss")
            conn.enable_load_extension(True)
            sqlite_vss.load(conn)

        return conn
