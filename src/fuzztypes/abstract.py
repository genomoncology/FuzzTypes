from typing import Any, Callable, Type, Union, Optional

from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    json_schema,
)
from pydantic_core import CoreSchema, core_schema, PydanticCustomError
from pydantic import BaseModel
from datetime import date, datetime

from . import Entity, MatchList, const

SupportedType = Union[str, float, int, dict, list, date, datetime, BaseModel]


def AbstractType(
    lookup_function: Callable[[str], MatchList],
    *,
    EntityType: Type = Entity,
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    python_type: Type[SupportedType] = str,
    schema_alt_type: Type[SupportedType] = None,
    validator_mode: const.ValidatorMode = "before",
):
    """
    Factory function to create a specialized AbstractType, which is a Pydantic
    based type with added fuzzy matching capabilities.

    :param lookup_function: Function to perform the lookup.
    :param EntityType: Type of Entity (e.g. NamedEntity) to return.
    :param examples: Example values used in schema generation.
    :param notfound_mode: 'raise' an error, set 'none', or 'allow' unknown key.
    :param python_type: The underlying Python data type.
    :param schema_alt_type: Alternate type to combine with python_type.
    :param validator_mode: Validation mode ('before', 'after', 'plain', 'wrap')
    :return: A specialized AbstractType based on the provided specifications.
    """

    # noinspection PyClassHasNoInit
    class _AbstractType(python_type):
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
            py_schema = handler(python_type)

            if schema_alt_type:
                # used for Person where name (str) or Person (BaseModel) used.
                alt_schema = handler(schema_alt_type)
                py_schema = core_schema.union_schema([py_schema, alt_schema])

            if notfound_mode == "none":
                py_schema = core_schema.nullable_schema(py_schema)

            return validation_function(cls.get_value, py_schema)

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

            if notfound_mode == "allow":
                return EntityType(value=key)

            if notfound_mode == "none":
                return

            msg = "key ({key}) not resolved"
            ctx = dict(key=key)
            if match_list:
                ctx["near"] = [str(m) for m in match_list]
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
            except PydanticCustomError:
                raise KeyError("Key Error: {key}")

    return _AbstractType
