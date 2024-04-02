from typing import Union, Any, Optional

from pydantic import BaseModel, Field, TypeAdapter


class Entity(BaseModel):
    name: str = Field(
        ...,
        description="Entity's preferred term.",
    )
    aliases: list[str] = Field(
        ...,
        description="Entity's alias terms.",
        default_factory=list,
    )
    label: Optional[str] = Field(
        default=None,
        description="Entity concept type such as PERSON, ORG, or GPE.",
    )
    meta: Optional[dict] = Field(
        default=None,
        description="Additional entity attribute fields.",
    )
    priority: Optional[int] = Field(
        default=None,
        description="Tiebreaker rank (higher wins, None=0, negative allowed)",
    )

    def __eq__(self, other: Any):
        other = getattr(other, "name", other)
        return self.name == other

    @property
    def rank(self) -> int:
        """Normalized by converting None to 0 and making lower better."""
        return -1 * (self.priority or 0)

    def __lt__(self, other: "Entity") -> bool:
        # noinspection PyTypeChecker
        return (self.rank, self.name) < (other.rank, other.name)

    def __getattr__(self, key: str) -> Any:
        # Check if the key exists in the meta dictionary
        if self.meta is not None and key in self.meta:
            return self.meta[key]
        # Attribute not found; raise AttributeError
        raise AttributeError(
            f"{self.__class__.__name__!r} object has no attribute {key!r}"
        )

    def __setattr__(self, key: str, name: Any):
        # Check if the key is a predefined field in the BaseModel
        if key in self.model_fields:
            super().__setattr__(key, name)
        else:
            self.meta = self.meta or {}
            self.meta[key] = name

    @classmethod
    def convert(cls, item: Union[str, dict, list, tuple, "Entity"]):
        if isinstance(item, cls):
            return item

        data = {}
        if item and isinstance(item, (list, tuple)):
            name, aliases = item[0], item[1:]
            if len(aliases) == 1 and isinstance(aliases[0], (tuple, list)):
                aliases = aliases[0]
            data = dict(name=name, aliases=aliases)
        elif isinstance(item, dict):
            data = item
        else:
            data = dict(name=item)

        return cls(**data)


EntityAdapter = TypeAdapter(Entity)
