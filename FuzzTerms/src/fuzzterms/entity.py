from typing import Any, Optional, ClassVar

from pydantic import BaseModel, Field


class Entity(BaseModel):
    NULL_LABEL: ClassVar = "NULL"

    name: str = Field(
        ...,
        description="Entity's preferred term.",
    )
    aliases: list[str] = Field(
        ...,
        description="Entity's alias terms.",
        default_factory=list,
    )
    label: str = Field(
        default=NULL_LABEL,
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

    @property
    def pk(self):
        return self.name, self.label

    def __eq__(self, other: Any):
        other = getattr(other, "pk", other)
        return self.pk == other

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
