from typing import Iterable, Callable

from pydantic_core import PydanticCustomError
from rapidfuzz import fuzz, process
from rapidfuzz.utils import default_process

from . import Entity, FuzzType
from .aliasstr import AliasLookup


def FuzzStr(
    source: Iterable,
    scorer: Callable = fuzz.token_sort_ratio,
    min_score: float = 80.0,
    num_nearest: int = 3,
    case_sensitive: bool = False,
):
    """Fuzzy string type."""
    lookup = FuzzLookup(
        source,
        scorer=scorer,
        min_score=min_score,
        num_nearest=num_nearest,
        case_sensitive=case_sensitive,
    )
    return FuzzType(lookup_function=lookup)


class FuzzLookup(AliasLookup):
    def __init__(
        self,
        source: Iterable,
        scorer: Callable,
        min_score: float,
        num_nearest: int,
        case_sensitive: bool,
    ):
        super().__init__(source, case_sensitive)
        self.scorer = scorer
        self.min_score = min_score
        self.num_nearest = num_nearest
        self.clean: list[str] = []
        self.names: list[str] = []

    def _add_entity(self, entity: Entity):
        super()._add_entity(entity)

        # noinspection PyTypeChecker
        clean_name: str = default_process(entity.name)
        self.clean.append(clean_name)
        self.names.append(entity.name)

        for alias in entity.aliases:
            # noinspection PyTypeChecker
            clean_alias: str = default_process(alias)
            self.clean.append(clean_alias)
            self.names.append(entity.name)

    def _get(self, key: str, raise_exception_if_missing: bool = True) -> str:
        # Attempt to resolve the name using exact and alias matches first
        name = super()._get(key, False)

        if name is None:
            clean_key = default_process(key)

            match = process.extract(
                clean_key,
                self.clean,
                scorer=self.scorer,
                limit=self.num_nearest,
            )

            nearest = []
            name = None
            match_score = 0
            for found_clean, score, index in match:
                found_name = self.names[index]

                if (score >= self.min_score) and (score > match_score):
                    name = found_name
                    match_score = score

                score = f"{score:.1f}"
                if default_process(found_name) == found_clean:
                    nearest.append(f"{found_name} [{score}]")
                else:
                    nearest.append(f"{found_clean} => {found_name} [{score}]")

            nearest = ", ".join(nearest)

            if raise_exception_if_missing and name is None:
                msg = "key ({key}) not resolved (nearest: {nearest})"
                raise PydanticCustomError(
                    "fuzz_str_not_found",
                    msg,
                    dict(key=key, nearest=nearest),
                )

        return name
