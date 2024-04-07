from lancedb import LanceDBConnection, connect

from fuzzterms import Database
from .table import EntitiesTable, TermsTable


class LanceDBDatabase(Database):
    name = "lancedb"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._conn = None
        self._terms = None
        self._entities = None

    @property
    def conn(self) -> LanceDBConnection:
        if self._conn is None:
            db_url = self.path / self.config.db_url
            self._conn = connect(uri=db_url)
        return self._conn

    @property
    def entities(self) -> EntitiesTable:
        if self._entities is None:
            self._entities = EntitiesTable.connect(self, self.conn)
        return self._entities

    @property
    def terms(self) -> TermsTable:
        if self._terms is None:
            self._terms = TermsTable.connect(self, self.conn)
        return self._terms

    def initialize(self):
        pass

    def update_indexes(self):
        self.entities.update_indexes()
        self.terms.update_indexes()

    def stats(self) -> dict:
        return {
            "entities": self.entities.count(),
            "terms": self.terms.count(),
        }

    def upsert(self, entity_dicts: list[dict], term_dicts: list[dict]):
        self.entities.add(entity_dicts)
        self.terms.add(term_dicts)

    def search(self, query: str, vector: list[float], limit: int):
        pass
