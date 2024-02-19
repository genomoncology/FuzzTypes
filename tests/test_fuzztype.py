from typing import Optional
from pydantic import BaseModel, Field
from fuzztype import FuzzType


# Example usage
class MyClass(BaseModel):
    my_upper: FuzzType(str.upper, examples=["A", "B", "C"])
    my_lower: Optional[FuzzType(str.lower, examples=["a", "b", "c"])] = Field(
        None
    )


def test_upper_and_lower():
    instance = MyClass(
        my_upper="hello world",
        my_lower="HELLO WORLD",
    )
    assert instance.my_upper == "HELLO WORLD", instance.my_upper
    assert instance.my_lower == "hello world", instance.my_lower


def test_json_schema():
    assert MyClass.model_json_schema() == {
        "properties": {
            "my_lower": {
                "anyOf": [
                    {"examples": ["a", "b", "c"], "type": "string"},
                    {"type": "null"},
                ],
                "default": None,
                "title": "My Lower",
            },
            "my_upper": {
                "examples": ["A", "B", "C"],
                "title": "My Upper",
                "type": "string",
            },
        },
        "required": ["my_upper"],
        "title": "MyClass",
        "type": "object",
    }
