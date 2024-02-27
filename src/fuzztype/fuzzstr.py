from typing import Iterable, List, Optional

from pydantic import PositiveInt

from . import (
    AliasLookup,
    Entity,
    FuzzMatch,
    FuzzType,
    LookupReturn,
    const,
    fuzz_clean,
    fuzz_match,
)


def FuzzStr(
    source: Iterable,
    *,
    case_sensitive: bool = False,
    examples: list = None,
    fuzz_limit: PositiveInt = 3,
    fuzz_min_score: float = 80.0,
    fuzz_scorer: const.FuzzScorer = "token_sort_ratio",
    notfound_mode: const.NotFoundMode = "raise",
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    """Fuzzy string type."""
    lookup = FuzzLookup(
        source,
        case_sensitive=case_sensitive,
        fuzz_limit=fuzz_limit,
        fuzz_min_score=fuzz_min_score,
        fuzz_scorer=fuzz_scorer,
        tiebreaker_mode=tiebreaker_mode,
    )
    return FuzzType(
        lookup_function=lookup,
        examples=examples,
        notfound_mode=notfound_mode,
        python_type=str,
        validator_mode=validator_mode,
    )


class FuzzLookup(AliasLookup):
    def __init__(
        self,
        source: Iterable,
        *,
        case_sensitive: bool,
        fuzz_limit: int,
        fuzz_min_score: float,
        fuzz_scorer: const.FuzzScorer,
        tiebreaker_mode: const.TiebreakerMode,
    ):
        super().__init__(source, case_sensitive=case_sensitive)
        self.clean: list[str] = []
        self.entities: list[Entity] = []
        self.fuzz_limit = fuzz_limit
        self.fuzz_min_score = fuzz_min_score
        self.fuzz_scorer = fuzz_scorer
        self.tiebreaker_mode = tiebreaker_mode

    def _add(self, entity: Entity):
        super()._add(entity)

        clean_name: str = fuzz_clean(entity.name)
        self.clean.append(clean_name)
        self.entities.append(entity)

        for alias in entity.aliases:
            clean_alias: str = fuzz_clean(alias)
            self.clean.append(clean_alias)
            self.entities.append(entity)

    def _get(self, key: str) -> LookupReturn:
        # Attempt to resolve the name using exact and alias matches first
        entity = super()._get(key)
        near_matches = []

        if entity is None:
            query = fuzz_clean(key)

            near_matches = fuzz_match(
                query,
                self.clean,
                scorer=self.fuzz_scorer,
                limit=self.fuzz_limit,
                entities=self.entities,
            )

            entity = self._select_best(near_matches)

        return entity or near_matches

    def _select_best(self, matches: List[FuzzMatch]) -> Optional[Entity]:
        # Filter by score
        matches = [m for m in matches if m.score >= self.fuzz_min_score]

        # Sort by rank (fuzz score, priority) and alphabetical order
        matches = sorted(matches)

        entity = None

        if len(matches) == 1:
            entity = matches[0].entity

        elif matches and self.tiebreaker_mode == "raise":
            if matches[0].rank != matches[1].rank:
                entity = matches[0].entity

        elif matches and self.tiebreaker_mode == "alphabetical":
            entity = matches[0].entity

        return entity
