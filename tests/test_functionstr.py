from typing import Optional

from pydantic import BaseModel, Field

from fuzztype import FunctionStr

UpperType = FunctionStr(str.upper, examples=["A", "B", "C"])
LowerType = FunctionStr(str.lower, examples=["a", "b", "c"])


# Example usage
class MyClass(BaseModel):
    my_upper: UpperType
    my_lower: Optional[LowerType] = Field(None)


def test_simple_transforms():
    obj = MyClass(my_upper="Abc", my_lower="ABc")
    assert obj.my_upper == "ABC"
    assert obj.my_lower == "abc"


def test_getitem_upper():
    assert UpperType["hello"].name == "HELLO"


def test_class_getitem():
    StripType = FunctionStr(str.strip)
    assert StripType[" a b c "].name == "a b c"


def test_missing_lookup():
    def apple_banana(key: str) -> str:
        return dict(a="apple", b="banana").get(key)

    AppleBanana = FunctionStr(apple_banana)
    assert AppleBanana["a"].name == "apple"
    assert AppleBanana["a"].value == "apple"
    assert AppleBanana.get_value("a") == "apple"

    try:
        assert AppleBanana["c"] is not None
        assert False, "Didn't throw exception."
    except KeyError:
        pass

    NoAppleBananaOk = FunctionStr(apple_banana, notfound_mode="none")
    assert NoAppleBananaOk["d"] is None

    AnyFruitOk = FunctionStr(apple_banana, notfound_mode="allow")
    assert AnyFruitOk.get_value("kiwi") == "kiwi"


def test_json_schema():
    assert MyClass.model_json_schema() == {
        "properties": {
            "my_lower": {
                "anyOf": [
                    {
                        "examples": ["a", "b", "c"],
                        "type": "string",
                    },
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
