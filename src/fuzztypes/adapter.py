from functools import lru_cache
from itertools import chain
from typing import Any, Optional, Union, get_args

from pydantic import TypeAdapter

from fuzztypes import FuzzValidator


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
    ta = get_type_adapter(cls)
    return ta.validate_python(value)
