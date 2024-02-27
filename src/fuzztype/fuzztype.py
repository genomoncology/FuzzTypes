from typing import Callable, Type, Union, Optional

from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationInfo,
    json_schema,
)
from pydantic_core import CoreSchema, core_schema, PydanticCustomError

from . import Entity, LookupReturn, const

SupportedType = Union[str, float, int, dict, list]


def FuzzType(
    lookup_function: Callable[[str], LookupReturn],
    *,
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    python_type: Type[SupportedType] = str,
    validator_mode: const.ValidatorMode = "before",
):
    """
    Factory function to create a specialized FuzzType, which is a Pydantic
    based type with added fuzzy matching capabilities.

    :param lookup_function: Function to perform the lookup.
    :param examples: Example values used in schema generation.
    :param notfound_mode: 'raise' an error, set 'none', or 'allow' unknown key.
    :param python_type: The underlying Python data type.
    :param validator_mode: Validation mode ('before', 'after', 'plain', 'wrap')
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
            py_schema = handler(python_type)
            if notfound_mode == "none":
                py_schema = core_schema.nullable_schema(py_schema)

            return validation_function(cls._validate, py_schema)

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
        def _do_lookup(key: str) -> Optional[Entity]:
            response = lookup_function(key)

            if isinstance(response, Entity):
                return response

            if notfound_mode == "allow":
                return Entity(name=key)

            if notfound_mode == "none":
                return

            msg = "key ({key}) not resolved"
            ctx = dict(key=key)
            if response is not None:
                nearest = ", ".join(map(str, response))
                msg = f"{msg} (nearest: {nearest})"
                ctx["nearest"] = nearest

            raise PydanticCustomError("key_not_found", msg, ctx)

        @classmethod
        def _validate(cls, key: str, _: ValidationInfo = None) -> Optional[str]:
            entity = cls._do_lookup(key)
            if entity:
                return entity.name

        @classmethod
        def __class_getitem__(cls, key) -> Optional[Entity]:
            try:
                return cls._do_lookup(key)
            except PydanticCustomError:
                raise KeyError("Key Error: {key}")

    return _FuzzType
