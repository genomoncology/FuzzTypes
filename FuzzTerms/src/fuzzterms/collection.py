from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from fuzzterms import Config


class Collection(BaseModel):
    path: Path
    config: Optional[Config] = None

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

    @classmethod
    def load(cls, path: Path):
        project = cls(path=path)
        project.initialize()
        return project
