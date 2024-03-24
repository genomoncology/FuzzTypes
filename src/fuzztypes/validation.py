"""This module contains related classes and functions for validation."""

import dataclasses
import sys
from functools import lru_cache
from typing import Any, Union, Callable, Dict, cast

from pydantic import GetCoreSchemaHandler, TypeAdapter
from pydantic_core import core_schema
from fuzztypes import const

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
    notfound_mode: const.NotFoundMode = "raise"

    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        schema = handler(source_type)
        func = cast(core_schema.NoInfoValidatorFunction, self.func)

        return core_schema.no_info_before_validator_function(
            func, schema=schema
        )
