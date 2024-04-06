from abc import ABC, abstractmethod
from typing import List

from fuzzterms import Config, lazy


class Encoder(ABC):
    def __init__(self, config: Config):
        self.config = config

    def __call__(self, sentences: List[str]) -> List[List[float]]:
        return self.encode(sentences=sentences)

    @abstractmethod
    def encode(self, sentences: List[str]) -> List[List[float]]:
        pass

    @classmethod
    def construct(cls, config: Config) -> "Encoder":
        options = {
            "sbert": "fuzzterms.encoders.SBertEncoder",
        }
        backend = options.get(config.vss_backend, config.vss_backend)
        library_name, attr_name = backend.rsplit(".", maxsplit=1)
        db_class = lazy.lazy_import(library_name, attr_name)
        assert issubclass(db_class, cls)
        return db_class(config=config)
