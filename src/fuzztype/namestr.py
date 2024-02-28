from typing import Iterable

from . import Entity, Match, MatchList, FuzzType, const


def NameStr(
    source: Iterable,
    case_sensitive: bool = False,
    examples: list = None,
    validator_mode: const.ValidatorMode = "before",
    notfound_mode: const.NotFoundMode = "raise",
):
    return FuzzType(
        NameLookup(source, case_sensitive=case_sensitive),
        examples=examples,
        notfound_mode=notfound_mode,
        python_type=str,
        validator_mode=validator_mode,
    )


def CasedNameStr(
    source: Iterable,
    examples: list = None,
    validator_mode: const.ValidatorMode = "before",
    notfound_mode: const.NotFoundMode = "raise",
):
    return NameStr(
        source,
        case_sensitive=True,
        examples=examples,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )


class NameLookup:
    def __init__(self, source: Iterable, *, case_sensitive: bool):
        self.case_sensitive: bool = case_sensitive
        self.name_exact: dict[str, Entity] = {}
        self.name_lower: dict[str, Entity] = {}
        self.prepped: bool = False
        self.source: Iterable = source

    def __call__(self, key: str) -> MatchList:
        self._prep()
        return self._get(key)

    # private functions

    def _get(self, key: str) -> MatchList:
        matches = MatchList()
        entity = self.name_exact.get(key)
        if not self.case_sensitive and entity is None:
            entity = self.name_lower.get(key.lower())
        if entity:
            matches.set(key=key, entity=entity, is_alias=False)
        return matches

    def _prep(self):
        if not self.prepped:
            self.prepped = True
            for item in self.source:
                entity = Entity.convert(item)
                self._add(entity)

    def _add(self, entity: Entity):
        self.name_exact[entity.name] = entity
        self.name_lower[entity.name.lower()] = entity
