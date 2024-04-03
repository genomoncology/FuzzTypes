from abc import ABC, abstractmethod
from contextlib import contextmanager

from fuzzterms import Collection


class Database(ABC):
    def __init__(self, collection: Collection):
        self.collection: Collection = collection

    @classmethod
    def construct(cls, collection: Collection):
        if collection.config.db_backend == "sqlite":
            from fuzzterms.databases import SQLiteDatabase

            return SQLiteDatabase(collection)
        else:
            raise NotImplementedError(
                f"Database not supported: {collection.config.db_backend}"
            )

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def entity_count(self) -> int:
        pass


class SQLDatabase(Database, ABC):
    def __init__(self, collection: Collection):
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
            self.sql.initialize(conn)

    def entity_count(self) -> int:
        with self.acquire() as conn:
            return self.sql.entity_count(conn)
