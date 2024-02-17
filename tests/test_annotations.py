# Experiment to learn what was possible with Python Annotations and Pydantic.

from pydantic import (
    BaseModel,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue

from pydantic_core.core_schema import (
    CoreSchema,
    with_info_before_validator_function,
    str_schema,
)


def CustomStr(modifier: str):
    """
    Factory function that returns a custom string class based on the modifier.
    """

    class ModifierStr(str):
        """
        A custom string type that modifies input strings based on a modifier.
        """

        @classmethod
        def __get_pydantic_core_schema__(cls, *_) -> CoreSchema:
            return with_info_before_validator_function(
                cls._validate, str_schema()
            )

        @classmethod
        def _validate(cls, value, schema):
            if not isinstance(value, str):
                raise TypeError("string required")
            if modifier == "UPPER":
                return cls(value.upper())
            elif modifier == "LOWER":
                return cls(value.lower())
            else:
                raise ValueError(f"Unsupported modifier: {modifier}")

        @classmethod
        def __get_pydantic_json_schema__(
            cls,
            core_schema: CoreSchema,
            handler: GetJsonSchemaHandler,
        ) -> JsonSchemaValue:
            json_schema = handler(core_schema)
            json_schema = handler.resolve_ref_schema(json_schema)
            json_schema["examples"] = ["a", "B"]
            return json_schema

    return ModifierStr


# Example usage
class MyClass(BaseModel):
    my_upper: CustomStr("UPPER")
    my_lower: CustomStr("LOWER")


# Tests
def test_custom_str():
    instance = MyClass(my_upper="hello world", my_lower="HELLO WORLD")
    assert instance.my_upper == "HELLO WORLD", instance.my_upper
    assert instance.my_lower == "hello world", instance.my_lower


def test_json_schema():
    assert MyClass.model_json_schema() == {
        "properties": {
            "my_lower": {
                "examples": ["a", "B"],
                "title": "My Lower",
                "type": "string",
            },
            "my_upper": {
                "examples": ["a", "B"],
                "title": "My Upper",
                "type": "string",
            },
        },
        "required": ["my_upper", "my_lower"],
        "title": "MyClass",
        "type": "object",
    }
