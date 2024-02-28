from typing import Iterable

from . import Entity, EntityDict, MatchList, FuzzType, const


def NameStr(
    source: Iterable,
    case_sensitive: bool = False,
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    lookup = NameLookup(
        source,
        case_sensitive=case_sensitive,
        tiebreaker_mode=tiebreaker_mode,
    )
    return FuzzType(
        lookup,
        examples=examples,
        notfound_mode=notfound_mode,
        python_type=str,
        validator_mode=validator_mode,
    )


def CasedNameStr(
    source: Iterable,
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    return NameStr(
        source,
        case_sensitive=True,
        examples=examples,
        notfound_mode=notfound_mode,
        tiebreaker_mode=tiebreaker_mode,
        validator_mode=validator_mode,
    )


class NameLookup:
    def __init__(
        self,
        source: Iterable,
        *,
        case_sensitive: bool,
        tiebreaker_mode: const.TiebreakerMode,
    ):
        self.entity_dict = EntityDict(case_sensitive, tiebreaker_mode)
        self.prepped: bool = False
        self.source: Iterable = source
        self.case_sensitive = case_sensitive
        self.tiebreaker_mode = tiebreaker_mode

    def __call__(self, key: str) -> MatchList:
        self._prep()
        return self._get(key)

    # private functions

    def _get(self, key: str) -> MatchList:
        matches = MatchList()
        entity = self.entity_dict[key]
        if entity:
            matches.set(key=key, entity=entity, is_alias=True)
        return matches

    def _prep(self):
        if not self.prepped:
            self.prepped = True
            for item in self.source:
                entity = Entity.convert(item)
                self._add(entity)

    def _add(self, entity: Entity):
        self.entity_dict[entity.name] = entity
