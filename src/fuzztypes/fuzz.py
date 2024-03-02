from typing import Iterable
from typing import List

from pydantic import PositiveInt
from rapidfuzz import fuzz, process, utils

from . import AliasLookup, AbstractType, NamedEntity, Match, MatchList, const


def fuzz_clean(key: str) -> str:
    # no really, it's a string
    # noinspection PyTypeChecker
    return utils.default_process(key)


def fuzz_match(
    query: str,
    choices: list,
    limit: int,
    entities: List[NamedEntity],
    scorer: const.FuzzScorer = "token_sort_ratio",
) -> MatchList:
    scorer = getattr(fuzz, scorer, fuzz.token_sort_ratio)

    # https://rapidfuzz.github.io/RapidFuzz/Usage/process.html#extract
    extract = process.extract(
        query=query,
        choices=choices,
        scorer=scorer,
        limit=limit,
    )

    match_list = MatchList()
    for key, similarity, index in extract:
        entity = entities[index]
        is_alias = fuzz_clean(entity.value) != key
        m = Match(key=key, entity=entity, is_alias=is_alias, score=similarity)
        match_list.append(m)
    return match_list


def Fuzz(
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
    return AbstractType(
        lookup,
        EntityType=NamedEntity,
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
        super().__init__(
            source,
            case_sensitive=case_sensitive,
            tiebreaker_mode=tiebreaker_mode,
        )
        self.clean: list[str] = []
        self.entities: list[NamedEntity] = []
        self.fuzz_limit = fuzz_limit
        self.fuzz_min_score = fuzz_min_score
        self.fuzz_scorer = fuzz_scorer

    def _add(self, entity: NamedEntity):
        super()._add(entity)

        clean_name: str = fuzz_clean(entity.value)
        self.clean.append(clean_name)
        self.entities.append(entity)

        for alias in entity.aliases:
            clean_alias: str = fuzz_clean(alias)
            self.clean.append(clean_alias)
            self.entities.append(entity)

    def _get(self, key: str) -> MatchList:
        # Attempt to resolve the value using exact and alias matches first
        match_list = super()._get(key)

        if not match_list:
            query = fuzz_clean(key)

            match_list = fuzz_match(
                query,
                self.clean,
                scorer=self.fuzz_scorer,
                limit=self.fuzz_limit,
                entities=self.entities,
            )

            match_list.apply(self.fuzz_min_score, self.tiebreaker_mode)

        return match_list
