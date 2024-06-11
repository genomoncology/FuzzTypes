from typing import Annotated
from enum import Enum
from fuzztypes import EnumValidator, validate_python


class FruitEnum(str, Enum):
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


def test_exact_match_name_or_value():
    Fruit = Annotated[FruitEnum, EnumValidator(FruitEnum)]
    assert validate_python(Fruit, "fig") == FruitEnum.FIG
    assert validate_python(Fruit, "FIG") == FruitEnum.FIG

    FruitStr = Annotated[str, EnumValidator(FruitEnum)]
    assert validate_python(FruitStr, "fig") == "fig"
    assert validate_python(FruitStr, "FIG") == "fig"


# todo: fuzzy logic using rapidfuzz and minimum similarity scores!
