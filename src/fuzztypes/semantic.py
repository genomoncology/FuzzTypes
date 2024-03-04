"""
Match by name or alias via vector-based semantic similarity search.

Default model is paraphrase-MiniLM-L6-v2 which has been trained to focus
on paraphrasing and semantic similarity.
https://www.sbert.net/examples/applications/paraphrase-mining/README.html

Uses np.dot to calculate the cosine similarity between the vector of the
input string and the collection of vectors of the names and synonyms. If
you want to use a different approach, either inherit this class and override
the nearest neighbors function.

You can also integrate a vector database or other solution via the Function
fuzz type found in function.py.
"""
import hashlib
import os
import pickle
from typing import Iterable

from . import (
    NamedEntity,
    AbstractType,
    MatchList,
    const,
    Match,
    AliasLookup,
)


def Semantic(
    source: Iterable,
    *,
    case_sensitive: bool = False,
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    sem_limit: int = 5,
    sem_model_name: str = "sentence-transformers/paraphrase-MiniLM-L6-v2",
    sem_min_score: float = 80.0,
    sem_skip_aliases: bool = False,
    tiebreaker_mode: const.TiebreakerMode = "raise",
    validator_mode: const.ValidatorMode = "before",
) -> AbstractType:
    lookup = SemanticLookup(
        source,
        case_sensitive=case_sensitive,
        sem_limit=sem_limit,
        sem_min_score=sem_min_score,
        sem_model_name=sem_model_name,
        sem_skip_aliases=sem_skip_aliases,
        tiebreaker_mode=tiebreaker_mode,
    )
    return AbstractType(
        lookup,
        EntityType=NamedEntity,
        examples=examples,
        input_type=str,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )


class SemanticLookup(AliasLookup):
    def __init__(
        self,
        source: Iterable[NamedEntity],
        *,
        case_sensitive: bool,
        sem_limit: int,
        sem_min_score: float,
        sem_model_name: str,
        sem_skip_aliases: bool,
        tiebreaker_mode: const.TiebreakerMode,
    ):
        super().__init__(
            source,
            case_sensitive=case_sensitive,
            tiebreaker_mode=tiebreaker_mode,
        )
        self.sem_model_name = sem_model_name
        self.sem_limit = sem_limit
        self.sem_min_score = sem_min_score
        self.sem_skip_aliases = sem_skip_aliases
        self.terms: list[str] = []
        self.entities: list[NamedEntity] = []
        self.embeddings = None
        self._encoder = None

    @property
    def encoder(self):
        if self._encoder is None:
            try:
                # Note: sentence-transformers is an Apache 2.0 licensed
                # optional dependency.
                # You must import it yourself to use this functionality.
                # https://github.com/UKPLab/sentence-transformers
                from sentence_transformers import SentenceTransformer

            except ImportError:  # pragma: no cover
                raise RuntimeError(
                    "Import Failed: `pip install sentence-transformers`"
                )

            self._encoder = SentenceTransformer(self.sem_model_name)

        return self._encoder

    def _prep(self):
        super(SemanticLookup, self)._prep()

        if self.embeddings is None:
            self.embeddings = self._load_embeddings()
            if self.embeddings is None:
                self.embeddings = self.encoder.encode(self.terms)
                self._store_embeddings(self.embeddings)

    def _add(self, entity: NamedEntity):
        super()._add(entity)

        self.terms.append(entity.value)
        self.entities.append(entity)

        if not self.sem_skip_aliases:
            for alias in entity.aliases:
                self.terms.append(alias)
                self.entities.append(entity)

    def _get(self, key: str) -> MatchList:
        # Attempt to resolve the value using exact and alias matches first
        match_list = super()._get(key)

        if not match_list:
            indices, scores = self.find_knn(key)
            for index, score in zip(indices, scores):
                entity = self.entities[index]
                term = self.terms[index]
                is_alias = term != self.entities[index].value
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

    def _get_hash_path(self) -> str:
        # determine cache directory path using environment variable
        fuzztypes_dir = os.getenv("FUZZTYPES_DIR", "~/.local/fuzztypes/")
        cache_dir = os.path.join(os.path.expanduser(fuzztypes_dir), "cache")
        os.makedirs(cache_dir, exist_ok=True)

        # calculate MD5 digest of model name + sorted terms
        terms_str = self.sem_model_name + "|".join(sorted(self.terms))
        hash_object = hashlib.md5(terms_str.encode())
        digest = hash_object.hexdigest()

        hash_path = os.path.join(cache_dir, f"{digest}.pkl")
        return hash_path

    def _load_embeddings(self):
        hash_path = self._get_hash_path()
        if os.path.exists(hash_path):
            with open(hash_path, "rb") as f:
                return pickle.load(f)

    def _store_embeddings(self, embeddings):
        hash_path = self._get_hash_path()
        with open(hash_path, "wb") as f:
            pickle.dump(embeddings, f)

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
