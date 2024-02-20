import csv
import json
from pathlib import Path
from typing import List, Union, Type

from pydantic import BaseModel, Field, RootModel


class Entity(BaseModel):
    """An entity has a preferred term (name), synonyms and label."""

    name: str = Field(
        ...,
        description="Preferred term of Entity.",
    )
    synonyms: list[str] = Field(
        ...,
        description="List of aliases for Entity.",
        default_factory=list,
    )
    label: str = Field(
        "",
        description="Entity type such as PERSON, ORG, or GPE.",
    )

    @classmethod
    def convert(cls, item: Union[str, dict, list, tuple, "Entity"]):
        if isinstance(item, cls):
            return item

        if item and isinstance(item, (list, tuple)):
            name, synonyms = item[0], item[1:]
            if len(synonyms) == 1 and isinstance(synonyms[0], (tuple, list)):
                synonyms = synonyms[0]
            item = dict(name=name, synonyms=synonyms)

        elif isinstance(item, str):
            item = dict(name=item)

        return Entity(**item)


class EntitySource:
    def __init__(self, source_path: Path):
        self.loaded = False
        self.source_path = source_path
        self.entities = []

    def __len__(self):
        self._load_if_necessary()
        return len(self.entities)

    def __getitem__(self, item: Union[int, str]):
        self._load_if_necessary()
        if isinstance(item, int):
            return self.entities[item]
        else:
            return iter(filter(lambda e: e.label == item, self.entities))

    def __iter__(self):
        self._load_if_necessary()
        return iter(self.entities)

    def _load_if_necessary(self):
        if not self.loaded:
            self.loaded = True
            dialects = {
                "csv": self.from_csv,
                "tsv": self.from_tsv,
                "jsonl": self.from_jsonl,
            }
            _, ext = self.source_path.name.lower().rsplit(".", maxsplit=1)
            f = dialects.get(ext)
            self.entities = f(self.source_path)

    @classmethod
    def from_jsonl(cls, path: Path) -> List[Entity]:
        """
        Constructs an EntityList from a .jsonl file of Entity definitions.

        :param path: Path object pointing to the .jsonl file.
        :return: List of Entities.
        """
        entities = []
        with path.open("r") as fp:
            for line in fp:
                entity = Entity.convert(json.loads(line))
                entities.append(entity)
        return entities

    @classmethod
    def from_csv(cls, path: Path):
        return cls.from_sv(path, csv.excel)

    @classmethod
    def from_tsv(cls, path: Path):
        return cls.from_sv(path, csv.excel_tab)

    @staticmethod
    def from_sv(path: Path, dialect: Type[csv.Dialect]) -> List[Entity]:
        """
        Constructs an EntityList from a .csv or .tsv file.

        :param path: Path object pointing to the .csv or .tsv file.
        :param dialect: CSV or TSV excel-based dialect.
        :return: List of Entities
        """

        entities = []
        with path.open("r") as fp:
            item: dict
            for item in csv.DictReader(fp):
                synonyms = item.get("synonyms").split("|")
                item["synonyms"] = sorted(filter(None, synonyms))
                entity = Entity.convert(item)
                entities.append(entity)
        return entities
