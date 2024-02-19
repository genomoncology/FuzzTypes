import json
from pathlib import Path
from typing import List, Union

from pydantic import BaseModel, Field, RootModel


class Entity(BaseModel):
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

        if isinstance(item, str):
            item = dict(name=item)

        return Entity(**item)


class EntityList(RootModel):
    root: List[Entity]

    def __len__(self):
        return len(self.root)

    def __getitem__(self, item: Union[int, str]):
        if isinstance(item, int):
            return self.root[item]
        else:
            return iter(filter(lambda e: e.label == item, self.root))

    @classmethod
    def from_jsonl(cls, path: Path):
        assert path.name.endswith(".jsonl")
        entities = []
        with path.open("r") as fp:
            for line in fp:
                entity = Entity.convert(json.loads(line))
                entities.append(entity)
        return cls(entities)
