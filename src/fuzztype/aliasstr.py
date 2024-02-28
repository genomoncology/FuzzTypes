from typing import Iterable

from . import Entity, EntityDict, FuzzType, MatchList, const
from .namestr import NameLookup


def AliasStr(
    source: Iterable,
    *,
    case_sensitive: bool = False,
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
) -> FuzzType:
    lookup = AliasLookup(
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


def CasedAliasStr(
    source: Iterable,
    *,
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    return AliasStr(
        source,
        examples=examples,
        case_sensitive=True,
        notfound_mode=notfound_mode,
        tiebreaker_mode=tiebreaker_mode,
        validator_mode=validator_mode,
    )


class AliasLookup(NameLookup):
    def __init__(
        self,
        source: Iterable,
        *,
        case_sensitive: bool,
        tiebreaker_mode: const.TiebreakerMode,
    ):
        super().__init__(
            source,
            case_sensitive=case_sensitive,
            tiebreaker_mode=tiebreaker_mode,
        )
        self.entity_dict = EntityDict(case_sensitive, tiebreaker_mode)

    def _add(self, entity: Entity):
        super(AliasLookup, self)._add(entity)

        for alias in entity.aliases:
            self.entity_dict[alias] = entity

    def _get(self, key: str) -> MatchList:
        matches = super(AliasLookup, self)._get(key)
        if not matches:
            entity = self.entity_dict[key]
            if entity:
                matches.set(key=key, entity=entity, is_alias=True)
        return matches
