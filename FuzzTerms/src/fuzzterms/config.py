from pathlib import Path

from pydantic import BaseModel

from fuzzterms import const, flags


class Config(BaseModel):
    # batch size for encoding and upserting data
    batch_size: int = 1000

    # database backend
    db_backend: str = "sqlite"
    db_url: str = "terms.db"

    # vector similarity search (VSS)
    #
    # paraphrase mining model:
    # https://www.sbert.net/examples/applications/paraphrase-mining/README.html
    # https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L6-v2
    #
    vss_backend: str = "sbert"
    vss_enabled: bool = True
    vss_device: const.DeviceType = "cpu"
    vss_model: str = "sentence-transformers/paraphrase-MiniLM-L6-v2"
    vss_dimensions: int = 384

    # searcher
    search_type: const.SearchType = "alias"

    @property
    def search_flag(self) -> flags.SearchFlag:
        return flags.SearchMappings[self.search_type]

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
