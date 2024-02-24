import csv
import json
from pathlib import Path
from typing import List, Union, Type, Any, Optional

from pydantic import BaseModel, Field


class Entity(BaseModel):
    name: str = Field(
        ...,
        description="Preferred term of Entity.",
    )
    aliases: list[str] = Field(
        ...,
        description="List of aliases for Entity.",
        default_factory=list,
    )
    label: Optional[str] = Field(
        default=None,
        description="Entity type such as PERSON, ORG, or GPE.",
    )
    meta: dict = Field(
        None,
        description="Additional attributes accessible through dot-notation.",
    )

    def __getattr__(self, key: str) -> Any:
        # Check if the key exists in the meta dictionary
        if self.meta is not None and key in self.meta:
            return self.meta[key]
        # Attribute not found; raise AttributeError
        raise AttributeError(
            f"{self.__class__.__name__!r} object has no attribute {key!r}"
        )

    def __setattr__(self, key: str, value: Any):
        # Check if the key is a predefined field in the BaseModel
        if key in self.__fields__:
            super().__setattr__(key, value)
        else:
            # Initialize meta if it's None
            if self.__dict__.get("meta") is None:
                super().__setattr__("meta", {})
            # Add or update the attribute in the meta dictionary
            self.meta[key] = value

    @classmethod
    def convert(cls, item: Union[str, dict, list, tuple, "Entity"]):
        if isinstance(item, cls):
            return item

        if item and isinstance(item, (list, tuple)):
            name, aliases = item[0], item[1:]
            if len(aliases) == 1 and isinstance(aliases[0], (tuple, list)):
                aliases = aliases[0]
            item = dict(name=name, aliases=aliases)

        elif isinstance(item, str):
            item = dict(name=item)

        return Entity(**item)


class EntitySource:
    def __init__(self, source_path: Path, mv_splitter="|"):
        self.loaded = False
        self.source_path = source_path
        self.mv_splitter = mv_splitter
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

    def from_csv(self, path: Path):
        return self.from_sv(path, csv.excel)

    def from_tsv(self, path: Path):
        return self.from_sv(path, csv.excel_tab)

    def from_sv(self, path: Path, dialect: Type[csv.Dialect]) -> List[Entity]:
        """
        Constructs an EntityList from a .csv or .tsv file.

        :param path: Path object pointing to the .csv or .tsv file.
        :param dialect: CSV or TSV excel-based dialect.
        :return: List of Entities
        """

        entities = []
        with path.open("r") as fp:
            item: dict
            for item in csv.DictReader(fp, dialect=dialect):
                aliases = item.get("aliases", "").split(self.mv_splitter)
                item["aliases"] = sorted(filter(None, aliases))
                entity = Entity.convert(item)
                entities.append(entity)
        return entities
