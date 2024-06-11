from typing import Literal, Annotated
from fuzztypes import LiteralValidator, validate_python

FruitLiteral = Literal["apple", "banana", "cherry"]
Fruit = Annotated[str, LiteralValidator(FruitLiteral)]
FruitLiteral = Annotated[FruitLiteral, LiteralValidator(FruitLiteral)]


def test_literal_validator():
    assert validate_python(Fruit, "apple") == "apple"
    assert validate_python(FruitLiteral, "apple") == "apple"

    try:
        assert validate_python(Fruit, "fig")
        assert False, "Didn't fail to parse non-literal."
    except ValueError:
        pass
