from typing import Iterable

from . import Entity, LookupReturn, FuzzType, const


def NameStr(
    source: Iterable,
    case_sensitive: bool = False,
    validator_mode: const.ValidatorMode = "before",
    notfound_mode: const.NotFoundMode = "raise",
):
    return FuzzType(
        lookup_function=NameLookup(source, case_sensitive),
        python_type=str,
        validator_mode=validator_mode,
        notfound_mode=notfound_mode,
    )


def CasedNameStr(
    source: Iterable,
    validator_mode: const.ValidatorMode = "before",
    notfound_mode: const.NotFoundMode = "raise",
):
    return NameStr(
        source=source,
        case_sensitive=True,
        validator_mode=validator_mode,
        notfound_mode=notfound_mode,
    )


class NameLookup:
    def __init__(self, source: Iterable, case_sensitive: bool):
        self.prepped: bool = False
        self.source: Iterable = source
        self.case_sensitive: bool = case_sensitive
        self.name_exact: dict[str, Entity] = {}
        self.name_lower: dict[str, Entity] = {}

    def __call__(self, key: str) -> Entity:
        self._prep()
        return self._get(key)

    # private functions

    def _get(self, key: str) -> LookupReturn:
        entity = self.name_exact.get(key)
        if not self.case_sensitive and entity is None:
            entity = self.name_lower.get(key.lower())
        return entity

    def _prep(self):
        if not self.prepped:
            self.prepped = True
            for item in self.source:
                entity = Entity.convert(item)
                self._add(entity)

    def _add(self, entity: Entity):
        self.name_exact[entity.name] = entity
        self.name_lower[entity.name.lower()] = entity
