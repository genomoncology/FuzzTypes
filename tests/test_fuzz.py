from pydantic import BaseModel, ValidationError

from fuzztypes import Fuzz, NamedEntity, const

FruitStr = Fuzz(["Apple", "Banana"])
DirectionStr = Fuzz(
    [
        ("Left", "L"),
        ("Right", "R"),
        ("Middle", "M"),
    ]
)
LooseStr = Fuzz(["A B C", "X Y Z"], fuzz_min_score=10.0, fuzz_limit=1)
StrictStr = Fuzz(["A B C", "X Y Z"], fuzz_min_score=95.0, fuzz_limit=1)


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
    assert DirectionStr["L"].value == "Left"

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

    alpha_tiebreaker = Fuzz(
        ["A1", "A2", "A3"],
    )
    pass


def test_with_priority():
    entities = [
        NamedEntity(value="WP1", priority=1),
        NamedEntity(value="WP2", priority=1),
        NamedEntity(value="WP3", priority=3),
    ]

    # highest priority sorts to the front
    assert sorted(entities)[0].value == "WP3"

    # value is tiebreaker
    assert sorted(entities)[1].value == "WP1"

    # validate that priority wins
    WithPriority = Fuzz(entities, fuzz_min_score=65.0)
    assert WithPriority["WPX"].value == "WP3"


def test_without_priority():
    entities = ["NT1", "NT2", "NT3"]
    WithoutPriority = Fuzz(entities, fuzz_min_score=65.0)
    try:
        assert WithoutPriority["NTX"] is None
    except KeyError:
        pass

    LesserTiebreak = Fuzz(
        entities, fuzz_min_score=65, tiebreaker_mode="lesser"
    )
    assert LesserTiebreak["NTX"].value == "NT1"

    GreaterTiebreak = Fuzz(
        entities, fuzz_min_score=65, tiebreaker_mode="greater"
    )
    assert GreaterTiebreak["NTX"].value == "NT3"
