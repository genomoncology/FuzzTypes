from typing import Iterable, Callable

from rapidfuzz import fuzz, process
from rapidfuzz.utils import default_process

from . import const, Entity, LookupReturn, NearMatch, FuzzType
from .aliasstr import AliasLookup


def FuzzStr(
    source: Iterable,
    scorer: Callable = fuzz.token_sort_ratio,
    min_score: float = 80.0,
    num_nearest: int = 3,
    case_sensitive: bool = False,
    validator_mode: const.ValidatorMode = "before",
    notfound_mode: const.NotFoundMode = "raise",
    examples: list = None,
):
    """Fuzzy string type."""
    lookup = FuzzLookup(
        source,
        scorer=scorer,
        min_score=min_score,
        num_nearest=num_nearest,
        case_sensitive=case_sensitive,
    )
    return FuzzType(
        lookup_function=lookup,
        python_type=str,
        validator_mode=validator_mode,
        notfound_mode=notfound_mode,
        examples=examples,
    )


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

    def _add(self, entity: Entity):
        super()._add(entity)

        # noinspection PyTypeChecker
        clean_name: str = default_process(entity.name)
        self.clean.append(clean_name)
        self.entities.append(entity)

        for alias in entity.aliases:
            # noinspection PyTypeChecker
            clean_alias: str = default_process(alias)
            self.clean.append(clean_alias)
            self.entities.append(entity)

    def _get(self, key: str) -> LookupReturn:
        # Attempt to resolve the name using exact and alias matches first
        entity = super()._get(key)
        near_matches = []

        if entity is None:
            clean_key = default_process(key)

            matches = process.extract(
                clean_key,
                self.clean,
                scorer=self.scorer,
                limit=self.num_nearest,
            )

            if matches and matches[0][1] >= self.min_score:
                entity = self.entities[matches[0][2]]

            else:
                for found_clean, score, index in matches:
                    near_entity = self.entities[index]
                    is_alias = default_process(near_entity.name) != found_clean
                    alias = found_clean if is_alias else None
                    near_match = NearMatch(
                        entity=near_entity,
                        score=score,
                        alias=alias,
                    )
                    near_matches.append(near_match)

        return entity or near_matches
