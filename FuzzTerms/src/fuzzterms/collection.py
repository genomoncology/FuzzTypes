from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from fuzzterms import Config


class Collection(BaseModel):
    path: Path
    config: Optional[Config] = None
    _database = None
    _encoder = None

    @classmethod
    def load(cls, path: Path):
        project = cls(path=path)
        project.initialize()
        return project

    def initialize(self):
        if not self.path.is_dir():
            self.path.mkdir(parents=True, exist_ok=True)
        self.config = Config.load(self.config_path)

    def save(self, **updates):
        self.config.save(self.config_path, **updates)

    @property
    def is_semantic(self):
        return self.config.search_flag.is_semantic

    @property
    def config_path(self):
        return self.path / "terms.json"

    @property
    def database(self):
        if self._database is None:
            self._database = self._construct_database()
        return self._database

    @property
    def encoder(self):
        if self._encoder is None:
            self._encoder = self._construct_encoder()
        return self._encoder

    # constructors

    def _construct_database(self):
        if self.config.db_backend == "sqlite":
            from fuzzterms.databases import SQLiteDatabase

            return SQLiteDatabase(self)
        else:
            raise NotImplementedError(
                f"Database not supported: {self.collection.config.db_backend}"
            )

    def _construct_encoder(self):
        if self.config.vss_backend == "sbert":
            from fuzzterms.encoders.sbert import SBertEncoder

            return SBertEncoder(self)
        else:
            raise NotImplementedError(
                f"Database not supported: {self.collection.config.vss_backend}"
            )
