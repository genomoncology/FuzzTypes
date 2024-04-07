from pathlib import Path
from abc import ABC, abstractmethod
from fuzzterms import Config
from fuzzterms import lazy


class Database(ABC):
    def __init__(self, path: Path, config: Config):
        self.path: Path = path
        self.config: Config = config

    @abstractmethod
    def initialize(self):
        pass

    def update_indexes(self):
        pass

    @abstractmethod
    def stats(self) -> dict:
        pass

    @abstractmethod
    def upsert(self, entity_dicts: list[dict], term_dicts: list[dict]):
        pass

    @abstractmethod
    def search(self, query: str, vector: list[float], limit: int):
        pass

    @classmethod
    def construct(cls, path: Path, config: Config) -> "Database":
        options = {
            "sqlite": "fuzzterms.databases.SQLiteDatabase",
            "lancedb": "fuzzterms.databases.LanceDBDatabase",
        }
        backend = options.get(config.db_backend, config.db_backend)
        library_name, attr_name = backend.rsplit(".", maxsplit=1)
        db_class = lazy.lazy_import(library_name, attr_name)
        assert issubclass(db_class, cls)
        return db_class(path=path, config=config)
