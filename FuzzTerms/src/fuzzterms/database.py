from abc import ABC, abstractmethod


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
    def hybrid_search(
        self, query: str, vector: list[float], limit: int
    ) -> list[dict]:
        pass
