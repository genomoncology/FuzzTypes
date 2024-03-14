from datetime import date, datetime
from typing import Any, Callable, Type, Union, Optional, Iterable, List

from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    json_schema,
)
from pydantic_core import CoreSchema, PydanticCustomError, core_schema

from fuzztypes import NamedEntity, Entity, MatchList, const, flags, lazy

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
            """
            Generate the Pydantic core schema for the AbstractType.

            This method is used internally by Pydantic to generate the schema
            based on the provided validation mode and input/output types.
            """
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

            return validation_function(cls, in_schema)

        @classmethod
        def __get_pydantic_json_schema__(
            cls,
            schema: CoreSchema,
            handler: GetJsonSchemaHandler,
        ) -> json_schema.JsonSchemaValue:
            """
            Generate the JSON schema for the AbstractType.

            This method is used internally by Pydantic to generate the JSON
            schema representation of the AbstractType, including any examples.
            """
            schema = handler(schema)
            if examples is not None:
                schema["examples"] = examples
            return schema

        def __new__(cls, key: str, _: Any = None) -> Optional[Any]:
            """
            Doesn't create an AbstractType, it's actually a class-level
            __call__ function.

            Pydantic core schema logic will pass an additional argument
            that can be ignored.

            It retrieves the entity associated with the provided key.
            If an entity is found, it returns the value of the entity.
            If no entity is found, it returns None.
            If an exception is raised, it is will not be caught.
            """
            entity = cls.lookup(key)
            if entity:
                return entity.value

        @classmethod
        def __class_getitem__(cls, key) -> EntityType:
            """
            Get the entity associated with the given key using dictionary-like
            access.

            This method allows retrieving the entity using dictionary-like
            syntax (e.g., AbstractType[key]).

            If entity found, it is returned.
            If entity not found, raise a KeyError based on PydanticCustomError.
            """
            try:
                return cls.lookup(key)
            except PydanticCustomError as err:
                raise KeyError(f"Key Error: {key} [{err}]") from err

        @classmethod
        def lookup(cls, key: str) -> Optional[EntityType]:
            """
            Lookup the entity for the given key.

            This method attempts to find the entity associated with the
            provided key.

            If a match is found, it returns the corresponding entity.

            If no match is found, takes action based on the notfound_mode:
                "none": returns None (if notfound_mode is "none")
                "allow": returns an entity with the key as value
                "raise": raises a PydanticCustomError
            """
            match_list: MatchList = lookup_function(key)

            if match_list.success:
                return match_list.entity

            if notfound_mode == "allow":
                return EntityType(value=key)

            if notfound_mode == "none":
                return

            msg = "key ({key}) could not be resolved"
            ctx = dict(key=key)
            if match_list:
                ctx["near"] = [str(m) for m in match_list]
                msg += f", closest non-matches = {match_list}"
            raise PydanticCustomError("key_not_found", msg, ctx)

    return _AbstractType


class AbstractStorage:
    def __init__(
        self,
        source: Iterable[NamedEntity],
        *,
        case_sensitive: bool = False,
        encoder: Union[Callable, str, object] = None,
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
        self.limit = limit
        self.min_similarity = min_similarity
        self.prepped = False
        self.search_flag = search_flag
        self.tiebreaker_mode = tiebreaker_mode

        # store string for lazy loading
        self._fuzz_scorer = fuzz_scorer
        self._encoder = encoder
        self._vect_dimensions = None

    def __call__(self, key: str) -> MatchList:
        if not self.prepped:
            self.prepped = True
            self.prepare()

        match_list = self.get(key)
        match_list.choose(self.min_similarity, self.tiebreaker_mode)
        return match_list

    def prepare(self):
        raise NotImplementedError

    def get(self, key: str) -> MatchList:
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
