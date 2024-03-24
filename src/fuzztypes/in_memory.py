from collections import defaultdict
from typing import Callable, Iterable, Union, Type, Optional

from pydantic import PositiveInt

from fuzztypes import (
    FuzzValidator,
    Match,
    MatchResult,
    NamedEntity,
    Record,
    const,
    flags,
    lazy,
    storage,
)


class InMemoryStorage(storage.AbstractStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._mapping = defaultdict(list)
        self._terms = []
        self._is_alias = []
        self._entities = []
        self._embeddings = None

    #
    # Prepare
    #

    def prepare(self):
        for item in self.source:
            entity = self.entity_type.convert(item)
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
        norm_term = self.normalize(term)
        record = Record(
            entity=entity, term=term, norm_term=norm_term, is_alias=False
        )
        self._mapping[norm_term].append(record)

    def add_by_alias(self, entity: NamedEntity) -> None:
        for term in entity.aliases:
            norm_term = self.normalize(term)
            record = Record(
                entity=entity, term=term, norm_term=norm_term, is_alias=True
            )
            self._mapping[norm_term].append(record)

    def add_fuzz_or_semantic(self, entity: NamedEntity) -> None:
        clean_name: str = self.fuzz_clean(entity.value)
        self._terms.append(clean_name)
        self._entities.append(entity)
        self._is_alias.append(False)

        for alias in entity.aliases:
            clean_alias: str = self.fuzz_clean(alias)
            self._terms.append(clean_alias)
            self._entities.append(entity)
            self._is_alias.append(True)

    #
    # Getters
    #

    def get(self, key: str) -> MatchResult:
        records = self._mapping.get(self.normalize(key), [])
        match_list = Record.from_list(
            records, key=key, entity_type=self.entity_type
        )

        results = MatchResult(matches=match_list)

        if not results:
            if self.search_flag.is_fuzz_ok:
                results = self.get_by_fuzz(key)

            if self.search_flag.is_semantic_ok:
                results = self.get_by_semantic(key)

        return results

    #
    # Fuzzy Matching
    #

    def get_by_fuzz(self, term) -> MatchResult:
        query = self.fuzz_clean(term)
        matches = self.fuzz_match(query)
        return matches

    def fuzz_match(
        self,
        query: str,
    ) -> MatchResult:
        # https://rapidfuzz.github.io/RapidFuzz/Usage/process.html#extract
        extract = self.rapidfuzz.process.extract(
            query=query,
            choices=self._terms,
            scorer=self.fuzz_scorer,
            limit=self.limit,
        )

        results = MatchResult()
        for key, score, index in extract:
            entity = self._entities[index]
            is_alias = self._is_alias[index]
            m = Match(key=key, entity=entity, is_alias=is_alias, score=score)
            results.append(m)
        return results

    #
    # Vector Similarity Search
    #

    def get_by_semantic(self, key) -> MatchResult:
        # find closest match using knn
        indices, scores = self.find_knn(key)

        # create a MatchResult from the results
        results = MatchResult()
        for index, score in zip(indices, scores):
            entity = self._entities[index]
            term = self._terms[index]
            is_alias = self._is_alias[index]
            match = Match(
                key=key,
                entity=entity,
                score=score,
                is_alias=is_alias,
                term=term,
            )
            results.append(match)

        return results

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = self.encode(self._terms)
        return self._embeddings

    def find_knn(self, key: str) -> tuple:
        np = lazy.lazy_import("numpy")
        cosine_similarity = lazy.lazy_import(
            "sklearn.metrics.pairwise", "cosine_similarity"
        )

        # Encode the query
        term = self.fuzz_clean(key)
        query = self.encode([term])[0]

        # Reshape the query to a 2D array for cosine_similarity compatibility
        query = query.reshape(1, -1)

        # Compute cosine similarity
        similarities = cosine_similarity(self.embeddings, query).flatten()

        # Normalize the scores to the range of 0 to 100
        normalized_scores = (similarities + 1) * 50

        # Get indices of the top-k similarities
        k_nearest_indices = np.argsort(-normalized_scores)[: self.limit]

        # Get the top-k normalized scores
        top_k_scores = normalized_scores[k_nearest_indices]

        return k_nearest_indices, top_k_scores


def InMemory(
    source: Iterable,
    *,
    case_sensitive: bool = False,
    encoder: Union[Callable, str, object] = None,
    entity_type: Type[NamedEntity] = NamedEntity,
    examples: Optional[list] = None,
    fuzz_scorer: const.FuzzScorer = "token_sort_ratio",
    limit: PositiveInt = 10,
    min_similarity: float = 80.0,
    notfound_mode: const.NotFoundMode = "raise",
    search_flag: flags.SearchFlag = flags.DefaultSearch,
    tiebreaker_mode: const.TiebreakerMode = "raise",
):
    in_memory = InMemoryStorage(
        source,
        case_sensitive=case_sensitive,
        encoder=encoder,
        entity_type=entity_type,
        fuzz_scorer=fuzz_scorer,
        limit=limit,
        min_similarity=min_similarity,
        notfound_mode=notfound_mode,
        search_flag=search_flag,
        tiebreaker_mode=tiebreaker_mode,
    )

    return FuzzValidator(in_memory, examples=examples)
