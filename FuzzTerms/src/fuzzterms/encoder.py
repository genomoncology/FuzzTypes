from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from fuzzterms import Collection


class Encoder(ABC):
    def __init__(self, collection: "Collection"):
        self.collection = collection
        self.config = collection.config

    def __call__(self, sentences: List[str]) -> List[float]:
        return self.encode(sentences=sentences)

    @abstractmethod
    def encode(self, sentences: List[str]) -> List[float]:
        pass
