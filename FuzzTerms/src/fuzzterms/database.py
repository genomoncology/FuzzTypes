from abc import ABC, abstractmethod
from contextlib import contextmanager


class Database(ABC):
    def __init__(self, db_url: str, vss_enabled: bool, vss_dimensions: int):
        self.db_url = db_url
        self.vss_enabled = vss_enabled
        self.vss_dimensions = vss_dimensions

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def stats(self) -> dict:
        pass

    @abstractmethod
    def upsert(self, entity_dicts: list[dict], term_dicts: list[dict]):
        pass

    @abstractmethod
    def search(
        self, query: str, vector: list[float], limit: int
    ) -> list[dict]:
        pass


class SQLDatabase(Database, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sql = None

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
            self.sql.initialize(conn)
            conn.execute(
                f"CREATE VIRTUAL TABLE IF NOT EXISTS vss_terms USING "
                f"vss0(term_embedding({self.vss_dimensions}))"
            )

    def stats(self) -> int:
        with self.acquire() as conn:
            return self.sql.stats(conn)

    def upsert(self, entity_dicts: list[dict], term_dicts: list[dict]):
        with self.acquire() as conn:
            self.sql.upsert_entities(conn, entity_dicts)
            self.sql.upsert_terms(conn, term_dicts)

    def search(
        self, query: str, vector: list[float], limit: int
    ) -> list[dict]:
        with self.acquire() as conn:
            results = self.sql.fts_search(
                conn,
                query=query,
                vector=vector,
                limit=limit,
            )
            return results
