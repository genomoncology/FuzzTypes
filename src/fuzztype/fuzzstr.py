"""

Instead or lower or casefold, we use rapidfuzz.utils.default_process
to "clean" a key:
    This function preprocesses a string by:
        - removing all non alphanumeric characters
        - trimming whitespaces
        - converting all characters to lower case
    reference: https://rapidfuzz.github.io/RapidFuzz/Usage/utils.html

"""


from typing import Iterable, Callable

from pydantic_core import PydanticCustomError
from rapidfuzz import fuzz, process
from rapidfuzz.utils import default_process

from . import Entity, FuzzType


def FuzzStr(
    source: Iterable,
    scorer: Callable = fuzz.WRatio,
    min_score: float = 80.0,
    num_nearest: int = 3,
):
    """Fuzzy string type."""
    lookup = Lookup(
        source,
        scorer=scorer,
        min_score=min_score,
        num_nearest=num_nearest,
    )
    return FuzzType(lookup_function=lookup)


class Lookup:
    def __init__(
        self,
        source: Iterable,
        scorer: Callable,
        min_score: float,
        num_nearest: int,
    ):
        self.name_exact: dict[str, str] = {}
        self.name_clean: dict[str, str] = {}
        self.alias_exact: dict[str, str] = {}
        self.alias_clean: dict[str, str] = {}
        self.clean: list[str] = []
        self.names: list[str] = []
        self.source: Iterable = source
        self.scorer = scorer
        self.min_score = min_score
        self.prepped = False
        self.num_nearest = num_nearest

    def __call__(self, key: str) -> str:
        if not self.prepped:
            self._prep_source()
            self.prepped = True

        name, nearest = self._get_name_from_key(key)

        if name is None:
            msg = "key ({key}) not resolved (nearest: {nearest})"
            raise PydanticCustomError(
                "fuzz_str_not_resolved",
                msg,
                dict(key=key, nearest=nearest),
            )

        return name

    # private functions

    def _prep_source(self):
        for item in self.source:
            entity = Entity.convert(item)
            clean_name = _clean_str(entity.name)

            self.name_exact[entity.name] = entity.name
            self.name_clean[clean_name] = entity.name
            self.clean.append(clean_name)
            self.names.append(entity.name)

            for synonym in entity.synonyms:
                clean_syn = _clean_str(synonym)
                self.clean.append(clean_syn)
                self.names.append(entity.name)
                self.alias_exact[synonym] = entity.name
                self.alias_clean[clean_syn] = entity.name

    def _get_name_from_key(self, key: str) -> tuple[str, list[str]]:
        name = self.by_key(key)
        if name is not None:
            return name, []

        entity, nearest = self.by_fuzz(key)
        return entity, nearest

    def by_key(self, key: str) -> str:
        value = self.name_exact.get(key)
        if not value:
            cleaned_key: str = _clean_str(key)
            value = self.name_clean.get(cleaned_key)
            value = value or self.alias_exact.get(key)
            value = value or self.alias_clean.get(cleaned_key)
        return value

    def by_fuzz(self, key: str):
        match = process.extract(
            key,
            self.clean,
            scorer=self.scorer,
            limit=self.num_nearest,
        )

        nearest = []
        for found_clean, score, index in match:
            found_name = self.names[index]

            # Found Match: Early Exit
            if score >= self.min_score:
                return found_name, []

            score = f"{score:.1f}"
            if _clean_str(found_name) == found_clean:
                nearest.append(f"{found_name} [{score}]")
            else:
                nearest.append(f"{found_clean} => {found_name} [{score}]")

        nearest = ", ".join(nearest)

        return None, nearest


def _clean_str(s: str) -> str:
    """
    Cleans a string using RapidFuzz's default_process to prepare it for
    fuzzy matching. Removes non-alphanumeric characters, trims whitespace,
    and converts to lower case.

    :param s: The string to clean.
    :return: The cleaned string.
    """
    return str(default_process(s))
