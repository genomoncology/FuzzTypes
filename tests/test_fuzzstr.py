from pydantic import BaseModel, ValidationError

from fuzztype import FuzzStr, Entity

FruitStr = FuzzStr(["Apple", "Banana"])
DirectionStr = FuzzStr(
    [
        ("Left", "L"),
        ("Right", "R"),
        ("Middle", "M"),
    ]
)
LooseStr = FuzzStr(["A B C", "X Y Z"], min_score=10.0, num_nearest=1)
StrictStr = FuzzStr(["A B C", "X Y Z"], min_score=95.0, num_nearest=1)


class Model(BaseModel):
    fruit: FruitStr = None
    direction: DirectionStr = None
    loose: LooseStr = "A B C"
    strict: StrictStr = "A B C"


def test_exact_matches():
    obj = Model(fruit="Apple", title="Hello World", direction="Left")
    assert obj.fruit == "Apple"
    assert obj.direction == "Left"


def test_case_insensitive():
    obj = Model(fruit="banana", title="hello world", direction="right")
    assert obj.fruit == "Banana"
    assert obj.direction == "Right"


def test_case_fuzzy():
    obj = Model(fruit="appel", direction="lft.")
    assert obj.fruit == "Apple"
    assert obj.direction == "Left"


def test_synonyms():
    assert Model(direction="L").direction == "Left"
    assert Model(direction="r").direction == "Right"
    assert Model(direction="M.").direction == "Middle"


def test_min_score():
    assert Model(loose="B K L").loose == "A B C"

    try:
        Model(strict="B K L")
        assert "Expected validation error!"

    except ValidationError as e:
        assert e.errors(include_url=False) == [
            {
                "ctx": {"key": "B K L", "nearest": "A B C [40.0]"},
                "input": "B K L",
                "loc": ("strict",),
                "msg": "key (B K L) not resolved (nearest: A B C [40.0])",
                "type": "fuzz_str_not_resolved",
            }
        ]
