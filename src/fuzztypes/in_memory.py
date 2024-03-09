from collections import defaultdict
from typing import Callable, Iterable, Union, List, Dict

from pydantic import PositiveInt

from fuzztypes import (
    Match,
    MatchList,
    NamedEntity,
    Record,
    abstract,
    const,
    flags,
)


class InMemoryStorage(abstract.AbstractStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # todo: Hybrid search for InMemory types not implemented
        assert not self.search_flag.is_hybrid, "Hybrid search not supported"

        self._mapping: Dict[str, List[Record]] = defaultdict(list)
        self._terms: list[str] = []
        self._is_alias: list[bool] = []
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
        self._mapping[self.normalize(term)].append(record)

    def add_by_alias(self, entity: NamedEntity) -> None:
        for term in entity.aliases:
            record = Record(entity=entity, term=term, is_alias=True)
            key = term if self.case_sensitive else term.lower()
            self._mapping[key].append(record)

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

    def get(self, key: str) -> MatchList:
        records = self._mapping.get(self.normalize(key), [])
        match_list = Record.from_list(records, key=key)

        if not match_list:
            # todo: implement hybrid search for InMemory types
            if self.search_flag.is_fuzz_ok:
                match_list = self.get_by_fuzz(key)

            if self.search_flag.is_semantic_ok:
                match_list = self.get_by_semantic(key)

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
            limit=self.limit,
        )

        match_list = MatchList()
        for key, score, index in extract:
            entity = self._entities[index]
            is_alias = self._is_alias[index]
            m = Match(key=key, entity=entity, is_alias=is_alias, score=score)
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
            is_alias = self._is_alias[index]
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
            self._embeddings = self.encode(self._terms)
        return self._embeddings

    def find_knn(self, key: str) -> tuple:
        try:
            # numpy and sklearn are optional dependencies.
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity

        except ImportError:
            raise RuntimeError("Import Failed: `pip install scikit-learn`")

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
    examples: list = None,
    fuzz_scorer: const.FuzzScorer = "token_sort_ratio",
    limit: PositiveInt = 10,
    min_similarity: float = 80.0,
    notfound_mode: const.NotFoundMode = "raise",
    search_flag: flags.SearchFlag = flags.DefaultSearch,
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
    vect_encoder: Union[Callable, str, object] = None,
):
    storage = InMemoryStorage(
        source,
        case_sensitive=case_sensitive,
        fuzz_scorer=fuzz_scorer,
        limit=limit,
        min_similarity=min_similarity,
        search_flag=search_flag,
        tiebreaker_mode=tiebreaker_mode,
        vect_encoder=vect_encoder,
    )

    return abstract.AbstractType(
        storage,
        EntityType=NamedEntity,
        examples=examples,
        input_type=str,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )
