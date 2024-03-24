from datetime import date, datetime
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
)

from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    json_schema,
)
from pydantic_core import CoreSchema, PydanticCustomError, core_schema

from fuzztypes import Entity, MatchResult, const

T = TypeVar("T")

SupportedType = Union[
    str, float, int, dict, list, date, datetime, BaseModel, T
]


class _AbstractTypeMeta(type, Generic[T]):
    def __getitem__(cls: Type[T], key: Any) -> Entity[T]:
        """
        Get the entity associated with the given key using dictionary-like
        access.

        This method allows retrieving the entity using dictionary-like
        syntax (e.g., AbstractType[key]).

        If entity found, it is returned.
        If entity not found, raise a KeyError based on PydanticCustomError.
        """
        try:
            return cls.lookup(key)  # type: ignore
        except PydanticCustomError as err:
            raise KeyError(f"Key Error: {key} [{err}]") from err


def AbstractType(
    lookup_function: Callable[[T], MatchResult],
    *,
    EntityType: Type[Entity] = Entity,
    examples: Optional[list] = None,
    input_type: Type[SupportedType] = str,
    notfound_mode: const.NotFoundMode = "raise",
    output_type: Optional[Type[T]] = None,
    validator_mode: const.ValidatorMode = "before",
) -> _AbstractTypeMeta:
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

    # noinspection PyClassHasNoInit
    class _AbstractType(metaclass=_AbstractTypeMeta):
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
            validation_function_map: Dict[str, Callable] = {
                "before": core_schema.no_info_before_validator_function,
                "after": core_schema.no_info_before_validator_function,
                "plain": core_schema.no_info_plain_validator_function,
                "wrap": core_schema.no_info_wrap_validator_function,
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

        def __new__(cls, key: T) -> Optional[T]:  # type: ignore
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
            return entity.resolve() if entity else None

        @classmethod
        def lookup(cls, key: T) -> Optional[Entity[T]]:
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
            match_list: MatchResult = lookup_function(key)

            if match_list.choice is not None:
                return match_list.entity

            if notfound_mode == "allow":
                return EntityType(value=key)

            if notfound_mode == "none":
                return None

            msg = "key ({key}) could not be resolved"
            ctx: Dict[str, Any] = dict(key=key)
            if match_list:
                ctx["near"] = [str(m) for m in match_list]
                msg += f", closest non-matches = {match_list}"
            raise PydanticCustomError("key_not_found", msg, ctx)

    return _AbstractType
