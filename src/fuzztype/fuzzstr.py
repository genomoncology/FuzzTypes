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
        self.entities: list[Entity] = []

    def _add_entity(self, entity: Entity):
        super()._add_entity(entity)

        # noinspection PyTypeChecker
        clean_name: str = default_process(entity.name)
        self.clean.append(clean_name)
        self.entities.append(entity)

        for alias in entity.aliases:
            # noinspection PyTypeChecker
            clean_alias: str = default_process(alias)
            self.clean.append(clean_alias)
            self.entities.append(entity)

    def _get(self, key: str, raise_if_missing: bool = True) -> Entity:
        # Attempt to resolve the name using exact and alias matches first
        entity = super()._get(key, False)

        if entity is None:
            clean_key = default_process(key)

            match = process.extract(
                clean_key,
                self.clean,
                scorer=self.scorer,
                limit=self.num_nearest,
            )

            nearest = []
            match_score = 0
            for found_clean, score, index in match:
                found_entity = self.entities[index]

                if (score >= self.min_score) and (score > match_score):
                    entity = found_entity
                    match_score = score

                score = f"{score:.1f}"
                if default_process(found_entity.name) == found_clean:
                    msg = f"{found_entity.name} [{score}]"
                else:
                    msg = f"{found_clean} => {found_entity.name} [{score}]"
                nearest.append(msg)

            nearest = ", ".join(nearest)

            if raise_if_missing and entity is None:
                msg = "key ({key}) not resolved (nearest: {nearest})"
                raise PydanticCustomError(
                    "fuzz_str_not_found",
                    msg,
                    dict(key=key, nearest=nearest),
                )

        return entity
