from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from fuzzterms import Config, Database, Encoder


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
            self._database = Database.construct(self.path, self.config)
        return self._database

    @property
    def encoder(self):
        if self._encoder is None:
            self._encoder = Encoder.construct(self.config)
        return self._encoder
