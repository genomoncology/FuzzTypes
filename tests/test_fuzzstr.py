from pydantic import BaseModel

from fuzztype import FuzzStr, Entity

FruitStr = FuzzStr(["Apple", "Banana"])
TitleStr = FuzzStr(str.title)
DirectionStr = FuzzStr(
    [
        ("Left", "L"),
        ("Right", "R"),
        ("Middle", "M"),
    ]
)


class Model(BaseModel):
    fruit: FruitStr = None
    title: TitleStr = None
    direction: DirectionStr = None


def test_exact_matches():
    obj = Model(fruit="Apple", title="Hello World", direction="Left")
    assert obj.fruit == "Apple"
    assert obj.title == "Hello World"
    assert obj.direction == "Left"


def test_case_insensitive():
    obj = Model(fruit="banana", title="hello world", direction="right")
    assert obj.fruit == "Banana"
    assert obj.title == "Hello World"
    assert obj.direction == "Right"


def test_case_fuzzy():
    obj = Model(fruit="appel", direction="lft.")
    assert obj.fruit == "Apple"
    assert obj.direction == "Left"


def test_synonyms():
    assert Model(direction="L").direction == "Left"
    assert Model(direction="r").direction == "Right"
    assert Model(direction="M.").direction == "Middle"
