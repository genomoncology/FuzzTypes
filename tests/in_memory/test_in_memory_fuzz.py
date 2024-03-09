from pydantic import BaseModel, ValidationError

from fuzztypes import NamedEntity, InMemory, flags

FruitStr = InMemory(
    ["Apple", "Banana"],
    search_flag=flags.FuzzSearch,
)
DirectionStr = InMemory(
    [
        ("Left", "L"),
        ("Right", "R"),
        ("Middle", "M"),
    ],
    search_flag=flags.FuzzSearch,
)
LooseStr = InMemory(
    ["A B C", "X Y Z"],
    min_similarity=10.0,
    limit=1,
    search_flag=flags.FuzzSearch,
)
StrictStr = InMemory(
    ["A B C", "X Y Z"],
    min_similarity=95.0,
    limit=1,
    search_flag=flags.FuzzSearch,
)


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
                "msg": "key (B K L) could not be resolved, potential matches "
                "= A B C [40.0]",
                "type": "key_not_found",
            }
        ]


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
    WithPriority = InMemory(
        entities,
        min_similarity=65.0,
        search_flag=flags.FuzzSearch,
    )
    assert WithPriority["WPX"].value == "WP3"


def test_without_tiebreaker():
    entities = ["NT1", "NT2", "NT3"]
    WithoutPriority = InMemory(
        entities,
        min_similarity=65.0,
        search_flag=flags.FuzzSearch,
    )
    try:
        assert WithoutPriority["NTX"] is None
    except KeyError:
        pass


def test_with_lesser_tiebreaker():
    entities = ["NT1", "NT2", "NT3"]
    LesserTiebreak = InMemory(
        entities,
        min_similarity=65,
        tiebreaker_mode="lesser",
        search_flag=flags.FuzzSearch,
    )
    assert LesserTiebreak["NTX"].value == "NT1"


def test_with_greater_tiebreaker():
    entities = ["NT1", "NT2", "NT3", "XX5"]
    GreaterTiebreak = InMemory(
        entities,
        min_similarity=0,
        tiebreaker_mode="greater",
        search_flag=flags.FuzzSearch,
    )
    assert GreaterTiebreak["NTX"].value == "NT3"
