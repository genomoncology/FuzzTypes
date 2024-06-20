from typing import Annotated, Literal

from pydantic import ValidationError

from fuzztypes import EnumValidator, StrEnum, validate_python


class FruitEnum(StrEnum):
    APPLE = "apple"
    BANANA = "banana"
    CHERRY = "cherry"
    DATE = "date"
    FIG = "fig"
    GRAPE = "grape"
    KIWI = "kiwi"
    LEMON = "lemon"
    LIME = "lime"
    ORANGE = "orange"
    PEAR = "pear"
    PINEAPPLE = "pineapple"
    PLUM = "plum"
    STRAWBERRY = "strawberry"
    WATERMELON = "watermelon"


def test_enum_as_enum_output():
    Fruit = Annotated[FruitEnum, EnumValidator(FruitEnum)]

    assert validate_python(Fruit, "fig") == FruitEnum.FIG
    assert validate_python(Fruit, "FIG") == FruitEnum.FIG
    assert validate_python(Fruit, "graph") == FruitEnum.GRAPE

    try:
        assert validate_python(Fruit, "fog") == FruitEnum.FIG
        assert False, "Didn't fail with a lower similarity."
    except ValueError:
        pass


def test_enum_as_str_output():
    FruitStr = Annotated[str, EnumValidator(FruitEnum)]
    assert validate_python(FruitStr, "fig") == "fig"
    assert validate_python(FruitStr, "FIG") == "fig"


def test_literal_validator():
    FruitLiteral = Literal["apple", "banana", "cherry"]
    Fruit = Annotated[FruitLiteral, EnumValidator(FruitLiteral)]

    assert validate_python(Fruit, "apple") == "apple"
    assert validate_python(Fruit, "APPLE") == "apple"

    try:
        validate_python(Fruit, "fig")
    except ValidationError as e:
        assert "Input should be 'apple', 'banana' or 'cherry'" in str(e)
