from typing import List, Tuple, Optional, Iterator, Any

from pydantic import BaseModel, Field, model_validator

from . import Entity, const


class Match(BaseModel):
    key: Any
    entity: Entity
    is_alias: bool = False
    score: float = 100.0
    term: Optional[str] = None

    @model_validator(mode="after")
    def set_term(self):
        if self.term is None:
            self.term = self.key

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

    def __iter__(self) -> Iterator[Match]:
        return iter(self.matches)

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

    def apply(self, min_score: float, tiebreaker_mode: const.TiebreakerMode):
        """Filter matches by score, sort by rank/alpha, and make choice."""
        allowed = sorted(m for m in self.matches if m.score >= min_score)
        count = len(allowed)

        if count == 1:
            self.choice = allowed[0]

        elif count > 1:
            if tiebreaker_mode == "raise":
                if allowed[0].rank != allowed[1].rank:
                    self.choice = allowed[0]

            elif tiebreaker_mode == "lesser":
                self.choice = allowed[0]

            elif tiebreaker_mode == "greater":
                self.choice = allowed[-1]
