from typing import List, Tuple, Optional, Iterator, Any, Union

from pydantic import BaseModel, Field

from . import Entity, NamedEntity, const


class Match(BaseModel):
    key: Any
    entity: Entity
    is_alias: bool = False
    score: float = 100.0
    term: Optional[str] = None

    @property
    def rank(self) -> Tuple[float, int]:
        return -1 * self.score, self.entity.rank

    @property
    def rank_value(self) -> Tuple[Tuple[float, int], Any]:
        return self.rank, self.entity.value

    def __lt__(self, other: "Match"):
        return self.rank_value < other.rank_value

    def __str__(self):
        if self.is_alias:
            return f"{self.key} => {self.entity.value} [{self.score:.1f}]"
        else:
            return f"{self.entity.value} [{self.score:.1f}]"


class MatchList(BaseModel):
    matches: List[Match] = Field(default_factory=list)
    choice: Optional[Match] = None

    def __bool__(self):
        return bool(self.matches)

    def __len__(self):
        return len(self.matches)

    def __iter__(self) -> Iterator[Match]:
        return iter(self.matches)

    def __getitem__(self, item):
        return self.matches[item]

    def __str__(self):
        return ", ".join(map(str, self.matches))

    @property
    def success(self):
        return self.choice is not None

    @property
    def entity(self):
        return self.success and self.choice.entity

    def set(
        self,
        key: str,
        entity: Entity,
        is_alias: bool = False,
        term: str = None,
    ):
        """If match is a known winner, just set it and forget it."""
        match = Match(key=key, entity=entity, is_alias=is_alias, term=term)
        self.choice = match
        self.matches.append(match)

    def append(self, match: Match):
        """Add a match to the list of potential matches."""
        self.matches.append(match)

    def choose(self, min_score: float, tiebreaker_mode: const.TiebreakerMode):
        """Filter matches by score, sort by rank/alpha, and make choice."""
        allowed = sorted(m for m in self.matches if m.score >= min_score)
        count = len(allowed)

        if count == 1:
            self.choice = allowed[0]

        elif count > 1:
            first = allowed[0]
            tied = [
                m
                for m in allowed[1:]
                if m.rank == first.rank and m.entity != first.entity
            ]

            if not tied or tiebreaker_mode == "lesser":
                self.choice = first

            elif tiebreaker_mode == "greater":
                self.choice = tied[-1]


class Record(BaseModel):
    entity: Union[NamedEntity, str]
    term: str
    is_alias: bool
    vector: Any = None

    def deserialize(self):
        if isinstance(self.entity, str):
            self.entity = NamedEntity.model_validate_json(self.entity)

    @classmethod
    def from_list(cls, recs: list, key, score: float = 100.0) -> List[Match]:
        return [record.to_match(key, score) for record in recs]

    def to_match(self, key, score: float = 100.0) -> Match:
        self.deserialize()
        return Match(
            key=key,
            entity=self.entity,
            is_alias=self.is_alias,
            score=score,
            term=self.term,
        )
