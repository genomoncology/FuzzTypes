from collections import defaultdict
from typing import Callable, Iterable, Optional, Union, List, Dict

from pydantic import BaseModel, PositiveInt

from fuzztypes import (
    Match,
    MatchList,
    NamedEntity,
    abstract,
    const,
    flags,
)


class Record(BaseModel):
    entity: NamedEntity
    term: str
    is_alias: bool

    @classmethod
    def from_list(
        cls, records: list, key, score: float = 100.0
    ) -> List[Match]:
        return [Record.to_match(record, key, score) for record in records]

    @classmethod
    def to_match(cls, record, key, score: float = 100.0) -> Match:
        return Match(
            key=key,
            entity=record.entity,
            is_alias=record.is_alias,
            score=score,
        )


class InMemoryStorage(abstract.AbstractStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # in-memory storage
        self._mapping: Dict[str, List[Record]] = defaultdict(list)
        self._terms: list[str] = []
        self._entities: list[NamedEntity] = []
        self._embeddings = None

    #
    # Prepare
    #

    def prepare(self):
        for item in self.source:
            entity = NamedEntity.convert(item)
            self.add(entity)

    def add(self, entity: NamedEntity) -> None:
        if self.search_flag.is_name_ok:
            self.add_by_name(entity)

        if self.search_flag.is_alias_ok:
            self.add_by_alias(entity)

        if self.search_flag.is_fuzz_or_semantic_ok:
            self.add_fuzz_or_semantic(entity)

    def add_by_name(self, entity: NamedEntity) -> None:
        term = entity.value
        record = Record(entity=entity, term=term, is_alias=False)
        key = term if self.case_sensitive else term.lower()
        self._mapping[key].append(record)

    def add_by_alias(self, entity: NamedEntity) -> None:
        for term in entity.aliases:
            record = Record(entity=entity, term=term, is_alias=True)
            key = term if self.case_sensitive else term.lower()
            self._mapping[key].append(record)

    def add_fuzz_or_semantic(self, entity: NamedEntity) -> None:
        clean_name: str = self.fuzz_clean(entity.value)
        self._terms.append(clean_name)
        self._entities.append(entity)

        for alias in entity.aliases:
            clean_alias: str = self.fuzz_clean(alias)
            self._terms.append(clean_alias)
            self._entities.append(entity)

    #
    # Getters
    #

    def get(self, term: str) -> MatchList:
        key = term if self.case_sensitive else term.lower()
        records = self._mapping.get(key, [])
        match_list = Record.from_list(records, key=key)

        if not match_list and self.search_flag.is_fuzz_ok:
            match_list = self.get_by_fuzz(term)

        if not match_list and self.search_flag.is_semantic_ok:
            match_list = match_list or self.get_by_semantic(term)

        matches = MatchList(matches=match_list)
        return matches

    #
    # Fuzzy Matching
    #

    def get_by_fuzz(self, term) -> MatchList:
        query = self.fuzz_clean(term)
        matches = self.fuzz_match(query)
        return matches

    @property
    def rapidfuzz(self):
        try:
            # Note: rapidfuzz is an MIT licensed optional dependency.
            # You must import it yourself to use this functionality.
            # https://github.com/rapidfuzz/RapidFuzz
            import rapidfuzz
        except ImportError:
            raise RuntimeError("Import Failed: `pip install rapidfuzz`")

        return rapidfuzz

    def fuzz_clean(self, term: str) -> str:
        # no really, it's a string
        # noinspection PyTypeChecker
        return self.rapidfuzz.utils.default_process(term)

    def fuzz_match(
        self,
        query: str,
    ) -> MatchList:
        scorer = getattr(
            self.rapidfuzz.fuzz,
            self.fuzz_scorer,
            self.rapidfuzz.fuzz.token_sort_ratio,
        )
        # https://rapidfuzz.github.io/RapidFuzz/Usage/process.html#extract
        extract = self.rapidfuzz.process.extract(
            query=query,
            choices=self._terms,
            scorer=scorer,
            limit=self.fuzz_limit,
        )

        match_list = MatchList()
        for key, similarity, index in extract:
            entity = self._entities[index]
            is_alias = self.fuzz_clean(entity.value) != key
            m = Match(
                key=key, entity=entity, is_alias=is_alias, score=similarity
            )
            match_list.append(m)
        return match_list

    #
    # Vector Similarity Search
    #

    def get_by_semantic(self, key) -> List[Match]:
        # find closest match using knn
        indices, scores = self.find_knn(key)

        # create a MatchList from the results
        matches = []
        for index, score in zip(indices, scores):
            entity = self._entities[index]
            term = self._terms[index]
            is_alias = term != self._entities[index].value
            match = Match(
                key=key,
                entity=entity,
                score=score,
                is_alias=is_alias,
                term=term,
            )
            matches.append(match)

        return matches

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = self.encoder.encode(self._terms)
        return self._embeddings

    def find_knn(self, key: str) -> tuple:
        import numpy as np

        # Encode the query
        query = self.encoder.encode([key])

        # Ensure the query is a 2D array for dot product compatibility
        # If the query is already 2D, this does not change its shape
        query = query.reshape(1, -1)

        # Compute cosine similarity (assuming vectors are normalized)
        # Transpose query to match dimensions: (n_features, 1)
        similarities = np.dot(self.embeddings, query.T).flatten()

        # Get indices of the top-k similarities
        k_nearest_indices = np.argsort(-similarities)[: self.vect_limit]

        # Get the top-k similarities
        top_k_similarities = similarities[k_nearest_indices]

        return k_nearest_indices, top_k_similarities


def InMemory(
    source: Iterable,
    *,
    case_sensitive: bool = False,
    examples: list = None,
    fuzz_limit: PositiveInt = 5,
    min_similarity: float = 80.0,
    fuzz_scorer: const.FuzzScorer = "token_sort_ratio",
    notfound_mode: const.NotFoundMode = "raise",
    search_flag: flags.SearchFlag = flags.DefaultSearch,
    vect_encoder: Union[Callable, str, object] = None,
    vect_limit: int = 5,
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    storage = InMemoryStorage(
        source,
        case_sensitive=case_sensitive,
        fuzz_limit=fuzz_limit,
        min_similarity=min_similarity,
        fuzz_scorer=fuzz_scorer,
        search_flag=search_flag,
        vect_encoder=vect_encoder,
        vect_limit=vect_limit,
        tiebreaker_mode=tiebreaker_mode,
    )

    return abstract.AbstractType(
        storage,
        EntityType=NamedEntity,
        examples=examples,
        input_type=str,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )
