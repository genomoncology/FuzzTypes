from typing import Union, Any

from pydantic import BaseModel, Field


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
