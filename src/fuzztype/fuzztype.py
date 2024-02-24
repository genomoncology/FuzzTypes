from typing import Callable, Literal, Type, Union

from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationInfo,
    json_schema,
)
from pydantic_core import CoreSchema, core_schema, PydanticCustomError

from . import Entity

SupportedType = Union[str, float, int, dict, list]


def FuzzType(
    lookup_function: Callable,
    python_type: Type[SupportedType] = str,
    validator_mode: Literal["before", "after", "plain", "wrap"] = "before",
    examples: list = None,
):
    """
    Factory function to create a specialized FuzzType, which is a Pydantic
    based type with added fuzzy matching capabilities.

    :param lookup_function: Function to perform the lookup.
    :param python_type: The underlying Python data type.
    :param validator_mode: Validation mode ('before', 'after', 'plain', 'wrap')
    :param examples: Examples of possible values, used in schema generation.
    :return: A specialized FuzzType based on the provided specifications.
    """

    # noinspection PyClassHasNoInit
    class _FuzzType(python_type):
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
            return validation_function(cls._validate, handler(str))

        @classmethod
        def __get_pydantic_json_schema__(
            cls,
            core_schema: CoreSchema,
            handler: GetJsonSchemaHandler,
        ) -> json_schema.JsonSchemaValue:
            json_schema = handler(core_schema)
            if examples is not None:
                json_schema["examples"] = examples
            return json_schema

        @staticmethod
        def _validate(key: str, schema: ValidationInfo) -> str:
            value = lookup_function(key)
            return value.name if isinstance(value, Entity) else value

        @classmethod
        def __class_getitem__(cls, key) -> str:
            try:
                value = lookup_function(key)
                return value.name if isinstance(value, Entity) else value
            except PydanticCustomError:
                raise KeyError("Key Error: {key}")

    return _FuzzType
