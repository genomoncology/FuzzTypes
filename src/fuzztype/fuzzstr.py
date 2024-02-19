"""

Instead or lower or casefold, we use rapidfuzz.utils.default_process
to "clean" a key:
    This function preprocesses a string by:
        - removing all non alphanumeric characters
        - trimming whitespaces
        - converting all characters to lower case
    reference: https://rapidfuzz.github.io/RapidFuzz/Usage/utils.html

"""


from typing import Iterable, Callable, Union

from rapidfuzz import fuzz, process
from rapidfuzz.utils import default_process

from . import Entity, FuzzType


def clean_str(s: str) -> str:
    return str(default_process(s))


def FuzzStr(source: Union[Callable, Iterable]):
    lookup = Lookup(source) if isinstance(source, Iterable) else source
    return FuzzType(lookup)


class Lookup:
    """Lookup of Entities for a single label value."""

    def __init__(self, source: Iterable, scorer=fuzz.WRatio, score_cutoff=80):
        self.name_exact: set[str] = set()
        self.name_clean: dict[str, str] = {}
        self.alias_exact: dict[str, str] = {}
        self.alias_clean: dict[str, str] = {}
        self.choices: list[str] = []
        self.source: Iterable = source
        self.scorer = scorer
        self.score_cutoff = score_cutoff
        self.prepped = False

    def __call__(self, key: str) -> str:
        if not self.prepped:
            self.prep_source()
            self.prepped = True
        return self.get_name_from_key(key)

    def prep_source(self):
        for item in self.source:
            entity = Entity.convert(item)

            self.name_exact.add(entity.name)
            self.name_clean[clean_str(entity.name)] = entity.name
            self.choices.append(clean_str(entity.name))

            for synonym in entity.synonyms:
                self.alias_exact[synonym] = entity.name
                self.alias_clean[clean_str(synonym)] = entity.name
                self.choices.append(clean_str(synonym))

    def get_name_from_key(self, key: str) -> str:
        name = self.by_key(key)
        if name is not None:
            return name

        entity = self.by_fuzz(key)
        if entity is not None:
            return entity

        raise KeyError(f"Key not found: {key}")

    def by_key(self, key: str) -> str:
        if key in self.name_exact:
            return key

        cleaned_key: str = clean_str(key)

        try:
            return self.name_clean[cleaned_key]
        except KeyError:
            try:
                return self.alias_exact[key]
            except KeyError:
                try:
                    return self.alias_clean[cleaned_key]
                except KeyError:
                    pass

    def by_fuzz(self, key: str):
        match = process.extractOne(
            key,
            self.choices,
            scorer=self.scorer,
            score_cutoff=self.score_cutoff,
        )

        if match:
            fuzz_key, score, index = match
            entity = self.by_key(fuzz_key)
            if entity is not None:
                return entity
