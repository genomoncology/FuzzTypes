import string
from typing import Literal

from pydantic import PositiveInt, ValidationError, BaseModel

from fuzztype import FuzzStr


class FuzzClass(BaseModel):
    my_fuzz_str: FuzzStr(string.ascii_letters) = "a"


def test_fuzzstr():
    obj = FuzzClass(my_fuzz_str="b")
    assert obj.model_dump(exclude_defaults=True) == {"my_fuzz_str": "b"}

    try:
        FuzzClass(my_fuzz_str="5")
        assert False, "Didn't fail!"

    except ValidationError as e:
        errors = e.errors(include_url=False)
        assert errors == [
            {
                "ctx": {"key": "5", "nearest": "a [0.0], b [0.0], c [0.0]"},
                "input": "5",
                "loc": ("my_fuzz_str",),
                "msg": "key (5) not resolved (nearest: a [0.0], b [0.0], "
                "c [0.0])",
                "type": "fuzz_str_not_resolved",
            }
        ]


class NonFuzzClass(BaseModel):
    my_pos_int: PositiveInt = 1
    my_literal: Literal["x", "y", "z"] = "z"


def test_standard_examples():
    obj = NonFuzzClass(my_pos_int=5, my_literal="y")
    assert obj.model_dump(exclude_defaults=True) == {
        "my_pos_int": 5,
        "my_literal": "y",
    }

    try:
        NonFuzzClass(my_pos_int=-5, my_literal="m")
        assert False, "Didn't fail!"
    except ValidationError as e:
        errors = e.errors(include_url=False)
        assert errors == [
            {
                "ctx": {"gt": 0},
                "input": -5,
                "loc": ("my_pos_int",),
                "msg": "Input should be greater than 0",
                "type": "greater_than",
            },
            {
                "ctx": {"expected": "'x', 'y' or 'z'"},
                "input": "m",
                "loc": ("my_literal",),
                "msg": "Input should be 'x', 'y' or 'z'",
                "type": "literal_error",
            },
        ]
