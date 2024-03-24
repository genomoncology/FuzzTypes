from pydantic import BaseModel, ValidationError

from fuzztypes import Integer, utils


def test_convert_number_to_int():
    assert utils.validate_python(Integer, 3) == 3
    assert utils.validate_python(Integer, "three") == 3
    assert utils.validate_python(Integer, "third") == 3
    assert (
        utils.validate_python(Integer, "nineteen billion and nineteen")
        == 19_000_000_019
    )
    assert (
        utils.validate_python(
            Integer, "two million three thousand and nineteen"
        )
        == 2_003_019
    )


def test_validation_error():
    class MyModel(BaseModel):
        num: Integer

    assert MyModel(num="three").num == 3  # type: ignore[arg-type]

    try:
        assert MyModel(num="xyz")  # type: ignore[arg-type]
        assert False, "Didn't fail to parse non-integer."
    except ValidationError:
        pass
