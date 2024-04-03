from typing import List
from abc import ABC, abstractmethod
from fuzzterms import Collection


class Encoder(ABC):
    def __init__(self, collection: Collection):
        self.collection = collection
        self.config = collection.config

    @classmethod
    def construct(cls, collection: Collection):
        if collection.config.vss_backend == "sbert":
            from fuzzterms.encoders.sbert import SBertEncoder

            return SBertEncoder(collection)
        else:
            raise NotImplementedError(
                f"Database not supported: {collection.config.vss_backend}"
            )

    @abstractmethod
    def encode(self, sentences: List[str]) -> List[float]:
        pass
