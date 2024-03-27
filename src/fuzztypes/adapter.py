from functools import lru_cache
from itertools import chain
from typing import Any, Optional, Union, get_args

from pydantic import TypeAdapter

from fuzztypes import Entity, FuzzValidator, MatchResult, storage


@lru_cache(maxsize=None)
def get_type_adapter(cls: Any) -> TypeAdapter:
    """
    Get a type adapter for the given class wrapped by a cache.

    :param cls: TypedDict, BaseModel, or Annotation.
    :return: TypeAdapter wrapper of cls
    """
    return TypeAdapter(cls)


def get_validator(cls: Any) -> Optional[FuzzValidator]:
    """
    Finds and returns validator from class or annotation metadata.

    :param cls: class that could be a FuzzValidator or Annotated type.
    :return: FuzzValidator instance
    """
    metadata = get_args(cls)
    validator = None
    for item in chain([cls], metadata):
        if isinstance(item, FuzzValidator):
            validator = item
            break
    return validator


def get_storage(item: Any) -> Optional[storage.AbstractStorage]:
    """
    Finds and returns storage from class from FuzzValidator.

    :param item: class that could be a FuzzValidator or Annotated type.
    :return: AbstractStorage instance (InMemory or OnDisk)
    """
    storage_obj = None

    if isinstance(item, storage.AbstractStorage):
        storage_obj = item
    else:
        validator = get_validator(item)
        if validator and isinstance(validator.func, storage.AbstractStorage):
            storage_obj = validator.func

    return storage_obj


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


def resolve_entity(cls: Any, value: Any) -> Optional[Entity]:
    """
    Returns entity from metadata if cls is a FuzzValidator.

    :param cls: Any object
    :param value: input value
    :return: Entity if validator is an entity source
    """
    validator = get_validator(cls)
    return validator[value] if validator is not None else None


def find_matches(cls: Any, value: Any) -> Optional[MatchResult]:
    """
    Find matches for a value from storage type.

    :param cls: Any object
    :param value: input value
    :return: MatchResult returned by validator
    """
    storage_obj = get_storage(cls)
    assert storage_obj is not None, f"No storage found for {cls}"
    return storage_obj.match(value)
