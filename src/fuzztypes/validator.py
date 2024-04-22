import dataclasses
import sys
from typing import Any, Dict, Optional, cast

from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    json_schema,
)
from pydantic_core import CoreSchema, PydanticCustomError, core_schema

dataclass_kwargs: Dict[str, Any]

slots_true: Dict[str, bool] = {}
if sys.version_info >= (3, 10):
    slots_true = {"slots": True}  # pragma: no cover


@dataclasses.dataclass(frozen=True, **slots_true)
class FuzzValidator:
    func: Any
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
