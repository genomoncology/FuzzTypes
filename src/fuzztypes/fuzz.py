from typing import List

from rapidfuzz import fuzz, process
from rapidfuzz.utils import default_process

from . import const, NamedEntity, Match, MatchList


def fuzz_clean(key: str) -> str:
    # no really, it's a string
    # noinspection PyTypeChecker
    return default_process(key)


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
        is_alias = fuzz_clean(entity.name) != key
        m = Match(key=key, entity=entity, is_alias=is_alias, score=similarity)
        match_list.append(m)
    return match_list
