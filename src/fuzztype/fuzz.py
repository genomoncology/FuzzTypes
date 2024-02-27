from typing import NamedTuple, List, Sequence, Hashable, Union, Tuple

from rapidfuzz import fuzz, process
from rapidfuzz.utils import default_process

from . import const, Entity


def fuzz_clean(key: str) -> str:
    # no really, it's a string
    # noinspection PyTypeChecker
    return default_process(key)


class FuzzMatch(NamedTuple):
    key: str
    score: float
    entity: Entity

    @property
    def rank(self) -> Tuple[float, int]:
        return -1 * self.score, self.entity.rank

    def __lt__(self, other: "FuzzMatch"):
        # noinspection PyTypeChecker
        return (self.rank, self.entity.name) < (other.rank, other.entity.name)

    @property
    def is_alias(self):
        return fuzz_clean(self.entity.name) != self.key

    def __str__(self):
        if self.is_alias:
            return f"{self.key} => {self.entity.name} [{self.score:.1f}]"
        else:
            return f"{self.entity.name} [{self.score:.1f}]"


LookupReturn = Union[Entity, FuzzMatch, None]


def fuzz_match(
    query: str,
    choices: list,
    limit: int,
    entities: List[Entity],
    scorer: const.FuzzScorer = "token_sort_ratio",
) -> List[FuzzMatch]:
    scorer = getattr(fuzz, scorer, fuzz.token_sort_ratio)

    # https://rapidfuzz.github.io/RapidFuzz/Usage/process.html#extract
    extract = process.extract(
        query=query,
        choices=choices,
        scorer=scorer,
        limit=limit,
    )

    matches: List[FuzzMatch] = []
    for key, similarity, index in extract:
        matches.append(FuzzMatch(key, similarity, entities[index]))
    return matches
