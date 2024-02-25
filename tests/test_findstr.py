from typing import Optional

from pydantic import BaseModel, Field

from fuzztype import FindStr

UpperType = FindStr(str.upper, examples=["A", "B", "C"])


# Example usage
class MyClass(BaseModel):
    my_upper: UpperType
    my_lower: Optional[FindStr(str.lower, examples=["a", "b", "c"])] = Field(
        None
    )


def test_simple_transforms():
    obj = MyClass(my_upper="Abc", my_lower="ABc")
    assert obj.my_upper == "ABC"
    assert obj.my_lower == "abc"


def test_getitem_upper():
    assert UpperType["hello"] == "HELLO"


def test_class_getitem():
    StripType = FindStr(str.strip)
    assert StripType[" a b c "] == "a b c"


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
