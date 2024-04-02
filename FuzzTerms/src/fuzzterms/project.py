from typing import Optional
import sys
from pathlib import Path

from pydantic import BaseModel

from fuzzterms import const, flags, logger


class Config(BaseModel):
    device: const.DeviceType = "cpu"
    encoder: str = "sentence-transformers/paraphrase-MiniLM-L6-v2"
    search: const.SearchType = "alias"

    @property
    def search_flag(self) -> flags.SearchFlag:
        return flags.SearchMappings[self.search]

    def save(self, config_path: Path, **updates):
        """Update and save configuration."""
        for k, v in updates.items():
            if v is not None:
                setattr(self, k, v)
        data = self.model_dump_json(indent=4)
        config_path.write_text(data)

    @classmethod
    def load(cls, config_path: Path) -> "Config":
        if config_path.exists():
            data = config_path.read_text()
            config = Config.model_validate_json(data)
        else:
            config = Config()
            config.save(config_path)
        return config


class Project(BaseModel):
    path: Path
    config: Optional[Config] = None

    def initialize(self):
        if not self.path.is_dir():
            self.path.mkdir(parents=True, exist_ok=True)
        self.config = Config.load(self.config_path)

    def save(self, **updates):
        self.config.save(self.config_path, **updates)

    @property
    def config_path(self):
        return self.path / "terms.json"

    @property
    def db_path(self):
        return self.path / "terms.db"

    @classmethod
    def load(cls, path: Path):
        project = Project(path=path)
        project.initialize()
        return project
