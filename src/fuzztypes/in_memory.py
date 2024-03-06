from typing import Callable, Iterable, Optional, Union

from pydantic import PositiveInt

from fuzztypes import (
    EntityDict,
    Match,
    MatchList,
    NamedEntity,
    abstract,
    const,
    flags,
)


class InMemoryStorage(abstract.AbstractStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.by_name = EntityDict(self.case_sensitive, self.tiebreaker_mode)
        self.by_alias = EntityDict(self.case_sensitive, self.tiebreaker_mode)

        # in-memory storage
        self._terms: list[str] = []
        self._entities: list[NamedEntity] = []
        self._embeddings = None

    #
    # Add Entities
    #

    def add(self, entity: NamedEntity) -> None:
        if self.search_mode.is_name_ok:
            self.by_name[entity.value] = entity

        if self.search_mode.is_alias_ok:
            for alias in entity.aliases:
                self.by_alias[alias] = entity

        if self.search_mode.is_fuzz_or_semantic_ok:
            clean_name: str = self.fuzz_clean(entity.value)
            self._terms.append(clean_name)
            self._entities.append(entity)

            if self.search_mode.is_alias_ok:
                for alias in entity.aliases:
                    clean_alias: str = self.fuzz_clean(alias)
                    self._terms.append(clean_alias)
                    self._entities.append(entity)

    #
    # Name and Alias Matching
    #

    def get_by_name(self, key: str) -> Optional[MatchList]:
        if self.search_mode.is_name_ok:
            entity = self.by_name[key]
            if entity:
                matches = MatchList()
                matches.set(key=key, entity=entity, is_alias=False)
                return matches

    def get_by_alias(self, key) -> Optional[MatchList]:
        if self.search_mode.is_alias_ok:
            entity = self.by_alias[key]
            if entity:
                matches = MatchList()
                matches.set(key=key, entity=entity, is_alias=True)
                return matches

    #
    # Fuzzy Matching
    #

    def get_by_fuzz(self, key) -> MatchList:
        query = self.fuzz_clean(key)
        matches = self.fuzz_match(query, self._terms)
        matches.apply(self.fuzz_min_score, self.tiebreaker_mode)
        return matches

    @property
    def rapidfuzz(self):
        try:
            # Note: rapidfuzz is an MIT licensed optional dependency.
            # You must import it yourself to use this functionality.
            # https://github.com/rapidfuzz/RapidFuzz
            import rapidfuzz
        except ImportError:  # pragma: no cover
            raise RuntimeError("Import Failed: `pip install rapidfuzz`")

        return rapidfuzz

    def fuzz_clean(self, key: str) -> str:
        # no really, it's a string
        # noinspection PyTypeChecker
        return self.rapidfuzz.utils.default_process(key)

    def fuzz_match(
        self,
        query: str,
        choices: list,
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
    # Semantic Similarity Matching
    #
    def get_by_semantic(self, key) -> MatchList:
        match_list = MatchList()
        indices, scores = self.find_knn(key)
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
            match_list.append(match)

        match_list.apply(self.sem_min_score, self.tiebreaker_mode)
        return match_list

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
        k_nearest_indices = np.argsort(-similarities)[: self.sem_limit]

        # Get the top-k similarities
        top_k_similarities = similarities[k_nearest_indices]

        return k_nearest_indices, top_k_similarities


def InMemory(
    source: Iterable,
    *,
    case_sensitive: bool = False,
    examples: list = None,
    fuzz_limit: PositiveInt = 5,
    fuzz_min_score: float = 80.0,
    fuzz_scorer: const.FuzzScorer = "token_sort_ratio",
    notfound_mode: const.NotFoundMode = "raise",
    search_mode: flags.SearchType = flags.DefaultSearch,
    sem_encoder: Union[Callable, str, object] = None,
    sem_limit: int = 5,
    sem_min_score: float = 80.0,
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
):
    storage = InMemoryStorage(
        source,
        case_sensitive=case_sensitive,
        fuzz_limit=fuzz_limit,
        fuzz_min_score=fuzz_min_score,
        fuzz_scorer=fuzz_scorer,
        search_mode=search_mode,
        sem_encoder=sem_encoder,
        sem_limit=sem_limit,
        sem_min_score=sem_min_score,
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
