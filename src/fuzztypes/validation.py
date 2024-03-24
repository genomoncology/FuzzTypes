import dataclasses
import sys
from functools import lru_cache
from typing import Any, Union, Callable, Dict, cast, Optional

from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    TypeAdapter,
    json_schema,
)
from pydantic_core import CoreSchema, core_schema

dataclass_kwargs: Dict[str, Any]

slots_true: Dict[str, bool] = {}
if sys.version_info >= (3, 10):
    slots_true = {"slots": True}


@lru_cache(maxsize=None)
def get_type_adapter(cls: Any) -> TypeAdapter:
    """
    Get a type adapter for the given class wrapped by a cache.

    :param cls: TypedDict, BaseModel, or Annotation.
    :return: TypeAdapter wrapper of cls
    """
    return TypeAdapter(cls)


def validate_json(cls: Any, value: Union[str, bytes]) -> Any:
    """
    Validate a JSON string or bytes against the model.

    :param cls: TypedDict, BaseModel, or Annotation.
    :param value: JSON string or bytes to validate.
    :return: Validated Python object.
    """
    return get_type_adapter(cls).validate_json(value)


def validate_python(cls: Any, value: Any) -> Any:
    """
    Validate a Python object against the model.

    :param cls: TypedDict, BaseModel, or Annotation.
    :param value: Python object to validate.
    :return: Validated Python object.
    """
    return get_type_adapter(cls).validate_python(value)


@dataclasses.dataclass(frozen=True, **slots_true)
class FuzzValidator:
    func: Callable[[Any], Any]
    examples: Optional[list] = None

    def __hash__(self):
        attrs = (self.func, tuple(self.examples or ()))
        return hash(attrs)

    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        schema = handler(source_type)
        func = cast(core_schema.NoInfoValidatorFunction, self.func)

        return core_schema.no_info_before_validator_function(
            func, schema=schema
        )

    def __get_pydantic_json_schema__(
        self,
        schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> json_schema.JsonSchemaValue:
        """
        Generate the JSON schema for the AbstractType.

        This method is used internally by Pydantic to generate the JSON
        schema representation of the AbstractType, including any examples.
        """
        schema = handler(schema)
        if self.examples is not None:
            schema["examples"] = self.examples
        return schema
