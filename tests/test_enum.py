from typing import Annotated
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


Fruit = Annotated[FruitEnum, EnumValidator(FruitEnum)]
FruitStr = Annotated[str, EnumValidator(FruitEnum)]


def test_exact_match_name_or_value():
    assert validate_python(Fruit, "fig") == FruitEnum.FIG
    assert validate_python(Fruit, "FIG") == FruitEnum.FIG

    assert validate_python(FruitStr, "fig") == "fig"
    assert validate_python(FruitStr, "FIG") == "fig"


def test_fuzzy_match():
    assert validate_python(Fruit, "graph") == FruitEnum.GRAPE

    try:
        assert validate_python(Fruit, "fog") == FruitEnum.FIG
        assert False, "Didn't fail with a lower similarity."
    except ValueError:
        pass
