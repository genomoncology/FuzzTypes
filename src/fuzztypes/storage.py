from typing import Callable, Iterable, List, Type, Union

from fuzztypes import NamedEntity, MatchResult, const, flags, lazy


class AbstractStorage:
    def __init__(
            self,
            source: Iterable[NamedEntity],
            *,
            case_sensitive: bool = False,
            encoder: Union[Callable, str, object] = None,
            entity_type: Type[NamedEntity] = NamedEntity,
            device: const.DeviceList = "cpu",
            fuzz_scorer: str = "token_sort_ratio",
            limit: int = 10,
            min_similarity: float = 80.0,
            search_flag: flags.SearchFlag = flags.DefaultSearch,
            tiebreaker_mode: const.TiebreakerMode = "raise",
    ):
        assert not search_flag.is_hybrid, "Hybrid search not yet supported!"

        self.source = source

        # options
        self.case_sensitive = case_sensitive
        self.device = device
        self.entity_type = entity_type
        self.limit = limit
        self.min_similarity = min_similarity
        self.prepped = False
        self.search_flag = search_flag
        self.tiebreaker_mode = tiebreaker_mode

        # store string for lazy loading
        self._fuzz_scorer = fuzz_scorer
        self._encoder = encoder
        self._vect_dimensions = None

    def __call__(self, key: str) -> MatchResult:
        if not self.prepped:
            self.prepped = True
            self.prepare()

        match_list = self.get(key)
        match_list.choose(self.min_similarity, self.tiebreaker_mode)
        return match_list

    def prepare(self):
        raise NotImplementedError

    def get(self, key: str) -> MatchResult:
        raise NotImplementedError

    def normalize(self, key: str):
        if key:
            key = key.strip()
            if self.case_sensitive:
                return key
            else:
                return key.lower()

    #
    # encoding
    #

    @property
    def encoder(self):
        return lazy.create_encoder(self._encoder, device=self.device)

    @property
    def vect_dimensions(self):
        if self._vect_dimensions is None:
            dummy_encoded = self.encode([""])
            self._vect_dimensions = dummy_encoded.shape[1]
        return self._vect_dimensions

    def encode(self, values: List[str]):
        return self.encoder(
            values,
        )

    #
    # fuzzy matching
    #

    @property
    def rapidfuzz(self):
        return lazy.lazy_import("rapidfuzz")

    @property
    def fuzz_scorer(self):
        return getattr(
            self.rapidfuzz.fuzz,
            self._fuzz_scorer,
            self.rapidfuzz.fuzz.token_sort_ratio,
        )

    def fuzz_clean(self, term: str) -> str:
        # no really, it's a string
        # noinspection PyTypeChecker
        return self.rapidfuzz.utils.default_process(term)
