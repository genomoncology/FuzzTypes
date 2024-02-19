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


def FuzzStr(source: Union[Callable, Iterable]):
    """
    Factory function to create a FuzzType instance specifically for string
    matching, utilizing a source of entities or lookup function.

    :param source: An iterable of entities or a lookup function.
    :return: An instance of FuzzType tailored for string matching.
    """
    lookup = Lookup(source) if isinstance(source, Iterable) else source
    return FuzzType(lookup)


class Lookup:
    """
    Manages a lookup mechanism over Entities, supporting exact matches and
    fuzzy matching, using RapidFuzz for high-performance comparisons.

    :param source: An iterable of Entity items or similar structures.
    :param scorer: Function from RapidFuzz used for scoring fuzzy matches.
    :param score_cutoff: Minimum score for a fuzzy match to be considered valid.
    """

    def __init__(self, source: Iterable, scorer=fuzz.WRatio, score_cutoff=80):
        self.name_exact: dict[str, str] = {}
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
            self._prep_source()
            self.prepped = True
        return self._get_name_from_key(key)

    # private functions

    def _prep_source(self):
        for item in self.source:
            entity = Entity.convert(item)

            self.name_exact[entity.name] = entity.name
            self.name_clean[_clean_str(entity.name)] = entity.name
            self.choices.append(_clean_str(entity.name))

            for synonym in entity.synonyms:
                self.alias_exact[synonym] = entity.name
                self.alias_clean[_clean_str(synonym)] = entity.name
                self.choices.append(_clean_str(synonym))

    def _get_name_from_key(self, key: str) -> str:
        name = self.by_key(key)
        if name is not None:
            return name

        entity = self.by_fuzz(key)
        if entity is not None:
            return entity

        raise KeyError(f"Key not found: {key}")

    def by_key(self, key: str) -> str:
        value = self.name_exact.get(key)
        if not value:
            cleaned_key: str = _clean_str(key)
            value = self.name_clean.get(cleaned_key)
            value = value or self.alias_exact.get(key)
            value = value or self.alias_clean.get(cleaned_key)
        return value

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


def _clean_str(s: str) -> str:
    """
    Cleans a string using RapidFuzz's default_process to prepare it for
    fuzzy matching. Removes non-alphanumeric characters, trims whitespace,
    and converts to lower case.

    :param s: The string to clean.
    :return: The cleaned string.
    """
    return str(default_process(s))
