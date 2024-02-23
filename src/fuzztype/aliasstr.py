from typing import Iterable

from pydantic_core import PydanticCustomError

from . import Entity, FuzzType

from .namestr import NameLookup


def AliasStr(source: Iterable, case_sensitive: bool = False):
    return FuzzType(lookup_function=AliasLookup(source, case_sensitive))


def CasedAliasStr(source: Iterable):
    return FuzzType(lookup_function=AliasLookup(source, True))


class AliasLookup(NameLookup):
    def __init__(self, source: Iterable, case_sensitive: bool):
        super().__init__(source, case_sensitive)
        self.alias_exact: dict[str, str] = {}
        self.alias_lower: dict[str, str] = {}

    def _add_entity(self, entity: Entity):
        super(AliasLookup, self)._add_entity(entity)
        for alias in entity.aliases:
            self.alias_exact[alias] = entity.name
            if not self.case_sensitive:
                self.alias_lower[alias.lower()] = entity.name

    def _get(self, key: str, raise_exception_if_missing: bool):
        name = super(AliasLookup, self)._get(key, False)
        if name is None:
            name = self.alias_exact.get(key)
            if not self.case_sensitive and name is None:
                name = self.alias_lower.get(key.lower())

        if raise_exception_if_missing and name is None:
            msg = "Key ({key}) not found."
            raise PydanticCustomError(
                "alias_str_not_found", msg, dict(key=key)
            )

        return name
