from typing import Iterable, List

from pydantic import BaseModel, Field
from rapidfuzz.fuzz import WRatio
from rapidfuzz.process import extractOne

from . import Entity


class Lookup(BaseModel):
    """Lookup of Entities for a single label value."""

    name_exact: dict[str, Entity] = Field(default_factory=dict)
    name_icase: dict[str, Entity] = Field(default_factory=dict)
    alias_exact: dict[str, Entity] = Field(default_factory=dict)
    alias_icase: dict[str, Entity] = Field(default_factory=dict)
    choices: List[str] = Field(default_factory=list)

    def __call__(self, key: str) -> str:
        entity = self.get_entity(key)
        return entity.name

    def get_entity(self, key: str) -> Entity:
        entity = self.by_key(key)
        if entity is not None:
            return entity

        entity = self.by_fuzz(key)
        if entity is not None:
            return entity

        raise KeyError(f"Key not found: {key}")

    def by_key(self, key: str) -> Entity:
        try:
            return self.name_exact[key]
        except KeyError:
            try:
                return self.name_icase[key.casefold()]
            except KeyError:
                try:
                    return self.alias_exact[key]
                except KeyError:
                    try:
                        return self.alias_icase[key.casefold()]
                    except KeyError:
                        pass

    def by_fuzz(self, key: str):
        match = extractOne(key, self.choices, scorer=WRatio, score_cutoff=50)
        if match:
            fuzz_key, score, index = match
            entity = self.by_key(fuzz_key)
            if entity is not None:
                return entity

    def add_entity(self, entity: Entity):
        found = self.name_exact.get(entity.name)
        if found is not None:
            found.synonyms = sorted(set(entity.synonyms + found.synonyms))
            entity = found

        self.name_exact[entity.name] = entity
        self.name_icase[entity.name.casefold()] = entity
        self.choices.append(entity.name)

        for synonym in entity.synonyms:
            self.alias_exact[synonym] = entity
            self.alias_icase[synonym.casefold()] = entity
            self.choices.append(synonym)


class Registry:
    """Registry of Lookups by label."""

    _lookups = {}

    @classmethod
    def lookup(cls, *, key: str, label: str = "") -> str:
        lookup = cls.get_lookup(label)
        return lookup(key)

    @classmethod
    def update(cls, entities: Iterable[Entity]) -> set[str]:
        labels_added = set()

        for entity in entities:
            lookup = cls.get_lookup(entity.label)
            lookup.add_entity(entity)
            labels_added.add(entity.label)

        return labels_added

    @classmethod
    def get_lookup(cls, label: str):
        if label not in cls._lookups:
            cls._lookups[label] = Lookup()
        return cls._lookups.get(label)
