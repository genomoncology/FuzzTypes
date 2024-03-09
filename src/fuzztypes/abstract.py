from datetime import date, datetime
from typing import Any, Callable, Type, Union, Optional, Iterable, List

from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    json_schema,
)
from pydantic_core import CoreSchema, PydanticCustomError, core_schema

from fuzztypes import NamedEntity, Entity, MatchList, const, flags

SupportedType = Union[str, float, int, dict, list, date, datetime, BaseModel]


def AbstractType(
    lookup_function: Callable[[str], MatchList],
    *,
    EntityType: Type = Entity,
    examples: list = None,
    input_type: Type[SupportedType] = str,
    notfound_mode: const.NotFoundMode = "raise",
    output_type: Type[SupportedType] = None,
    validator_mode: const.ValidatorMode = "before",
):
    """
    Factory function to create a specialized AbstractType, which is a Pydantic
    based type with added fuzzy matching capabilities.

    :param lookup_function: Function to perform the lookup.
    :param EntityType: Type of Entity (e.g. NamedEntity) to return.
    :param examples: Example values used in schema generation.
    :param input_type: The underlying Python data type.
    :param notfound_mode: 'raise' an error, set 'none', or 'allow' unknown key.
    :param output_type: Specify only if different from input_type.
    :param validator_mode: Validation mode ('before', 'after', 'plain', 'wrap')
    :return: A specialized AbstractType based on the provided specifications.
    """

    output_type = output_type or input_type

    # noinspection PyClassHasNoInit
    class _AbstractType(output_type):
        @classmethod
        def __get_pydantic_core_schema__(
            cls,
            source_type: type,
            handler: GetCoreSchemaHandler,
        ) -> CoreSchema:
            validation_function_map = {
                "before": core_schema.with_info_before_validator_function,
                "after": core_schema.with_info_before_validator_function,
                "plain": core_schema.with_info_plain_validator_function,
                "wrap": core_schema.with_info_wrap_validator_function,
            }

            validation_function = validation_function_map[validator_mode]
            in_schema = handler(input_type)

            if output_type and output_type != input_type:
                # used for Person where name (str) or Person (BaseModel) used.
                out_schema = handler(output_type)
                in_schema = core_schema.union_schema([in_schema, out_schema])

            if notfound_mode == "none":
                in_schema = core_schema.nullable_schema(in_schema)

            return validation_function(cls.get_value, in_schema)

        @classmethod
        def __get_pydantic_json_schema__(
            cls,
            schema: CoreSchema,
            handler: GetJsonSchemaHandler,
        ) -> json_schema.JsonSchemaValue:
            schema = handler(schema)
            if examples is not None:
                schema["examples"] = examples
            return schema

        @classmethod
        def find_matches(cls, key: str) -> MatchList:
            return lookup_function(key)

        @classmethod
        def lookup(cls, key: str) -> Optional[EntityType]:
            match_list: MatchList = cls.find_matches(key)

            if match_list.success:
                return match_list.entity

            #
            # todo: Move to Storage to allow for collection of new entities.
            #
            if notfound_mode == "allow":
                return EntityType(value=key)

            if notfound_mode == "none":
                return

            msg = "key ({key}) could not be resolved"
            ctx = dict(key=key)
            if match_list:
                ctx["near"] = [str(m) for m in match_list]
                msg += f", potential matches = {match_list}"
            raise PydanticCustomError("key_not_found", msg, ctx)

        @classmethod
        def get_value(cls, key: str, _ignore=None) -> Optional[Any]:
            entity = cls.lookup(key)
            if entity:
                return entity.value

        @classmethod
        def get_entity(cls, key: str) -> Optional[EntityType]:
            try:
                return cls.lookup(key)
            except PydanticCustomError:
                pass

        @classmethod
        def __class_getitem__(cls, key) -> EntityType:
            try:
                return cls.lookup(key)
            except PydanticCustomError as err:
                raise KeyError(f"Key Error: {key} [{err}]") from err

    return _AbstractType


class AbstractStorage:
    def __init__(
        self,
        source: Iterable[NamedEntity],
        *,
        case_sensitive: bool = False,
        device: const.DeviceList = "cpu",
        fuzz_scorer: str = "token_sort_ratio",
        limit: int = 10,
        min_similarity: float = 80.0,
        search_flag: flags.SearchFlag = flags.DefaultSearch,
        vect_encoder: Union[Callable, str, object] = None,
        vect_dimensions: int = 384,
        tiebreaker_mode: const.TiebreakerMode = "raise",
    ):
        self.source = source

        # options
        self.case_sensitive = case_sensitive
        self.device = device
        self.fuzz_scorer = fuzz_scorer
        self.limit = limit
        self.min_similarity = min_similarity
        self.prepped = False
        self.search_flag = search_flag
        self.tiebreaker_mode = tiebreaker_mode
        self.vect_dimensions = vect_dimensions
        self.vect_encoder = vect_encoder

    def __call__(self, key: str) -> MatchList:
        if not self.prepped:
            self.prepped = True
            self.prepare()

        match_list = self.get(key)
        match_list.choose(self.min_similarity, self.tiebreaker_mode)
        return match_list

    def normalize(self, key: str):
        if self.case_sensitive:
            return key
        else:
            return key.lower()

    @property
    def encoder(self):
        if self.vect_encoder is None:
            self.vect_encoder = const.DefaultEncoder

        if isinstance(self.vect_encoder, str):
            try:
                # Note: sentence-transformers is an Apache 2.0 licensed
                # optional dependency.
                # You must import it yourself to use this functionality.
                # https://github.com/UKPLab/sentence-transformers
                from sentence_transformers import SentenceTransformer

            except ImportError as err:
                raise RuntimeError(
                    "Import Failed: `pip install sentence-transformers`"
                ) from err

            self.vect_encoder = SentenceTransformer(self.vect_encoder)

        return self.vect_encoder

    def encode(self, values: List[str]):
        return self.encoder.encode(values, device=self.device)

    def prepare(self):
        raise NotImplementedError

    def get(self, key: str) -> MatchList:
        raise NotImplementedError
