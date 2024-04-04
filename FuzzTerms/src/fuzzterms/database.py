from abc import ABC, abstractmethod
from contextlib import contextmanager

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from fuzzterms import Collection, Config


class Database(ABC):
    def __init__(self, collection: "Collection"):
        self.collection = collection

    @property
    def config(self) -> "Config":
        return self.collection.config

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


class SQLDatabase(Database, ABC):
    def __init__(self, collection: "Collection"):
        super().__init__(collection)
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
            self.sql.initialize(conn, **self.config.model_dump())

    def stats(self) -> int:
        with self.acquire() as conn:
            return self.sql.stats(conn)

    def upsert(self, entity_dicts: list[dict], term_dicts: list[dict]):
        with self.acquire() as conn:
            self.sql.upsert_entities(conn, entity_dicts)
            self.sql.upsert_terms(conn, term_dicts)