from pathlib import Path

from pydantic import BaseModel

from fuzzterms import const, flags


class Config(BaseModel):
    # database backend
    db_backend: str = "sqlite"
    db_url: str = "terms.db"

    # vector similarity search (VSS)
    vss_enabled: bool = True
    vss_device: const.DeviceType = "cpu"
    vss_encoder: str = "sentence-transformers/paraphrase-MiniLM-L6-v2"

    # searcher
    search_type_default: const.SearchType = "alias"

    @property
    def search_type_default_flag(self) -> flags.SearchFlag:
        return flags.SearchMappings[self.search_type_default]

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
