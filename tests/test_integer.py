from pydantic import BaseModel, ValidationError

from fuzztypes import Integer


class MyModel(BaseModel):
    num: Integer


def test_convert_number_to_int():
    assert MyModel(num=3).num == 3
    assert MyModel(num="three").num == 3
    assert MyModel(num="third").num == 3
    assert MyModel(num="nineteen billion and nineteen").num == 19_000_000_019
    assert (
        MyModel(num="two million three thousand and nineteen").num == 2_003_019
    )


def test_validation_error():
    try:
        assert MyModel(num="xyz")
        assert False, "Didn't fail to parse non-integer."
    except ValidationError:
        pass


def test_json_schema():
    assert MyModel.model_json_schema() == {
        "properties": {"num": {"title": "Num", "type": "integer"}},
        "required": ["num"],
        "title": "MyModel",
        "type": "object",
    }
