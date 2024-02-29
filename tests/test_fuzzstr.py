from pydantic import BaseModel, ValidationError

from fuzztype import FuzzStr, NamedEntity, const

FruitStr = FuzzStr(["Apple", "Banana"])
DirectionStr = FuzzStr(
    [
        ("Left", "L"),
        ("Right", "R"),
        ("Middle", "M"),
    ]
)
LooseStr = FuzzStr(["A B C", "X Y Z"], fuzz_min_score=10.0, fuzz_limit=1)
StrictStr = FuzzStr(["A B C", "X Y Z"], fuzz_min_score=95.0, fuzz_limit=1)


class Model(BaseModel):
    fruit: FruitStr = None
    direction: DirectionStr = None
    loose: LooseStr = "A B C"
    strict: StrictStr = "A B C"


def test_exact_matches():
    obj = Model(fruit="Apple", direction="Left")
    assert obj.fruit == "Apple"
    assert obj.direction == "Left"


def test_case_insensitive():
    obj = Model(fruit="banana", direction="right")
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


def test_get_item():
    assert DirectionStr["L"].name == "Left"

    try:
        assert DirectionStr["XYZ"]
        raise AssertionError("Didn't throw KeyError")
    except KeyError:
        pass


def test_min_score():
    assert Model(loose="B K L").loose == "A B C"

    try:
        Model(strict="B K L")
        assert "Expected validation error!"

    except ValidationError as e:
        assert e.errors(include_url=False) == [
            {
                "ctx": {"key": "B K L", "near": ["A B C [40.0]"]},
                "input": "B K L",
                "loc": ("strict",),
                "msg": "key (B K L) not resolved",
                "type": "key_not_found",
            }
        ]

    alpha_tiebreaker = FuzzStr(
        ["A1", "A2", "A3"],
    )
    pass


def test_with_priority():
    entities = [
        NamedEntity(name="WP1", priority=1),
        NamedEntity(name="WP2", priority=1),
        NamedEntity(name="WP3", priority=3),
    ]

    # highest priority sorts to the front
    assert sorted(entities)[0].name == "WP3"

    # name is tiebreaker
    assert sorted(entities)[1].name == "WP1"

    # validate that priority wins
    WithPriority = FuzzStr(entities, fuzz_min_score=65.0)
    assert WithPriority["WPX"].name == "WP3"


def test_without_priority():
    entities = ["NT1", "NT2", "NT3"]
    WithoutPriority = FuzzStr(entities, fuzz_min_score=65.0)
    try:
        assert WithoutPriority["NTX"] is None
    except KeyError:
        pass

    AlphaTiebreak = FuzzStr(
        entities, fuzz_min_score=65, tiebreaker_mode="alphabetical"
    )
    assert AlphaTiebreak["NTX"].name == "NT1"
