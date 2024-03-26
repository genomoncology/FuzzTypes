import json
from enum import Enum
from typing import Annotated, Optional, List, Iterable, Type

from pydantic import TypeAdapter

from fuzztypes import EntitySource, NamedEntity, OnDiskValidator, flags, utils


class LanguageScope(Enum):
    INDIVIDUAL = "I"
    MACROLANGUAGE = "M"
    SPECIAL = "S"


class LanguageType(Enum):
    ANCIENT = "A"
    CONSTRUCTED = "C"
    EXTINCT = "E"
    HISTORICAL = "H"
    LIVING = "L"
    SPECIAL = "S"


class LanguageNamedEntity(NamedEntity):
    """Resolves to language full name."""

    alpha_2: Optional[str] = None
    alpha_3: str
    scope: Optional[LanguageScope] = None
    type: Optional[LanguageType] = None
    common_name: Optional[str] = None
    inverted_name: Optional[str] = None
    bibliographic: Optional[str] = None

    @property
    def code(self):
        return self.alpha_2 or self.alpha_3


class LanguageModelNamedEntity(LanguageNamedEntity):
    """Resolves to self as a full child object."""

    def resolve(self):
        return self


class LanguageCodeNameEntity(LanguageNamedEntity):
    """Resolves to code name."""

    def resolve(self):
        return self.code


LanguageNamedEntityType = Type[LanguageNamedEntity]


def load_languages(
    entity_cls: Type[LanguageNamedEntity],
):
    def do_load() -> Iterable[NamedEntity]:
        repo = "https://salsa.debian.org/iso-codes-team/iso-codes/"
        remote = f"{repo}-/raw/main/data/iso_639-3.json"
        local = utils.get_file(remote)
        assert local, f"Could not download: {remote}"
        data = json.load(open(local))["639-3"]
        alias_fields = {
            "alpha_2",
            "alpha_3",
            "common_name",
            "inverted_name",
            "bibliographic",
        }
        entities = []
        for item in data:
            item["value"] = item.pop("name")
            aliases = [v for k, v in item.items() if k in alias_fields]
            item["aliases"] = aliases
            entities.append(item)
        return TypeAdapter(List[entity_cls]).validate_python(data)

    return do_load


LanguageName = Annotated[
    str,
    OnDiskValidator(
        "Language",
        EntitySource(load_languages(LanguageNamedEntity)),
        entity_type=LanguageNamedEntity,
        search_flag=flags.AliasSearch,
        tiebreaker_mode="lesser",
    ),
]

LanguageCode = Annotated[
    str,
    OnDiskValidator(
        "Language",
        EntitySource(load_languages(LanguageCodeNameEntity)),
        entity_type=LanguageCodeNameEntity,
        search_flag=flags.AliasSearch,
        tiebreaker_mode="lesser",
    ),
]

Language = Annotated[
    LanguageNamedEntity,
    OnDiskValidator(
        "Language",
        EntitySource(load_languages(LanguageModelNamedEntity)),
        entity_type=LanguageModelNamedEntity,
        search_flag=flags.AliasSearch,
        tiebreaker_mode="lesser",
    ),
]
