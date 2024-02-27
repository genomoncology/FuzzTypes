from typing import Iterable

from . import Entity, FuzzType, LookupReturn, const
from .namestr import NameLookup


def AliasStr(
    source: Iterable,
    *,
    case_sensitive: bool = False,
    notfound_mode: const.NotFoundMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    return FuzzType(
        AliasLookup(source, case_sensitive=case_sensitive),
        notfound_mode=notfound_mode,
        python_type=str,
        validator_mode=validator_mode,
    )


def CasedAliasStr(
    source: Iterable,
    validator_mode: const.ValidatorMode = "before",
    notfound_mode: const.NotFoundMode = "raise",
):
    return AliasStr(
        source,
        case_sensitive=True,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )


class AliasLookup(NameLookup):
    def __init__(self, source: Iterable, *, case_sensitive: bool):
        super().__init__(source, case_sensitive=case_sensitive)
        self.alias_exact: dict[str, Entity] = {}
        self.alias_lower: dict[str, Entity] = {}

    def _add(self, entity: Entity):
        super(AliasLookup, self)._add(entity)
        for alias in entity.aliases:
            self.alias_exact[alias] = entity
            if not self.case_sensitive:
                self.alias_lower[alias.lower()] = entity

    def _get(self, key: str) -> LookupReturn:
        entity = super(AliasLookup, self)._get(key)
        if entity is None:
            entity = self.alias_exact.get(key)
            if not self.case_sensitive and entity is None:
                entity = self.alias_lower.get(key.lower())
        return entity
