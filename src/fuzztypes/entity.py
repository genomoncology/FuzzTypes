import csv
import json
from pathlib import Path
from typing import List, Union, Type, Any, Optional, Tuple, Dict, Callable

from pydantic import BaseModel, Field

from .const import TiebreakerMode


class Entity(BaseModel):
    value: Any = Field(
        ...,
        description="Value stored by Entity.",
    )
    label: Optional[str] = Field(
        default=None,
        description="Entity concept type such as PERSON, ORG, or GPE.",
    )
    meta: Optional[dict] = Field(
        None,
        description="Additional attributes accessible through dot-notation.",
    )
    priority: Optional[int] = Field(
        None,
        description="Tiebreaker rank (higher wins, None=0, negative allowed)",
    )

    def __eq__(self, other: Any):
        other = getattr(other, "value", other)
        return self.value == other

    @property
    def rank(self) -> int:
        """Normalized by converting None to 0 and making lower better."""
        return -1 * (self.priority or 0)

    def __lt__(self, other: "Entity") -> bool:
        # noinspection PyTypeChecker
        return (self.rank, self.value) < (other.rank, other.value)

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
        if key in self.model_fields:
            super().__setattr__(key, value)
        else:
            # Initialize meta if it's None
            if self.__dict__.get("meta") is None:
                super().__setattr__("meta", {})
            # Add or update the attribute in the meta dictionary
            self.meta[key] = value


class NamedEntity(Entity):
    value: str = Field(
        ...,
        description="Preferred term of NamedEntity.",
    )
    aliases: list[str] = Field(
        ...,
        description="List of aliases for NamedEntity.",
        default_factory=list,
    )

    @classmethod
    def convert(cls, item: Union[str, dict, list, tuple, "NamedEntity"]):
        if isinstance(item, cls):
            return item

        if item and isinstance(item, (list, tuple)):
            value, aliases = item[0], item[1:]
            if len(aliases) == 1 and isinstance(aliases[0], (tuple, list)):
                aliases = aliases[0]
            item = dict(value=value, aliases=aliases)

        elif isinstance(item, str):
            item = dict(value=item)

        return NamedEntity(**item)


SourceType = Union[Path, tuple["EntitySource", str], Callable]


class EntitySource:
    def __init__(self, source: SourceType, mv_splitter: str = "|"):
        self.loaded: bool = False
        self.source: SourceType = source
        self.mv_splitter: str = mv_splitter
        self.entities: List[NamedEntity] = []

    def __len__(self):
        self._load_if_necessary()
        return len(self.entities)

    def __getitem__(
        self, key: Union[int, slice, str]
    ) -> Union[NamedEntity, "EntitySource"]:
        if isinstance(key, str):
            # return another shell, let loading occur on demand.
            return EntitySource(source=(self, key))

        self._load_if_necessary()
        return self.entities[key]

    def __iter__(self):
        self._load_if_necessary()
        return iter(self.entities)

    def _load_if_necessary(self):
        if not self.loaded:
            self.loaded = True
            if isinstance(self.source, Tuple):
                parent, label = self.source
                self.entities = [e for e in parent if e.label == label]

            elif isinstance(self.source, Callable):
                self.entities = self.source()

            elif self.source:
                dialects = {
                    "csv": self.from_csv,
                    "tsv": self.from_tsv,
                    "jsonl": self.from_jsonl,
                }
                _, ext = self.source.name.lower().rsplit(".", maxsplit=1)
                f = dialects.get(ext)

                # noinspection PyArgumentList
                self.entities = f(self.source)

    @classmethod
    def from_jsonl(cls, path: Path) -> List[NamedEntity]:
        """
        Constructs an EntityList from a .jsonl file of NamedEntity definitions.

        :param path: Path object pointing to the .jsonl file.
        :return: List of Entities.
        """
        entities = []
        with path.open("r") as fp:
            for line in fp:
                entity = NamedEntity.convert(json.loads(line))
                entities.append(entity)
        return entities

    def from_csv(self, path: Path) -> List[NamedEntity]:
        return self.from_sv(path, csv.excel)

    def from_tsv(self, path: Path) -> List[NamedEntity]:
        return self.from_sv(path, csv.excel_tab)

    def from_sv(
        self, path: Path, dialect: Type[csv.Dialect]
    ) -> List[NamedEntity]:
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
                entity = NamedEntity.convert(item)
                entities.append(entity)
        return entities
