import dataclasses
import sys
from functools import lru_cache
from itertools import chain
from typing import Any, Dict, Optional, Union, cast, get_args

from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    TypeAdapter,
    json_schema,
)
from pydantic_core import CoreSchema, PydanticCustomError, core_schema

from fuzztypes import Entity, MatchResult

dataclass_kwargs: Dict[str, Any]

slots_true: Dict[str, bool] = {}
if sys.version_info >= (3, 10):
    slots_true = {"slots": True}  # pragma: no cover


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


def resolve_entity(cls: Any, value: Any) -> Optional[Entity]:
    """
    Returns entity from metadata if cls is a FuzzValidator.

    :param cls: Any object
    :param value: input value
    :return: Entity if validator is an entity source
    """
    validator = get_validator(cls)
    return validator[value] if validator is not None else None


@dataclasses.dataclass(frozen=True, **slots_true)
class FuzzValidator:
    func: Any
    examples: Optional[list] = None

    def __hash__(self):
        attrs = (self.func, tuple(self.examples or ()))
        return hash(attrs)

    def __getitem__(self, key):
        try:
            return self.func[key]
        except PydanticCustomError as err:
            raise KeyError(f"Key Error: {key} [{err}]") from err

    def match(self, key) -> MatchResult:
        return self.func.match(key)

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


def get_validator(cls: Any) -> Optional[FuzzValidator]:
    """
    Finds and returns validator from class or annotation metadata.

    :param cls: class that could be a FuzzValidator or Annotated type.
    :return: FuzzValidator instance
    """
    metadata = get_args(cls)
    entity = None
    for item in chain([cls], metadata):
        if isinstance(item, FuzzValidator):
            entity = item
            break
    return entity


def find_matches(cls: Any, value: Any) -> Optional[MatchResult]:
    """
    Find matches for a value from a validator or annotation type.

    :param cls: Any object
    :param value: input value
    :return: MatchResult returned by validator
    """
    validator = get_validator(cls)
    return validator.match(value) if validator is not None else None
