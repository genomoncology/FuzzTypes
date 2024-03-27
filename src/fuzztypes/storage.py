from typing import Any, Callable, Dict, Iterable, List, Optional, Type, Union

from pydantic_core import PydanticCustomError

from fuzztypes import NamedEntity, MatchResult, const, flags, lazy


class AbstractStorage:
    def __init__(
        self,
        source: Iterable,
        *,
        case_sensitive: bool = False,
        device: const.DeviceList = "cpu",
        encoder: Union[Callable, str, object] = None,
        entity_type: Type[NamedEntity] = NamedEntity,
        fuzz_scorer: const.FuzzScorer = "token_sort_ratio",
        limit: int = 10,
        min_similarity: float = 80.0,
        notfound_mode: const.NotFoundMode = "raise",
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
        self.notfound_mode = notfound_mode
        self.prepped = False
        self.search_flag = search_flag
        self.tiebreaker_mode = tiebreaker_mode

        # store string for lazy loading
        self._fuzz_scorer_str = fuzz_scorer
        self._fuzz_scorer = None
        self._encoder = encoder
        self._vect_dimensions = None

    def __call__(self, key: str) -> Optional[Any]:
        entity = self[key]
        return entity.resolve() if entity else None

    def __getitem__(self, key: str) -> Optional[NamedEntity]:
        result = self.match(key)

        if result and result.choice is not None:
            return result.entity

        if self.notfound_mode == "allow":
            return self.entity_type(value=key)

        if self.notfound_mode == "none":
            return None

        ctx: Dict[str, Any] = dict(key=key)
        if result:
            msg = result.error_message(key)
            ctx["result"] = result.model_dump(
                exclude_defaults=True, exclude_none=True
            )
        else:
            msg = f'"{key}" could not be resolved'

        raise PydanticCustomError("key_not_found", msg, ctx)

    def prepare(self):
        raise NotImplementedError

    def match(self, key: str) -> MatchResult:
        if not self.prepped:
            self.prepped = True
            self.prepare()

        match_result = self.get(key)
        match_result.choose(self.min_similarity, self.tiebreaker_mode)
        return match_result

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
        return self.encoder(values)

    #
    # fuzzy matching
    #

    @property
    def rapidfuzz(self):
        return lazy.lazy_import("rapidfuzz")

    @property
    def fuzz_scorer(self):
        if self._fuzz_scorer is None:
            self._fuzz_scorer = getattr(
                self.rapidfuzz.fuzz,
                self._fuzz_scorer_str,
                self.rapidfuzz.fuzz.token_sort_ratio,
            )
        return self._fuzz_scorer

    def set_fuzz_scorer(self, fuzz_scorer: const.FuzzScorer):
        self._fuzz_scorer_str = fuzz_scorer
        self._fuzz_scorer = None

    def fuzz_clean(self, term: str) -> str:
        # no really, it's a string
        # noinspection PyTypeChecker
        return self.rapidfuzz.utils.default_process(term)
