from typing import Callable, Literal, Type, Union

from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationInfo,
    json_schema,
)
from pydantic_core import CoreSchema, core_schema

SupportedType = Union[str, float, int, dict, list]


def FuzzType(
    lookup_function: Callable,
    python_type: Type[SupportedType] = str,
    pydantic_schema: Callable = None,
    validator_mode: Literal["before", "after", "plain", "wrap"] = "before",
    examples: list = None,
):
    """
    Factory function to create a specialized FuzzType, which is a Pydantic
    based type with added fuzzy matching capabilities.

    :param lookup_function: Function to perform the lookup.
    :param python_type: The underlying Python data type.
    :param pydantic_schema: Pydantic schema function if differs from default.
    :param validator_mode: Validation mode ('before', 'after', 'plain', 'wrap')
    :param examples: Examples of possible values, used in schema generation.
    :return: A specialized FuzzType based on the provided specifications.
    """

    # noinspection PyClassHasNoInit
    class _FuzzType(python_type):
        @classmethod
        def get_pydantic_schema(cls):
            nonlocal pydantic_schema

            if pydantic_schema is None:
                f = {
                    str: core_schema.str_schema,
                    float: core_schema.float_schema,
                    int: core_schema.int_schema,
                    dict: core_schema.dict_schema,
                    list: core_schema.list_schema,
                    Literal: core_schema.literal_schema,
                }.get(python_type)
                assert f, f"No pydantic schema defined for {python_type}"
                pydantic_schema = f

            return pydantic_schema()

        # noinspection PyUnusedLocal
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

            py_schema = cls.get_pydantic_schema()
            validation_function = validation_function_map[validator_mode]
            return validation_function(cls._validate, py_schema)

        @classmethod
        def __get_pydantic_json_schema__(
            cls,
            core_schema: CoreSchema,
            handler: GetJsonSchemaHandler,
        ) -> json_schema.JsonSchemaValue:
            json_schema = handler(core_schema)
            json_schema = handler.resolve_ref_schema(json_schema)
            if examples is not None:
                json_schema["examples"] = examples
            return json_schema

        @staticmethod
        def _validate(key: str, schema: ValidationInfo) -> str:
            return lookup_function(key)

        @classmethod
        def __class_getitem__(cls, key):
            return lookup_function(key)

        @classmethod
        def lookup_function(cls):
            return lookup_function

    return _FuzzType
